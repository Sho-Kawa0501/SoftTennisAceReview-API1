from rest_framework import generics,serializers
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from item import serializers
from item import models
from rest_framework.response import Response

class ItemDetailView(generics.RetrieveAPIView):
  queryset = models.Item.objects.all()
  serializer_class = serializers.ItemSerializer
  permission_classes = (AllowAny,)

class ItemListView(generics.ListAPIView):
  queryset = models.Item.objects.all()
  serializer_class = serializers.ItemSerializer
  permission_classes = (AllowAny,)

class ItemMetadataListView(APIView):
  permission_classes = (AllowAny,)

  def get(self, request):
    brands = models.Brand.objects.all()
    series = models.Series.objects.all()
    positions = models.Position.objects.all()

    data = {
      "brands": serializers.BrandSerializer(brands, many=True).data,
      "series": serializers.SeriesSerializer(series, many=True).data,
      "positions": serializers.PositionSerializer(positions, many=True).data
    }

    return Response(data)