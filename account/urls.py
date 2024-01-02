from django.urls import path
from django.conf.urls import include
from rest_framework.routers import DefaultRouter
from account import views
from reviewsite.authentication import csrfToken

app_name = 'accounts'
router = DefaultRouter()
router.register('', views.UserViewSet)

urlpatterns = [
    path('users/', include(router.urls)),
    path('login/', views.MyTokenObtainPairView.as_view(),name='login'),
    path('register/', views.RegisterView.as_view(),name='register'),
    path('check-auth/', views.CheckAuthView.as_view(),name='check-auth'),
    path('csrf-token/',csrfToken),
    path('get-refresh-token/',views.GetRefreshTokenView.as_view(),name='get-refresh-token'),
    path('create-accesstoken/',views.CreateAccessTokenView.as_view(),name='create-accesstoken'),
    path('logout/',views.LogoutView.as_view(),name='logout'),
    path('user/delete/', views.DeleteUserView.as_view(),name='user/delete/'),
]
