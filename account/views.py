from django.shortcuts import render
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
from rest_framework_simplejwt.views import TokenObtainPairView
from django.http import HttpResponseBadRequest
from django.http import JsonResponse
from django.contrib.auth import logout
from rest_framework_simplejwt.views import TokenRefreshView


logger = logging.getLogger(__name__)
User = get_user_model()


class RegisterView(APIView):
  #ログインしていなくても使用可能
  permission_classes = (permissions.AllowAny, )
  authentication_classes = ()

  def post(self, request):
    try:
      data = request.data
      email = data['email'].lower()
      password = data['password']

      if not email or not password:
        return Response(
        {'error': 'メールアドレスとパスワードは必須です。'},
        status=status.HTTP_400_BAD_REQUEST
      )
      #ユーザーが既に登録されているか確認する
      if not User.objects.filter(email=email).exists():
        User.objects.create_user(email=email,password=password)
        return Response(
          status=status.HTTP_201_CREATED
        )
      else:
        raise ValidationError('既に登録されているメールアドレスです。')
    except ValidationError as e:
      raise e
    except Exception as e:
      raise APIException('アカウント登録時に問題が発生しました。')
      
# 済み
# ログインVeiw
# jwt_expはexceptions
class MyTokenObtainPairView(jwt_views.TokenObtainPairView):
  #カスタムのMyTokenObtainPairSerializerが使用されている
  serializer_class = serializers.MyTokenObtainPairSerializer

  #httpのpostメソッドが呼ばれた時に実行する
  def post(self, request, *args, **kwargs):
    # シリアライザーに値を格納、バリデーションチェック
    #self.get_serializer()はDjangoRestFrameworkのGeneric viewsのメソッド。
    #定義されたserializers_classを返すため、ここではserializers.MyTokenObtainPairSerializer(Credential)という形になる
    serializer = self.get_serializer(data=request.data)
    
      # TokenErrorをキャッチ
      #serializerに格納されたCredentialの情報が正しければOK
    serializer.is_valid(raise_exception=True)
   
      # ExceptionはPythonのすべてのビルトイン例外の基底クラスで、この行はどんな例外でも捕捉することができる
    res = Response(serializer.validated_data, status=status.HTTP_200_OK)

    try:
      res.delete_cookie("access_token")
      res.set_cookie(
        "access_token",
        serializer.validated_data["access"],
        max_age=60 * 60 * 24,
        httponly=True,
      )
      res.set_cookie(
        "refresh_token",
        serializer.validated_data["refresh"],
        max_age=60 * 60 * 24 * 30,
        httponly=True,
      )
    except Exception as e:
      raise e.APIException("Failed to set access_token cookies.")
    return res

# テスト済み
# access_tokenを使ってログインユーザーの情報を取得
#トークンが存在する前提で使用する関数
#関数名要変更
#クッキーからアクセストークンを取得→
#decodeで与えられたトークンが有効で、署名が正しいことを確認(settings.SECRETKEYを使用)→
#fetchAsyncCheckAuth
class CheckAuthView(APIView):
  serializer_class = serializers.UserSerializer
  authentication_classes = (CookieHandlerJWTAuthentication,)

  def get(self, request, *args, **kwargs):
    # Set-CookieにしているのでCookieからトークンを入手
    jwt_token = request.COOKIES.get("access_token")
    if not jwt_token:
      return Response(
        {"error": "No Token"}, status=status.HTTP_400_BAD_REQUEST
      )
    # Token検証
    try:
      #PyJWTのdecodeメソッド HS256とはアルゴリズムの名前
      payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=["HS256"])
      # トークンから抽出したPayloadからユーザーIDを取得
      loginUser = User.objects.get(id=payload["user_id"])
      # アクティブチェック(アカウントが有効である場合)
      if loginUser.is_active:
          # 通常、generics.CreateAPIView系統はこの処理をしなくてもいい
          # しかしtry-exceptの処理かつ、オーバーライドしているせいかResponse()で返せとエラーが出るので以下で処理
        res = serializers.UserSerializer(self.request.user)
        return Response(res.data, status=status.HTTP_200_OK)
      else:
        return Response(
          {"error": "User is not active"}, status=status.HTTP_400_BAD_REQUEST
        )
    #エラーハンドリングはこれでいい
    # Token期限切れ
    except jwt.ExpiredSignatureError:
      return Response(
        {"error": "Activations link expired"}, status=status.HTTP_401_UNAUTHORIZED
      )
    # 不正なToken
    except jwt.exceptions.DecodeError:
      return Response(
        {"error": "Invalid Token"}, status=status.HTTP_401_UNAUTHORIZED
      )
    # ユーザーが存在しない
    except User.DoesNotExist:
      return Response(
        {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
      )

# テスト済み
# coookieからリフレッシュトークンを取得するだけだから、たいした処理はいらない
class RefreshGetView(APIView):
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
#シリアライザはリフレッシュトークンの検証と、アクセストークンの生成を行う
#→リクエストから送られてきたリフレッシュトークンを扱うためにシリアライザを使う
#→serializer.is_valid(raise_exception=True)でシリアライザ内で定義されているバリデーションルールに基づいてデータの検証を行う
#→バリデーションを通過すればTrue、ダメならFalseを返している
#→トークンが無効なら例外をスロー、補足
#→
# HTTPRequestのBodyプロパティから送られてきたtokenを受け取る
# refresh_tokenを使って、新しいaccess_tokenを生成する
# fetchAsyncNewToken
# エラーハンドリングを改善できるかもしれない
#テスト済み
class AccessTokenRefreshView(jwt_views.TokenRefreshView):
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
    # こちらも、BadRequestの代わりにエラーメッセージを返します。
      return Response({"detail": str(e.args[0])}, status=status.HTTP_401_UNAUTHORIZED)

    # token更新
    res = Response(serializer.validated_data, status=status.HTTP_200_OK)
    # 既存のAccess_Tokenを削除
    try:
      res.delete_cookie("access_token")
      # 更新したTokenをセット
      res.set_cookie(
        "access_token",
        serializer.validated_data["access"],
        max_age=60 * 24 * 24 * 30,
        # samesite='Lax',
        httponly=True,
      )
    except Exception as e:
      raise e.APIException("Failed to set access_token cookies.")
    return res


#単一モデルのCRUD処理にmodelviewsetを使用すればコードが簡易的になる
class UserViewSet(ModelViewSet):
  queryset = User.objects.all()
  serializer_class = serializers.UserSerializer
  authentication_classes = (CookieHandlerJWTAuthentication,)

# テスト済み
class LogoutView(APIView):
  authentication_classes = (CookieHandlerJWTAuthentication,)

  def post(self, request, *args, **kwargs):
    res = Response({"message": "Logout"}, status=status.HTTP_200_OK)
    res.delete_cookie("access_token")
    res.delete_cookie("refresh_token")
    return res



# 済み
class DeleteUserView(APIView):
  authentication_classes = (CookieHandlerJWTAuthentication,)

  def delete(self, request):
    user = request.user
    if user is None:
      raise NotAuthenticated("ユーザーが認証されていません。")
    try:
      user.delete()
      return Response(
        status=status.HTTP_204_NO_CONTENT,
      )
    except Exception as e:
      raise APIException("ユーザーの削除に問題が発生しました。エラーメッセージ: {}".format(str(e)))





##RT取得込み
# class TokenRefreshView(jwt_views.TokenRefreshView):
#   def post(self, request, *args, **kwargs):
#     try:
#       # Cookieから直接リフレッシュトークンを取得
#       RT = request.COOKIES["refresh_token"]
#       print(f"Refresh Token from cookie: {RT}")
#       logger.info(f"Refresh Token from cookie: {RT}")
#     except:
#       return Response({"detail": "Refresh token not found."}, status=status.HTTP_401_UNAUTHORIZED)
#     serializer = self.get_serializer(data={"refresh": RT})
#     if not serializer.is_valid():
#       # BadRequestの代わりに、エラーメッセージを返します。
#       return Response({"detail": "Invalid or expired token."}, status=status.HTTP_401_UNAUTHORIZED)

#     try:
#       serializer.validated_data
#     except jwt_exp.TokenError as e:
#             # こちらも、BadRequestの代わりにエラーメッセージを返します。
#       return Response({"detail": str(e.args[0])}, status=status.HTTP_401_UNAUTHORIZED)

#         # token更新
#     res = Response(serializer.validated_data, status=status.HTTP_200_OK)
#     # 既存のAccess_Tokenを削除
#     res.delete_cookie("access_token")
#     # 更新したTokenをセット
#     res.set_cookie(
#       "user_token",
#       serializer.validated_data["access"],
#       max_age=60 * 24 * 24 * 30,
#       httponly=True,
#     )
#     return res