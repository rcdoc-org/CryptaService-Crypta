import os
import requests
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

logger = logging.getLogger('api')

AUTH_REGISTER_URL = os.getenv('AUTH_REGISTER_URL', 'http://localhost:8002/api/v1/user/register/')

# Create your views here.
class CreateUserView_v1(APIView):
    """Proxy user registration to the authentication service."""

    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        logger.debug('Recieved registration request')
        try:
            logger.debug('Forwarding data to auth service at %s', AUTH_REGISTER_URL)
            resp = requests.post(AUTH_REGISTER_URL, data=request.data)
            logger.info('Auth service returned status %s', resp.status_code)
            content_type = resp.headers.get('Content-Type', '')
            data = resp.json() if content_type.startswith('application/json') else resp.text
            return Response(data, status=resp.status_code)
        except requests.RequestException as exc:
            logger.error('Failed to contact auth service: %s', exc, exc_info=True)
            return Response({'detail': 'Authentication service unavailable'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
