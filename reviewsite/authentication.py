from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from django.http import HttpResponseBadRequest
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.conf import settings
from rest_framework import exceptions
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
import logging

logger = logging.getLogger(__name__)


class CookieHandlerJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # Cookieヘッダーからaccess_tokenを取得
        access_token = request.COOKIES.get('access_token')
        if not access_token:
            logger.info('no token')
            return None
        
        request.META['HTTP_AUTHORIZATION'] = 'Bearer {access_token}'.format(access_token=access_token)

        try:
            return super().authenticate(request)
        except InvalidToken:
            if not settings.SECRET_KEY == settings.SECRET_KEY:
                raise exceptions.AuthenticationFailed('Invalid secret key')
            raise exceptions.AuthenticationFailed('Invalid token')
        except TokenError:
            raise exceptions.AuthenticationFailed('Token error')


def csrfToken(request):
    try:
        csrf_token = get_token(request)
        return JsonResponse({'csrfToken': csrf_token})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)