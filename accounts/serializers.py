#querysetやモデルインスタンス等複雑なデータ形式をjsonformatに変換する役割を持つ
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ('id','email')