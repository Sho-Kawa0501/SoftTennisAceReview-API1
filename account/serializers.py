from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
  def validate(self, attrs):
    authenticate_kwargs = {
      'email': attrs.get('email'),
      'password': attrs.get('password'),
    }
    user = authenticate(**authenticate_kwargs)
    
    if not user:
      raise AuthenticationFailed('メールアドレスまたはパスワードが間違っています。')

    data = super().validate(attrs)
    return data

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
  image = serializers.ImageField(default='default/default.png')
  
  class Meta:
    model = User
    fields = ('id','name','email','image','favorite_reviews')

