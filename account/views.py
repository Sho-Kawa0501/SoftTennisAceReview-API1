from rest_framework import response
from django.contrib.auth import get_user_model
from rest_framework import permissions,status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from account import serializers
from django.conf import settings
import jwt
import logging
from rest_framework.exceptions import ValidationError,APIException,NotFound,PermissionDenied
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework.exceptions import NotAuthenticated
from rest_framework_simplejwt import views as jwt_views,exceptions as jwt_exp
from reviewsite.authentication import CookieHandlerJWTAuthentication
from PIL import Image
import io
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.parsers import MultiPartParser, FormParser
from reviewsite.utils.image_utils import resize_image,delete_image_from_s3
from django.db import transaction
from review.models import UserReview

logger = logging.getLogger(__name__)
User = get_user_model()


class RegisterView(APIView):
  permission_classes = (permissions.AllowAny, )
  authentication_classes = ()

  def post(self, request):
    data = request.data
    email = data.get('email', '').lower()
    password = data.get('password', '')

    if not email or not password:
      # ValidationErrorを使用してカスタムエラーメッセージを設定
      raise ValidationError('メールアドレスとパスワードは必須です。')

    if User.objects.filter(email=email).exists():
      # 既に存在するメールアドレスである場合
      raise ValidationError('既に登録されているメールアドレスです。')

    try:
      User.objects.create_user(email=email, password=password)
      return Response(status=status.HTTP_201_CREATED)
    except Exception as e:
      # その他のエラーが発生した場合
      raise APIException('アカウント登録時に問題が発生しました。')
      
#ログイン
class MyTokenObtainPairView(jwt_views.TokenObtainPairView):
  serializer_class = serializers.MyTokenObtainPairSerializer
  permission_classes = (permissions.AllowAny, )
  authentication_classes = ()

  def post(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    res = Response(serializer.validated_data, status=status.HTTP_200_OK)

    try:
      res.delete_cookie("access_token")
      res.set_cookie(
        "access_token",
        serializer.validated_data["access"],
        max_age=60 * 60 * 24,
        secure=True,
        httponly=True,
        samesite='None',
      )
      res.set_cookie(
        "refresh_token",
        serializer.validated_data["refresh"],
        max_age=60 * 60 * 24 * 30,
        secure=True,
        httponly=True,
        samesite='None',
      )
    except Exception as e:
      raise e.APIException("Failed to set access_token cookies.")
    return res


# access_tokenを使ってログインユーザーの情報を取得し、返り値に設定
#トークンが存在する前提で使用する関数
#クッキーからアクセストークンを取得→
#decodeで与えられたトークンが有効で、署名が正しいことを確認(settings.SECRETKEYを使用)→

class CheckAuthView(APIView):
  serializer_class = serializers.UserSerializer
  authentication_classes = (CookieHandlerJWTAuthentication,)

  def get(self, request, *args, **kwargs):
    jwt_token = request.COOKIES.get("access_token")
    if not jwt_token:
      return Response({"isAccessAuthenticated": False, "reason": "missing_token"}, status=status.HTTP_200_OK)

    try:
      payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=["HS256"])
      user = User.objects.get(id=payload["user_id"])
      if user.is_active:
        res = serializers.UserSerializer(user)
        return Response(res.data, status=status.HTTP_200_OK)
      else:
        return Response({"isAccessAuthenticated": False, "reason": "user_inactive"}, status=status.HTTP_200_OK)
    except jwt.ExpiredSignatureError:
      return Response({"isAccessAuthenticated": False, "reason": "token_expired"}, status=status.HTTP_200_OK)
    except jwt.exceptions.DecodeError:
      return Response({"isAccessAuthenticated": False, "reason": "invalid_token"}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
      return Response({"isAccessAuthenticated": False, "reason": "user_not_found"}, status=status.HTTP_200_OK)

# coookieからリフレッシュトークンを取得
class GetRefreshTokenView(APIView):
  authentication_classes = (CookieHandlerJWTAuthentication,)

  def get(self, request, *args, **kwargs):
    try:
      RT = request.COOKIES.get('refresh_token')
      if RT is None:
        raise NotFound("Cookie 'refresh_token' was not found.")
      return Response({'refresh': RT})
    except Exception as e:
      raise APIException("An error occurred: {}".format(e))

#TokenRefreshViewを拡張
# リフレッシュトークンを使って、新しいアクセストークンを生成する
class CreateAccessTokenView(jwt_views.TokenRefreshView):
  def post(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    try:
      serializer.is_valid(raise_exception=True)
    except ValidationError:
      raise InvalidToken("Invalid or expired token.")

    try:
      serializer.validated_data
    except jwt_exp.TokenError as e:
      raise InvalidToken(str(e.args[0]))

    try:
      serializer.validated_data
    except jwt_exp.TokenError as e:
      return Response({"detail": str(e.args[0])}, status=status.HTTP_401_UNAUTHORIZED)

    # アクセストークンを更新する処理
    res = Response(serializer.validated_data, status=status.HTTP_200_OK)
    try:
      res.delete_cookie("access_token")
      res.set_cookie(
        "access_token",
        serializer.validated_data["access"],
        max_age=60 * 24 * 24 * 30,
        secure=True,
        httponly=True,
        samesite='None',
      )
    except Exception as e:
      raise e.APIException("Failed to set access_token cookies.")
    return res


class UserViewSet(ModelViewSet):
  queryset = User.objects.all()
  serializer_class = serializers.UserSerializer
  authentication_classes = (CookieHandlerJWTAuthentication,)

  def perform_update(self, serializer):
    login_user = serializer.instance

    if 'image' in serializer.validated_data:
      old_image = login_user.image
      if old_image:
        image_path = 'static/' + old_image.name
        delete_image_from_s3(image_path)

    if self.request.FILES.get('image'):
      uploaded_file = self.request.FILES.get('image')
      with Image.open(self.request.FILES.get('image')) as img:
        resized_image = resize_image(img)
      image_io = io.BytesIO()
      resized_image.save(image_io, format='JPEG', quality=85)
      image_io.seek(0)
      image_file = InMemoryUploadedFile(
        image_io,
        None,
        uploaded_file.name,
        'image/jpeg',
        image_io.getbuffer().nbytes, None
      )
      serializer.validated_data['image'] = image_file
      serializer.save()


class LogoutView(APIView):
  authentication_classes = (CookieHandlerJWTAuthentication,)

  def post(self, request, *args, **kwargs):
    res = Response({"message": "Logout"}, status=status.HTTP_200_OK)
    res.delete_cookie("access_token")
    res.delete_cookie("refresh_token")
    return res


class DeleteUserView(APIView):
  authentication_classes = (CookieHandlerJWTAuthentication,)

  def delete(self, request):
    user = request.user
    if user is None:
      raise NotAuthenticated("ユーザーが認証されていません。")

    try:
      with transaction.atomic():
        if user.image and not user.image.name.endswith('default/default.png'):
          delete_image_from_s3('static/' + user.image.name)

        user_reviews = UserReview.objects.filter(user=user)
        for user_review in user_reviews:
          if user_review.review.image:
            if user_review.review.image and not user_review.review.image.name.endswith('default/default.png'):
              delete_image_from_s3('static/' + user_review.review.image.name)
        user.delete()
      return Response(status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
      raise APIException(f"ユーザーの削除に問題が発生しました。エラーメッセージ: {str(e)}")


  # def delete(self, request):
  #   user = request.user
  #   if user is None:
  #     raise NotAuthenticated("ユーザーが認証されていません。")
  #   try:
  #     user.delete()
  #     return Response(
  #       status=status.HTTP_204_NO_CONTENT,
  #     )
  #   except Exception as e:
  #     raise APIException("ユーザーの削除に問題が発生しました。エラーメッセージ: {}".format(str(e)))


# class CheckAuthView(APIView):
#   serializer_class = serializers.UserSerializer
#   authentication_classes = (CookieHandlerJWTAuthentication,)

#   def get(self, request, *args, **kwargs):
#     jwt_token = request.COOKIES.get("access_token")
#     if not jwt_token:
#       return Response(
#         {"error": "No Token"}, status=status.HTTP_400_BAD_REQUEST
#       )
#     # Token検証
#     try:
#       payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=["HS256"])
#       loginUser = User.objects.get(id=payload["user_id"])
#       if loginUser.is_active:
#         res = serializers.UserSerializer(self.request.user)
#         return Response(res.data, status=status.HTTP_200_OK)
#       else:
#         return Response(
#           {"error": "User is not active"}, status=status.HTTP_400_BAD_REQUEST
#         )
#     # エラーキャッチ    
#     # Token期限切れ
#     except jwt.ExpiredSignatureError:
#       return Response(
#         {"error": "Activations link expired"}, status=status.HTTP_401_UNAUTHORIZED
#       )
#     # 不正なToken
#     except jwt.exceptions.DecodeError:
#       return Response(
#         {"error": "Invalid Token"}, status=status.HTTP_401_UNAUTHORIZED
#       )
#     # ユーザーが存在しない
#     except User.DoesNotExist:
#       return Response(
#         {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
#       )
