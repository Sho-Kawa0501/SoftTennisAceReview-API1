from django.contrib import admin
from django.urls import path, include
#simpleJWTにトークン用のviewが用意されているのでインポートする
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('api/login/', TokenObtainPairView.as_view()),
    path('api/refresh/', TokenRefreshView.as_view()),
    path('api/verify/', TokenVerifyView.as_view()),
    path('api/auth/', include('accounts.urls')),
    path('api/', include('app.urls')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
