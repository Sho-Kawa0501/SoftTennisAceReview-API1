from django.urls import path, include
from rest_framework.routers import DefaultRouter
from item import views

app_name='items'
router = DefaultRouter()
# router.register('', UserViewSet)

urlpatterns = [
  path('item_list/',views.ItemListView.as_view(),name='item-list'),
  path('item_detail/<int:pk>/',views.ItemDetailView.as_view(),name='item-detail'),
  path('item_metadata_list/', views.ItemMetadataListView.as_view(),name='item-metadata-list'),
]