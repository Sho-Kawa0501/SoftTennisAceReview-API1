from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from item.models import Item,Brand,Series,Position
from app.models import Review,Favorite
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
import datetime
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile


User = get_user_model()

# ベーステストクラス
class BaseReviewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # 共通のテストデータセットアップ
        cls.user = User.objects.create_user(email='test1@example.com', password='testpass')
        cls.brand = Brand.objects.create(name='Test Brand')
        cls.series = Series.objects.create(name='Test Series', brand=cls.brand)
        cls.position = Position.objects.create(name='Test Position')
        
        cls.item = Item.objects.create(
            item_name='Test Item',
            slug='test-item',
            brand=cls.brand,
            series=cls.series,
            position=cls.position,
            release_date=datetime.date(2023, 10, 1),
            display=True
        )
        time_now = timezone.now()
        cls.review1 = Review.objects.create(
            user=cls.user, 
            item=cls.item, 
            title='Review 1', 
            content='Content 1',
            created_at=time_now - datetime.timedelta(seconds=10)
        )
        cls.review2 = Review.objects.create( 
            user=cls.user, 
            item=cls.item, 
            title='Review 2', 
            content='Content 2',
            created_at=time_now
        )

# ReviewListViewのテストクラス
class ReviewListViewTest(BaseReviewTest):
    def setUp(self):
        self.url = reverse('reviews:review-list')
    
    # レビュー一覧を正常に取得できるか
    def test_get_review_list(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url,format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [review['title'] for review in response.data]
        self.assertIn(self.review1.title, titles)
        self.assertIn(self.review2.title, titles)
        self.client.force_authenticate(user=None)

    # 取得したレビューが降順となっているか
    def test_get_review_list_order(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url,format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        created_at_list = [datetime.datetime.strptime(review['created_at'], 
            "%Y/%m/%d %H:%M") for review in response.data]

        # リストが降順になっていることを確認（最新のレビューが最初）
        for i in range(len(created_at_list) - 1):
            self.assertTrue(created_at_list[i] >= created_at_list[i + 1])

        self.client.force_authenticate(user=None)

class MyReviewListViewTest(BaseReviewTest):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.url = reverse('reviews:my-reviews-list-all')

    # 自分が投稿したレビュー（マイレビュー）取得
    def test_list_my_reviews(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # setUpTestDataで作成された2つのレビューがあるはず

    # 認証されていない状態でマイレビュー取得を試みる
    def test_no_auth(self):
        self.client.force_authenticate(user=None)  # 認証を解除
        response = self.client.get(self.url,format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)  

class OtherUsersReviewListViewTest(BaseReviewTest):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        item_id = self.item.id
        self.url = reverse('reviews:otherusers-review-list', kwargs={'item_id': item_id})

    #　自分の投稿（マイレビュー）以外のレビューを取得
    def test_list_other_users_reviews(self):
        # 他のユーザーを作成し、レビューを作成
        other_user = User.objects.create_user(email='other@example.com', password='testpass')
        Review.objects.create(
            user=other_user, 
            item=self.item, 
            title='Other User Review', 
            content='Content by other user'
        )
        
        response = self.client.get(self.url,format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    # 認証されていない状態で取得を試みる
    def test_no_auth(self):
        self.client.force_authenticate(user=None)  # 認証を解除
        response = self.client.get(self.url,format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ReviewViewSetTests(BaseReviewTest):
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.user = User.objects.create_user(email='test2@example.com', password='password')
        self.client.force_authenticate(user=self.user)
        self.existing_review = Review.objects.create(
            item=self.item, 
            user=self.user, 
            title='Test Title', 
            content='Test Content',
            image='ImageData10'
        )
        self.create_url = reverse('reviews:create-review', kwargs={'item_id': self.item.id})
        self.update_url = reverse('reviews:review-detail', kwargs={'pk': self.existing_review.id})
        self.delete_url = reverse('reviews:review-detail', kwargs={'pk': self.existing_review.id})

    # レビュー作成
    def test_create_review(self):
        with open('media/tests/test100KB.jpg', 'rb') as img_file:
            image = SimpleUploadedFile(name='test_image.jpg', content=img_file.read(), content_type='image/jpeg')

        data = {
            "title": "New Review",
            "content": "This is a new review.",
            "image":image,
            "item": self.item.id,
        }
        response = self.client.post(self.create_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 4)

    # レビュー編集
    def test_update_review(self):
        with open('media/tests/test100KB.jpg', 'rb') as img_file:
            image = SimpleUploadedFile(name='test_image.jpg', content=img_file.read(), content_type='image/jpeg')

        data = {
            "title": "Updated Review",
            "content": "This is a update review.",
            "image":image,
            "reviewId": str(self.existing_review.id),
        }
        response = self.client.patch(self.update_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.existing_review.refresh_from_db()
        self.assertEqual(self.existing_review.title, "Updated Review")

    # レビュー削除
    def test_delete_review(self):
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class ReviewListFilterViewTests(BaseReviewTest):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        item_id = self.item.id
        self.url = reverse('reviews:review-list-filter', kwargs={'pk': item_id})

    # 特定のアイテムに対するレビューを取得
    def test_filter_reviews_by_item(self):
        response = self.client.get(self.url,format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2) 

class GetFavoriteListViewTest(BaseReviewTest):
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.url = reverse('reviews:get-favorite-list')
        self.favorite = Favorite.objects.create(user=self.user, review=self.review1)

    # レビューのお気に入りを取得
    def test_get_favorite_list(self):
        response = self.client.get(self.url,format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # 1つのお気に入りがあるはず
        self.assertEqual(response.data[0]['id'], str(self.review1.id))  # 正しいレビューが取得されるか確認

class GetFavoriteReviewCountViewTest(BaseReviewTest):
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.url = lambda review_id: reverse('reviews:get-favorite-review-count', kwargs={'review_id': review_id})
        self.favorite = Favorite.objects.create(user=self.user, review=self.review1)

    # お気に入りの数を取得
    def test_get_favorite_review_count(self):
        url = self.url(str(self.review1.id))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['favorites_count'], 1)  # お気に入り数は1

class GetFavoriteReviewViewTests(BaseReviewTest):
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.url = lambda review_id: reverse('reviews:get-favorite-review', kwargs={'review_id': review_id})

    # レビューにお気に入りがされていることを確認
    def test_get_favorite_status_true(self):
        Favorite.objects.create(user=self.user, review=self.review1)
        url = self.url(str(self.review1.id))
        response = self.client.get(url,format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['isFavorite'])

    #レビューにお気に入り登録がされていないことを確認
    def test_get_favorite_status_false(self):
        url = self.url(str(self.review1.id))
        response = self.client.get(url,format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['isFavorite'])

class FavoriteViewSetTests(BaseReviewTest):
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.create_url = reverse('reviews:favorite-create', kwargs={'review_id': self.review1.id})
        self.destroy_url = reverse('reviews:favorite-destroy', kwargs={'review_id': self.review2.id})

    #お気に入りが作成されたかを確認
    def test_create_favorite(self):
        response = self.client.post(self.create_url,format='json') 
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Favorite.objects.filter(user=self.user, review=self.review1).exists())

    #お気に入りが削除されたかを確認
    def test_destroy_favorite(self):
        Favorite.objects.create(user=self.user, review=self.review2)
        response = self.client.delete(self.destroy_url,format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Favorite.objects.filter(user=self.user, review=self.review2).exists())

