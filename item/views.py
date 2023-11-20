from django.shortcuts import render
from rest_framework import viewsets,generics,serializers
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from item import serializers
from item import models
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
import logging
from reviewsite.authentication import CookieHandlerJWTAuthentication
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


# class BrandListView(generics.ListAPIView):
#   queryset = models.Brand.objects.all()
#   serializer_class = serializers.BrandSerializer
#   permission_classes = (AllowAny,)

# class SeriesListView(generics.ListAPIView):
#   queryset = models.Series.objects.all()
#   serializer_class = serializers.SeriesSerializer
#   permission_classes = (AllowAny,)

# class PositionListView(generics.ListAPIView):
#   queryset = models.Position.objects.all()
#   serializer_class = serializers.PositionSerializer
#   permission_classes = (AllowAny,)