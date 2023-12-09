from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from reviewsite.utils.image_utils import resize_image

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ('id','name','email','image','favorite_reviews','is_edited')

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
  class Meta:
    model = User
    fields = ('id','name','email','image','favorite_reviews','is_edited')

  default_error_messages = {
    'no_active_account': 'メールアドレスまたはパスワードが間違っています'
  }