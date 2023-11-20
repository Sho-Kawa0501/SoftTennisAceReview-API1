#querysetやモデルインスタンス等複雑なデータ形式をjsonformatに変換する役割を持つ
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from reviewsite.utils.image_utils import resize_image

User = get_user_model()

#modelフィールドを再利用
class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    # fields = '__all__'
    fields = ('id','name','email','image','favorite_reviews')

  def update(self, instance, validated_data):
    image = validated_data.pop('image', None)
    if image:
      resized_image = resize_image(image)
      instance.image.save(resized_image.name, resized_image, save=False)

    for attr, value in validated_data.items():
      setattr(instance, attr, value)
    instance.save()
    return instance

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
  class Meta:
    model = User
    # fields = '__all__'
    fields = ('id','name','email','image','favorite_reviews')

  default_error_messages = {
    'no_active_account': 'メールアドレスまたはパスワードが間違っています'
  }