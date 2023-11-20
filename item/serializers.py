from rest_framework import serializers
from item import models 

class BrandSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.Brand
    fields = '__all__'

class SeriesSerializer(serializers.ModelSerializer):
  brand = BrandSerializer(read_only=True)

  class Meta:
    model = models.Series
    fields = '__all__'

class PositionSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.Position
    fields = '__all__'

class ItemSerializer(serializers.ModelSerializer) :
  brand = BrandSerializer(read_only=True)
  series = SeriesSerializer(read_only=True)
  position = PositionSerializer(read_only=True)

  class Meta:
    model = models.Item
    fields = '__all__'
    
