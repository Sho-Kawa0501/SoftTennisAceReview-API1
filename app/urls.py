from django.urls import path
from django.conf.urls import include
from app import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('post',views.PostViewSet)

urlpatterns = [
  path('post_list/',views.PostListView.as_view()),
  path('post_detail/<str:pk>/',views.PostDetailView.as_view()),
  path('',include(router.urls)),
]