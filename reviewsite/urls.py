from django.contrib import admin
from django.urls import path, include
#simpleJWTにトークン用のviewが用意されているのでインポートする
from rest_framework_simplejwt.views import TokenVerifyView
from django.conf.urls.static import static
from django.conf import settings

#全体のapiを全てとる
#authをaccountに変更
#今後は認証情報を扱う場合はauthを使うというルールでいいかもしれない
urlpatterns = [
    path('api/verify/', TokenVerifyView.as_view()),
    path('api/auth/', include('accounts.urls',)),
    path('api/item/',include('item.urls')),
    path('api/', include('app.urls')), #本番ではapiをreviewに変える
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
