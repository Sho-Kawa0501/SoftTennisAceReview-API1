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
    return JsonResponse({'csrfToken': get_token(request)})

# def refresh_get(request):
#     try:
#         RT = request.COOKIES['refresh_token']
#         if not RT:
#             return HttpResponseBadRequest("Cookie 'refresh_token' is empty or invalid.")
#         return JsonResponse({'refresh': RT})
#     except KeyError:
#         return HttpResponseBadRequest("Cookie 'refresh_token' was not found.")
#     except Exception as e:
#         print(e)
#         return HttpResponseBadRequest("An error occurred: {}".format(e))



# def refresh_get(request):
#     try:
#         RT = request.COOKIES['refresh_token']
#         return JsonResponse({'refresh': RT})
#     except Exception as e:
#         print(e)
#         return HttpResponseBadRequest("An error occurred: {}".format(e))