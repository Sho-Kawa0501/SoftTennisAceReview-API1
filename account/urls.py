from django.urls import path
from django.conf.urls import include
from rest_framework.routers import DefaultRouter
from account import views
from reviewsite.authentication import csrfToken

app_name = 'accounts'
router = DefaultRouter()
router.register('', views.UserViewSet)

urlpatterns = [
    path('login/', views.MyTokenObtainPairView.as_view(),name='login'),
    path('csrf-token/',csrfToken),
    path('users/', include(router.urls)),
    path('token/refresh/',views.AccessTokenRefreshView.as_view(),name='access-token-refresh'),
    path('refresh-token/',views.RefreshGetView.as_view(),name='refresh-token'),
    path('register/', views.RegisterView.as_view(),name='register'), 
    path('loginuser-information/', views.CheckAuthView.as_view(),name='loginuser-information'), 
    path('logout/',views.LogoutView.as_view(),name='logout'),
    path('user/delete/', views.DeleteUserView.as_view(),name='user/delete/'),
]
