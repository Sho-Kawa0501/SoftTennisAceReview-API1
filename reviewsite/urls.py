from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenVerifyView
from django.conf.urls.static import static
from django.views.static import serve
from django.conf import settings
from django.urls import re_path

urlpatterns = [
    path('api/verify/', TokenVerifyView.as_view()),
    path('api/auth/', include('account.urls',)),
    path('api/item/',include('item.urls')),
    path('api/', include('review.urls')), 
    path('admin/', admin.site.urls),
] 
