from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from item.models import Item, Brand, Series, Position
import datetime

class ItemDetailViewTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        brand = Brand.objects.create(name='Test Brand')
        series = Series.objects.create(name='Test Series', brand=brand)
        position = Position.objects.create(name='Test Position')
        cls.item = Item.objects.create(
            item_name='Test Item',
            slug='test-item',
            brand=brand,
            series=series,
            position=position,
            release_date=datetime.date.today(),
            display=True
        )

    def test_get_item_detail(self):
        url = reverse('items:item-detail', kwargs={'pk': self.item.id})
        response = self.client.get(url,format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['item_name'], self.item.item_name)

class ItemListViewTests(APITestCase):
    # アイテム取得
    def test_get_item_list(self):
        url = reverse('items:item-list')
        response = self.client.get(url,format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 0) 

class ItemMetadataListViewTests(APITestCase):
    # アイテムの要素取得
    def test_get_item_metadata(self):
        url = reverse('items:item-metadata-list')
        response = self.client.get(url,format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('brands', response.data)
        self.assertIn('series', response.data)
        self.assertIn('positions', response.data)
