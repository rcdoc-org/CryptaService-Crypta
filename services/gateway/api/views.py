import os
import requests
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

logger = logging.getLogger('api')

AUTH_REGISTER_URL = os.getenv('AUTH_REGISTER_URL', 'http://localhost:8002/api/v1/user/register/')
AUTH_LOGIN_URL = os.getenv('AUTH_LOGIN_URL', 'http://localhost:8002/api/v1/token/')
AUTH_REFRESH_URL = os.getenv('AUTH_REFRESH_URL', 'http://localhost:8002/api/v1/token/refresh/')

# Create your views here.
class CreateUserView_v1(APIView):
    """Proxy user registration to the authentication service."""

    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        """Tries to pass off the registration attempt to the auth service.
        And catches errors if they occur and sends a 503 in response."""
        logger.debug('Recieved registration request')
        try:
            logger.debug('Forwarding data to auth service at %s', AUTH_REGISTER_URL)
            logger.debug('data: %s', request.data)
            resp = requests.post(AUTH_REGISTER_URL, json=request.data)
            logger.info('Auth service returned status %s', resp.status_code)
            content_type = resp.headers.get('Content-Type', '')
            data = resp.json() if content_type.startswith('application/json') else resp.text
            return Response(data, status=resp.status_code)
        except requests.RequestException as exc:
            logger.error('Failed to contact auth service: %s', exc, exc_info=True)
            return Response({'detail': 'Authentication service unavailable'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

class LoginView_v1(APIView):
    """Proxy user login to the authentication service."""

    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        """Tries to pass off the login attempt to the auth service.
        And catches errors if they occur and sends a 503 in response."""
        logger.debug('Received login request')
        try:
            logger.debug('Forwarding data to auth service at %s', AUTH_LOGIN_URL)
            logger.debug('data: %s', request.data)
            resp = requests.post(AUTH_LOGIN_URL, json=request.data)
            logger.info('Auth Service returned status %s', resp.status_code)
            content_type = resp.headers.get('Content-Type', '')
            data = resp.json() if content_type.startswith('application/json') else resp.text
            return Response(data, status=resp.status_code)
        except requests.RequestException as exc:
            logger.error('Failed to contact auth service: %s', exc, exc_info=True)
            return Response(
                {'detail': 'Authentication service unavailable'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
                )

class TokenRefreshView_v1(APIView):
    """Proxy token refresh to the authentication service."""

    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        """Tries to pass off the token refresh attempt to the auth service.
        And catches errors if they occur and sends a 503 in response."""
        logger.debug('Received token refresh request')
        try:
            logger.debug('Forwarding data to auth service at %s', AUTH_REFRESH_URL)
            logger.debug('data %s', request.data)
            resp = requests.post(AUTH_REFRESH_URL, json=request.data)
            logger.info('Auth Service returned status %s', resp.status_code)
            content_type = resp.headers.get('Content-Type', '')
            data = resp.json() if content_type.startswith('application/json') else resp.text
            return Response(data, status=resp.status_code)
        except requests.RequestException as exc:
            logger.error('Failed to contact auth service: %s', exc, exc_info=True)
            return Response(
                {'detail': 'Authentication service unavailable'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
