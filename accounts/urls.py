from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, UserView,UserViewSet

router = DefaultRouter()
router.register('', UserViewSet)

urlpatterns = [
    path('users/', include(router.urls)),
    path('register/', RegisterView.as_view()), #認証用
    path('user/', UserView.as_view()), #ユーザー情報取得用
]