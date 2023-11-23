from rest_framework import serializers
from review import models
from account.serializers import UserSerializer
from item.serializers import ItemSerializer
from reviewsite.utils.image_utils import resize_image

class ReviewSerializer(serializers.ModelSerializer):
  user = UserSerializer(read_only=True)
  item = ItemSerializer(read_only=True)
  favorites_count = serializers.IntegerField(read_only=True)
  is_my_review = serializers.SerializerMethodField()

  class Meta:
    model = models.Review
    fields = '__all__'

  def create(self, validated_data):
    image = validated_data.pop('image', None)
    review = models.Review.objects.create(**validated_data)
    if image:
      resized_image = resize_image(image)
      review.image.save(resized_image.name, resized_image, save=True)
    return review

  def update(self, instance, validated_data):
    image = validated_data.pop('image', None)
    if image:
      resized_image = resize_image(image)
      instance.image.save(resized_image.name, resized_image, save=False)

    for attr, value in validated_data.items():
      setattr(instance, attr, value)
    instance.save()
    return instance

  def get_is_my_review(self, obj):
    return self.context['request'].user == obj.user

class FavoriteSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.Favorite
    fields = '__all__'

class FavoriteCountSerializer(serializers.Serializer):
  favorites_count = serializers.IntegerField()