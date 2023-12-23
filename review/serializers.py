from rest_framework import serializers
from review import models
from account.serializers import UserSerializer
from item.serializers import ItemSerializer

class ReviewSerializer(serializers.ModelSerializer):
  # user = UserSerializer(read_only=True)
  item = ItemSerializer(read_only=True)
  favorites_count = serializers.IntegerField(read_only=True)
  is_my_review = serializers.SerializerMethodField()

  class Meta:
    model = models.Review
    fields = '__all__'

  def get_is_my_review(self, obj):
    return self.context['request'].user == obj.user

class FavoriteSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.Favorite
    fields = '__all__'

class FavoriteCountSerializer(serializers.Serializer):
  favorites_count = serializers.IntegerField()