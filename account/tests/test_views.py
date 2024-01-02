#レスポンスのステータスコード、jsonデータの内容
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.serializers import ValidationError
from django.contrib.auth import get_user_model
from django.conf import settings
import jwt
import uuid
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.test import APIClient
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from email.utils import parsedate_to_datetime
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class RegisterViewTests(APITestCase):
  #新規ユーザーの登録
  def test_register_user(self):
    url = reverse('accounts:register')
    data = {
      'email': 'test@example.com',
      'password': 'testpassword123'
    }
    response = self.client.post(url, data, format='json')
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    self.assertTrue(User.objects.filter(email='test@example.com').exists())

  #すでに登録されているアカウントを使用して登録
  def test_register_user_with_existing_email(self):
    User.objects.create_user('existing@example.com', 'testpassword123')
    url = reverse('accounts:register')
    data = {
      'email': 'existing@example.com',
      'password': 'testpassword123'
    }
    response = self.client.post(url, data, format='json')
    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertIn('既に登録されているメールアドレスです。', response.data)

  #無効なデータを用いた登録
  def test_register_user_with_invalid_data(self):
    url = reverse('accounts:register')
    data = {
      'email': '', 
      'password': 'testpassword123'
    }
    response = self.client.post(url, data, format='json')
    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class MyTokenObtainPairViewTest(APITestCase):
  def setUp(self):
    self.user = User.objects.create_user(
      email='test@example.com',
      password='testpassword'
    )
    self.url = reverse('accounts:login')

  # 正しい資格情報でトークンを取得する
  def test_obtain_token_success(self):
    data = {
      'email': 'test@example.com',
      'password': 'testpassword'
    }
    response = self.client.post(self.url, data, format='json')

    # レスポンスコードとトークンの存在を確認。
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertIn('access', response.data)
    self.assertIn('refresh', response.data)
    self.assertIn('access_token', response.cookies)
    self.assertIn('refresh_token', response.cookies)

  # 不正な資格情報でトークン取得を試みる
  def test_obtain_token_fail(self):
    data = {
      'email': 'test@example.com',
      'password': 'wrongpassword123'
    }
    response = self.client.post(self.url, data, format='json')
    self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_400_BAD_REQUEST])

class CreateAccessTokenViewTest(APITestCase):
  def setUp(self):
    self.user = User.objects.create_user(email='test@example.com', password='password123')
    self.refresh_token = RefreshToken.for_user(self.user)
    self.url = reverse('accounts:access-token-refresh')

  def test_token_refresh(self):
    data = {
        'refresh': str(self.refresh_token)
    }
    response = self.client.post(self.url, data)
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertIn('access', response.data)


class CheckAuthViewTest(APITestCase):
  def setUp(self):
    self.user = User.objects.create_user(
      email='test@example.com',
      password='testpassword123',
    )
    self.inactive_user = User.objects.create_user(
      email='inactive@example.com',
      password='testpassword123',
    )
    self.inactive_user.is_active = False
    self.inactive_user.save()
    self.url = reverse('accounts:loginuser-information')

  #トークン作成関数
  def _generate_token(self, user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)

  #有効値を使用した場合
  def test_user_active_with_valid_token(self):
    token = self._generate_token(self.user)
    self.client.cookies['access_token'] = token
    response = self.client.get(self.url)
    self.assertEqual(response.status_code, status.HTTP_200_OK)

  # トークンがクッキーにない場合
  def test_no_token_in_cookie(self):
    response = self.client.get(self.url)
    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

  # 期限切れのトークンを使用
  def test_expired_token(self):
    # Generate a token then modify its 'exp' claim to simulate expiration
    token = self._generate_token(self.user)
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    payload['exp'] = 0 
    expired_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    self.client.cookies['access_token'] = expired_token
    response = self.client.get(self.url)
    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

  # 無効なトークンを使用
  def test_invalid_token(self):
    self.client.cookies['access_token'] = 'invalidtoken'
    response = self.client.get(self.url)
    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

  # ユーザーなし
  def test_user_not_found(self):
    token = self._generate_token(self.user)
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    payload['user_id'] = str(uuid.uuid4())  # Simulate non-existent user ID
    invalid_user_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    self.client.cookies['access_token'] = invalid_user_token
    response = self.client.get(self.url)
    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

  # ユーザーがアクティブでない場合
  def test_user_not_active(self):
    valid_token = self._generate_token(self.inactive_user)
    self.client.cookies['access_token'] = valid_token
    response = self.client.get(self.url)
    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class GetRefreshTokenViewTestCase(APITestCase):
  def setUp(self):
    # テスト用のユーザーを作成し、refresh_tokenを生成する
    self.user = User.objects.create_user(
        email='test@example.com',
        password='testpassword123'
    )
    self.refresh_token = RefreshToken.for_user(self.user)
    self.refresh_token_str = str(self.refresh_token)

  # #有効値を使用した場合
  def test_refresh_token_exists(self):
    self.client.cookies['refresh_token'] = self.refresh_token_str
    self.client.force_authenticate(user=self.user)
    url = reverse('accounts:refresh-token')
    response = self.client.get(url)
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data, {'refresh': self.refresh_token_str})
    
  #トークンがない場合
  def test_refresh_token_not_found(self):
    url = reverse('accounts:refresh-token')
    response = self.client.get(url)
    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

  # トークンが無効である場合
  def test_refresh_token_invalid(self):
    url = reverse('accounts:refresh-token')
    response = self.client.get(url)
    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class LogoutViewTestCase(APITestCase):
  def setUp(self):
    self.user = User.objects.create_user(email='user@example.com', password='password123')
    self.client = APIClient()
    self.logout_url = reverse('accounts:logout')  # DjangoのURLリバース関数を使用してURLを取得する
    self.client.force_authenticate(user=self.user)  # テスト用クライアントでユーザーを認証する

  # ログアウト成功時
  def test_logout_success(self):
    response = self.client.post(self.logout_url)
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data['message'], "Logout")

    # 'access_token'と'refresh_token'のクッキーが無効化されていることを確認する
    for cookie_name in ['access_token', 'refresh_token']:
      self.assertIn(cookie_name, response.cookies)
      self.assertEqual(response.cookies[cookie_name].value, '')
      cookie_expires = response.cookies[cookie_name]['expires']
      self.assertIsInstance(cookie_expires, str)
      expires_datetime = parsedate_to_datetime(cookie_expires)
      self.assertTrue(timezone.now() > expires_datetime)


class DeleteUserViewTest(APITestCase):
  def setUp(self):
    self.user = User.objects.create_user(email='test@example.com', password='password123')
    self.url = reverse('accounts:user/delete/')  # URLの名前を修正してください。
    self.client.force_authenticate(user=self.user)

  # アカウント削除成功時
  def test_delete_user(self):
    response = self.client.delete(self.url)
    self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    self.assertFalse(User.objects.filter(email='test@example.com').exists())

  # ログアウトしている状態のアカウントが、アカウント削除を実行した場合
  def test_delete_user_unauthenticated(self):
    self.client.logout()
    response = self.client.delete(self.url)
    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

  def tearDown(self):
    self.client.force_authenticate(user=None)



# プロフィール編集 未完成
# class UserViewSetTest(APITestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(email='test@example.com', password='password123')
#         self.token = RefreshToken.for_user(self.user)
#         self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')

#     def test_edit_user(self):
#         update_url = reverse('accounts:user-detail', kwargs={'pk': self.user.id})
#         data = {
#             'name': 'Updated Name',
#             # 'email': 'updated@example.com',
#             'image': self.get_test_image_file()
#         }
#         response = self.client.patch(update_url, data, format='multipart')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.user.refresh_from_db()
#         self.assertEqual(self.user.name, 'Updated Name')

#     def get_test_image_file(self):
#         with open('media/tests/test100KB.jpg', 'rb') as img_file:
#             image = SimpleUploadedFile(name='test_image.jpg', content=img_file.read(), content_type='image/jpeg')
#         return image

