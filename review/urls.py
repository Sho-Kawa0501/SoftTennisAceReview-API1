from django.urls import path
from django.conf.urls import include
from review import views
from rest_framework.routers import DefaultRouter

app_name = 'reviews'
router = DefaultRouter()
router.register('reviews', views.ReviewViewSet)

urlpatterns = [
  # path('review_list/',views.ReviewListView.as_view(),name='review-list'),
  path('myreview_list/', views.MyReviewListView.as_view(), name='my-reviews-list-all'),
  path('otherusers_review_list/<int:item_id>',views.OtherUsersReviewListView.as_view(),name='otherusers-review-list'),
  path('review_list/<int:pk>/',views.ReviewListFilterView.as_view(),name='review-list-filter'),
  path('review/create/<int:item_id>/', views.CreateReviewView.as_view(),name='create-review'),
  path('favorite_list/', views.GetFavoriteListView.as_view(),name='get-favorite-list'),
  path('review/<str:review_id>/favorite/', views.GetFavoriteReviewView.as_view(),name='get-favorite-review'),
  path('review/favorites_count/<str:review_id>/', views.GetFavoriteReviewCountView.as_view(),name='get-favorite-review-count'),
  path('review/set/<str:review_id>/', views.FavoriteViewSet.as_view({'post': 'create', 'delete': 'destroy'}),name='favorite-viewset'),
  path('review/set/<str:review_id>/favorite/', views.FavoriteViewSet.as_view({'post': 'create'}), name='favorite-create'),
  path('review/set/<str:review_id>/unfavorite/', views.FavoriteViewSet.as_view({'delete': 'destroy'}), name='favorite-destroy'),
  path('',include(router.urls)),
]