from django.urls import path
from .views import RegisterView, UserView

urlpatterns = [
    path('register/', RegisterView.as_view()), #認証用
    path('user/', UserView.as_view()), #ユーザー情報取得用
]