from rest_framework import viewsets,generics,serializers
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from review import serializers
from review import models
from item.models import Item
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
import logging
from reviewsite.authentication import CookieHandlerJWTAuthentication
from django.contrib.auth import get_user_model
from rest_framework.exceptions import NotFound

User = get_user_model()
logger = logging.getLogger(__name__)

#Djangoのビュークラスの命名規則はにモデル名+アクション名+View

#Reviewに関する処理
#一覧表示
class ReviewListView(generics.ListAPIView):
  queryset = models.Review.objects.all().order_by('-created_at')
  serializer_class = serializers.ReviewSerializer
  permission_classes = (AllowAny,)


#最新のレビューを2つ渡す
class LatestTwoReviewView(generics.ListAPIView):
  serializer_class = serializers.ReviewSerializer
  permission_classes = (AllowAny,)

  def get_queryset(self):
    return models.Review.objects.all().order_by('-created_at')[:2]


class MyReviewListView(APIView):
  serializer_class = serializers.ReviewSerializer
  # permission_classes = (IsAuthenticated,)
  authentication_classes = (CookieHandlerJWTAuthentication,)

  def get_queryset(self):
    return models.Review.objects.filter(user=self.request.user,).order_by('-created_at')
    # itemIdが設定されていない場合、ユーザーのすべてのレビューを返す

  def get(self, request, *args, **kwargs):
    queryset = self.get_queryset()
    serializer = self.serializer_class(queryset, many=True, context={'request': request})
    return Response(serializer.data)

#ログインユーザー以外のレビューを取得
class OtherUsersReviewListView(APIView):
  serializer_class = serializers.ReviewSerializer
  authentication_classes = (CookieHandlerJWTAuthentication,)

  def get_queryset(self):
    item_id = self.kwargs.get('item_id', None)
    if item_id:
      # item_id がマッチし、ログインユーザー以外のレビューを取得
      return models.Review.objects.exclude(user=self.request.user).filter(item__id=item_id).order_by('-created_at')
    # itemIdが設定されていない場合、ログインユーザー以外のすべてのレビューを返す
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

  def perform_create(self, serializer):
    item_id = self.kwargs['item_id']
    serializer.save(user=self.request.user, item_id=item_id)

class GetFavoriteReviewCountView(generics.RetrieveAPIView):
  queryset = models.Favorite.objects.all()
  serializer_class = serializers.FavoriteCountSerializer
  authentication_classes = (CookieHandlerJWTAuthentication,)

  def get_object(self):
    review_id = self.kwargs['review_id']
    review = models.Review.objects.get(id=review_id)
    count = models.Favorite.objects.filter(review=review).count()
    return {'favorites_count': count}

#新規投稿、編集、削除
class ReviewViewSet(viewsets.ModelViewSet):
  queryset = models.Review.objects.all()
  serializer_class = serializers.ReviewSerializer
  authentication_classes = (CookieHandlerJWTAuthentication,)

  def perform_create(self,serializer,**kwargs):
    serializer.save(user=self.request.user)

  def perform_update(self, serializer):
    review = serializer.instance
    if not review.is_edited:  # 既に編集されていない場合のみ
      serializer.save(is_edited=True)  # is_editedをTrueに設定
    else:
      serializer.save()


class ReviewListFilterView(generics.ListAPIView):
  serializer_class = serializers.ReviewSerializer
  permission_classes = (AllowAny,)
  def get_queryset(self):
    item_id = self.kwargs['pk']
    return models.Review.objects.filter(item_id=item_id)

#ログインユーザーのお気に入りをしたレビュー一覧
class GetFavoriteListView(generics.ListAPIView):
  serializer_class = serializers.ReviewSerializer
  authentication_classes = (CookieHandlerJWTAuthentication,)
  def get_queryset(self):
    user = self.request.user
    # ログインユーザーがお気に入りとして登録したレビューのIDを取得
    favorite_review_ids = models.Favorite.objects.filter(user=user).values_list('review_id', flat=True)
    # 取得したIDを使用してレビューを取得
    return models.Review.objects.filter(id__in=favorite_review_ids).order_by('-created_at')


#APIView?
#GetLikeReviewCountView
#GetLikeReviewCountViewというreviewIdを受け取り、そのReviewのlikeの数を返すviewを作成
class GetFavoriteReviewCountView(generics.RetrieveAPIView):
  # queryset = models.Favorite.objects.all()
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


#何故かAPIView判定になってる
#review_idとuser_idを引数にして、
#Likeモデルに引数の2つのidを含むlikeオブジェクトがあればtrue,なければfalseを返すGetLikeReviewViewを作成
class GetFavoriteReviewView(generics.RetrieveAPIView):
  serializer_class = serializers.FavoriteSerializer
  authentication_classes = (CookieHandlerJWTAuthentication,)

  #取得してきたreviewidを使って、
  #Favoriteモデルからユーザーがログインユーザー、取得したreviewidのオブジェクトを持ってくる
  def get_queryset(self):
    review_id = self.kwargs['review_id']
    return models.Favorite.objects.filter(user=self.request.user, review_id=review_id)
  #使っていない引数は残す
  def get(self, request, *args, **kwargs):
    favorite = self.get_queryset().exists()
    if favorite:
      return Response({'isFavorite': True})
    else:
      return Response({'isFavorite': False})
      

#ViewsetよりかはAPIViewを使用するべき？
# 真のいいね登録削除機能
class FavoriteViewSet(viewsets.ViewSet):
  # queryset = models.Favorite.objects.all()
  serializer_class = serializers.FavoriteSerializer
  authentication_classes = (CookieHandlerJWTAuthentication,)

  def create(self, request, review_id=None):
    review = get_object_or_404(models.Review, pk=review_id)
    models.Favorite.objects.create(user=request.user, review=review)
    review.favorites_count = models.Favorite.objects.filter(review=review).count()  # likes_count を更新します
    review.save()
    return Response({'status': 'favorite set'}, status=status.HTTP_201_CREATED)

  def destroy(self, request, review_id=None):
    review = get_object_or_404(models.Review, pk=review_id)
    favorite = get_object_or_404(models.Favorite, user=request.user, review=review)
    favorite.delete()
    review.favorites_count = models.Favorite.objects.filter(review=review).count()  # likes_count を更新します
    review.save()
    return Response({'status': 'favorite removed'}, status=status.HTTP_204_NO_CONTENT)