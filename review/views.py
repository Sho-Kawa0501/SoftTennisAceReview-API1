from rest_framework import viewsets,generics,serializers
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from review import serializers
from review import models
from item.models import Item
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import logging
from reviewsite.authentication import CookieHandlerJWTAuthentication
from reviewsite.utils.image_utils import resize_image
from django.contrib.auth import get_user_model
from rest_framework.exceptions import NotFound
from PIL import Image
import io
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import ValidationError

User = get_user_model()
logger = logging.getLogger(__name__)

#一覧表示
class ReviewListView(generics.ListAPIView):
  queryset = models.Review.objects.all().order_by('-created_at')
  serializer_class = serializers.ReviewSerializer
  permission_classes = (AllowAny,)


class MyReviewListView(APIView):
  serializer_class = serializers.ReviewSerializer
  authentication_classes = (CookieHandlerJWTAuthentication,)

  def get_queryset(self):
    return models.Review.objects.filter(user=self.request.user,).order_by('-created_at')

  def get(self, request, *args, **kwargs):
    queryset = self.get_queryset()
    serializer = self.serializer_class(queryset, many=True, context={'request': request})
    return Response(serializer.data)

#ログインしているユーザー以外のユーザーが投稿したレビューを取得
class OtherUsersReviewListView(APIView):
  serializer_class = serializers.ReviewSerializer
  authentication_classes = (CookieHandlerJWTAuthentication,)

  def get_queryset(self):
    item_id = self.kwargs.get('item_id', None)
    if item_id:
      return models.Review.objects.exclude(user=self.request.user).filter(item__id=item_id).order_by('-created_at')
    return models.Review.objects.exclude(user=self.request.user).order_by('-created_at')

  def get(self, request, *args, **kwargs):
    queryset = self.get_queryset()
    serializer = self.serializer_class(queryset, many=True, context={'request': request})
    return Response(serializer.data)


#レビューの詳細
class ReviewDetailView(generics.RetrieveAPIView):
  queryset = models.Review.objects.all()
  serializer_class = serializers.ReviewSerializer
  permission_classes = (AllowAny,)

class CreateReviewView(generics.CreateAPIView):
  queryset = models.Review.objects.all()
  serializer_class = serializers.ReviewSerializer
  authentication_classes = (CookieHandlerJWTAuthentication,)
  parser_classes = (MultiPartParser, FormParser)

  def perform_create(self, serializer):
    image = self.request.FILES.get('image')
    if not image:
      raise ValidationError({'image': 'Image is required.'})
      
    with Image.open(image) as img:
      resized_image = resize_image(img)

    image_io = io.BytesIO()
    resized_image.save(image_io, format='JPEG', quality=85)
    image_io.seek(0)
    image_file = InMemoryUploadedFile(
      image_io,
      None,
      image.name,
      'image/jpeg',
      image_io.getbuffer().nbytes, None
    )
    item_id = self.kwargs.get('item_id')

    serializer.save(user=self.request.user, image=image_file, item_id=item_id)


#新規投稿、編集、削除
class ReviewViewSet(viewsets.ModelViewSet):
  queryset = models.Review.objects.all()
  serializer_class = serializers.ReviewSerializer
  authentication_classes = (CookieHandlerJWTAuthentication,)

  # def perform_create(self,serializer,**kwargs):
  #   serializer.save(user=self.request.user)

  def perform_update(self, serializer):
    # レビューの画像が変更される場合の処理（S3から古い画像を削除する処理を追加）
    review = serializer.instance
    if 'image' in serializer.validated_data:
      # S3から古い画像を削除する処理をここに追加
      pass

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

    if not review.is_edited:
      serializer.save(is_edited=True)
    else:
      serializer.save()


class ReviewListFilterView(generics.ListAPIView):
  serializer_class = serializers.ReviewSerializer
  permission_classes = (AllowAny,)
  def get_queryset(self):
    item_id = self.kwargs['pk']
    return models.Review.objects.filter(item_id=item_id)


class GetFavoriteReviewCountView(generics.RetrieveAPIView):
  queryset = models.Favorite.objects.all()
  serializer_class = serializers.FavoriteCountSerializer
  authentication_classes = (CookieHandlerJWTAuthentication,)

  def get_object(self):
    review_id = self.kwargs['review_id']
    review = models.Review.objects.get(id=review_id)
    count = models.Favorite.objects.filter(review=review).count()
    return {'favorites_count': count}


#ログインユーザーのお気に入りをしたレビュー一覧
class GetFavoriteListView(generics.ListAPIView):
  serializer_class = serializers.ReviewSerializer
  authentication_classes = (CookieHandlerJWTAuthentication,)

  def get_queryset(self):
    user = self.request.user
    favorite_review_ids = models.Favorite.objects.filter(user=user).values_list('review_id', flat=True)
    return models.Review.objects.filter(id__in=favorite_review_ids).order_by('-created_at')

#reviewIdを受け取り、それと一致するレビューのいいねの数を返す
class GetFavoriteReviewCountView(generics.RetrieveAPIView):
  serializer_class = serializers.FavoriteCountSerializer
  authentication_classes = (CookieHandlerJWTAuthentication,)

  def get_object(self):
    review_id = self.kwargs['review_id']
    try:
      review = models.Review.objects.get(id=review_id)
    except models.Review.DoesNotExist:
      raise NotFound('Review does not exist.')
    count = models.Favorite.objects.filter(review=review).count()
    return {'favorites_count': count}

#review_idとuser_idを受け取り、レビューにいいねをしているかしていないかを返す
class GetFavoriteReviewView(generics.RetrieveAPIView):
  serializer_class = serializers.FavoriteSerializer
  authentication_classes = (CookieHandlerJWTAuthentication,)

  #Favoriteモデルからユーザーがログインユーザー、取得したreviewidのオブジェクトを持ってくる
  def get_queryset(self):
    review_id = self.kwargs['review_id']
    return models.Favorite.objects.filter(user=self.request.user, review_id=review_id)
  
  def get(self, *args, **kwargs):
    favorite = self.get_queryset().exists()
    if favorite:
      return Response({'isFavorite': True})
    else:
      return Response({'isFavorite': False})
      

#いいね登録削除機能
class FavoriteViewSet(viewsets.ViewSet):
  serializer_class = serializers.FavoriteSerializer
  authentication_classes = (CookieHandlerJWTAuthentication,)

  def create(self, request, review_id=None):
    review = get_object_or_404(models.Review, pk=review_id)
    models.Favorite.objects.create(user=request.user, review=review)
    review.favorites_count = models.Favorite.objects.filter(review=review).count()
    review.save()
    return Response({'status': 'favorite set'}, status=status.HTTP_201_CREATED)

  def destroy(self, request, review_id=None):
    review = get_object_or_404(models.Review, pk=review_id)
    favorite = get_object_or_404(models.Favorite, user=request.user, review=review)
    favorite.delete()
    review.favorites_count = models.Favorite.objects.filter(review=review).count()
    review.save()
    return Response({'status': 'favorite removed'}, status=status.HTTP_204_NO_CONTENT)