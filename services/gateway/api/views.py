import os
import requests
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

logger = logging.getLogger('api')

AUTH_REGISTER_URL = os.getenv('AUTH_REGISTER_URL', 'http://localhost:8002/api/v1/users/register/')
AUTH_LOGIN_URL = os.getenv('AUTH_LOGIN_URL', 'http://localhost:8002/api/v1/tokens/retrieve/')
AUTH_REFRESH_URL = os.getenv('AUTH_REFRESH_URL', 'http://localhost:8002/api/v1/tokens/refresh/')
AUTH_USERS_URL = os.getenv('AUTH_USERS_URL', 'http://localhost:8002/api/v1/users/')
AUTH_ROLES_URL = os.getenv('AUTH_ROLES_URL', 'http://localhost:8002/api/v1/roles/')
AUTH_TOKENS_URL = os.getenv('AUTH_TOKENS_URL', 'http://localhost:8002/api/v1/tokens/')
AUTH_ORGS_URL = os.getenv('AUTH_ORGS_URL', 'http://localhost:8002/api/v1/organizations/')
AUTH_ATTEMPTS_URL = os.getenv('AUTH_ATTEMPTS_URL', 'http://localhost:8002/api/v1/login_attempts/')
AUTH_GROUPS_URL = os.getenv('AUTH_GROUPS_URL', 'http://localhost:8002/api/v1/crypta_groups/')
AUTH_PERMS_URL = os.getenv('AUTH_PERMS_URL', 'http://localhost:8002/api/v1/query_permissions/')
AUTH_VERIFY_MFA_URL = os.getenv('AUTH_VERIFY_MFA_URL', 'http://localhost:8002/api/v1/users/verify_mfa/')
AUTH_SSO_LOGIN_URL = os.getenv('AUTH_SSO_LOGIN_URL', 'http://localhost:8002/api/v1/sso/login/')
AUTH_SSO_CALLBACK_URL = os.getenv('AUTH_SSO_CALLBACK_URL', 'http://localhost:8002/api/v1/sso/callback/')
CRYPTA_FETCHTREE_URL = os.getenv('CRYPTA_FETCHTREE_URL', 'http://localhost:8001/api/v1/filter_tree')
CRYPTA_FILTERRESULTS_URL = os.getenv('CRYPTA_FILTERRESULTS_URL', 'http://localhost:8001/api/v1/filter_results')
CRYPTA_SEARCH_URL = os.getenv('CRYPTA_SEARCH_URL', 'http://localhost:8001/api/v1/search')

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

class UsersView_v1(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        logger.debug('Received users request')
        try:
            logger.debug('Requesting %s', AUTH_USERS_URL)
            resp = requests.get(AUTH_USERS_URL)
            logger.info('Auth Service returned status %s', resp.status_code)
            data = resp.json()
            return Response(data, status=resp.status_code)
        except requests.RequestException as exc:
            logger.error('Failed to contact auth service: %s', exc, exc_info=True)
            return Response({'detail': 'Authentication service unavailable'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    def patch(self, request, pk, *args, **kwargs):
        logger.debug('Update user %s request', pk)
        try:
            logger.debug('Requesting %s', f'{AUTH_USERS_URL}{pk}')
            resp = requests.patch(f"{AUTH_USERS_URL}{pk}/", json=request.data)
            logger.info('Auth Service returned status %s', resp.status_code)
            data = resp.json() if resp.text else ''
            return Response(data, status=resp.status_code)
        except requests.RequestException as exc:
            logger.error('Failed to contact auth service: %s', exc, exc_info=True)
            return Response({'detail': 'Authentication service unavailable'}, status = status.HTTP_503_SERVICE_UNAVAILABLE)

    def delete(self, request, pk, *args, **kwargs):
        logger.debug('Delete user %s request', pk)
        try:
            resp = requests.delete(f"{AUTH_USERS_URL}{pk}/")
            logger.info('Auth Service returned status %s', resp.status_code)
            data = resp.json() if resp.text else ''
            return Response(data, status=resp.status_code)
        except requests.RequestException as exc:
            logger.error('Failed to contact auth service: %s', exc, exc_info=True)
            return Response({'detail': 'Authentication service unavailable'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

class RolesView_v1(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        logger.debug('Received roles request')
        try:
            logger.debug('Requesting %s', AUTH_ROLES_URL)
            resp = requests.get(AUTH_ROLES_URL)
            logger.info('Auth Service returned status %s', resp.status_code)
            data = resp.json()
            return Response(data, status=resp.status_code)
        except requests.RequestException as exc:
            logger.error('Failed to contact auth service: %s', exc, exc_info=True)
            return Response({'detail': 'Authentication service unavailable'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

class RoleDetailView_v1(APIView):
    permission_classes = [permissions.AllowAny]

    def delete(self, request, pk, *args, **kwargs):
        logger.debug('Delete role %s request', pk)
        try:
            resp = requests.delete(f"{AUTH_ROLES_URL}{pk}/")
            logger.info('Auth Service returned status %s', resp.status_code)
            data = resp.json() if resp.text else ''
            return Response(data, status=resp.status_code)
        except requests.RequestException as exc:
            logger.error('Failed to contact auth service: %s', exc, exc_info=True)
            return Response({'detail': 'Authentication service unavailable'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    def post(self, request, *args, **kwargs):
        logger.debug('Create role request')
        try:
            resp = requests.post(f'{AUTH_ROLES_URL}create/', json=request.data)
            logger.info('Auth Service returned status %s', resp.status_code)
            data = resp.json() if resp.text else ''
            return Response(data, status=resp.status_code)
        except requests.RequestException as exc:
            logger.error('Failed to contact auth service: %s', exc, exc_info=True)
            return Response({'detail': 'Authentication service unavailable'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

class TokensView_v1(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        logger.debug('Received tokens request')
        try:
            logger.debug('Requesting %s', AUTH_TOKENS_URL)
            resp = requests.get(AUTH_TOKENS_URL)
            logger.info('Auth Service returned status %s', resp.status_code)
            data = resp.json()
            return Response(data, status=resp.status_code)
        except requests.RequestException as exc:
            logger.error('Failed to contact auth service: %s', exc, exc_info=True)
            return Response({'detail': 'Authentication service unavailable'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

class OrganizationsView_v1(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        logger.debug('Received organizations request')
        try:
            logger.debug('Requesting %s', AUTH_ORGS_URL)
            resp = requests.get(AUTH_ORGS_URL)
            logger.info('Auth Service returned status %s', resp.status_code)
            data = resp.json()
            return Response(data, status=resp.status_code)
        except requests.RequestException as exc:
            logger.error('Failed to contact auth service: %s', exc, exc_info=True)
            return Response({'detail': 'Authentication service unavailable'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

class OrganizationDetailView_v1(APIView):
    permission_classes = [permissions.AllowAny]

    def delete(self, request, pk, *args, **kwargs):
        logger.debug('Delete organization %s request', pk)
        try:
            resp = requests.delete(f"{AUTH_ORGS_URL}{pk}/")
            logger.info('Auth Service returned status %s', resp.status_code)
            data = resp.json() if resp.text else ''
            return Response(data, status=resp.status_code)
        except requests.RequestException as exc:
            logger.error('Failed to contact auth service: %s', exc, exc_info=True)
            return Response({'detail': 'Authentication service unavailable'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    def post(self, request, *args, **kwargs):
        logger.debug('Create organization request')
        try:
            resp = requests.post(f'{AUTH_ORGS_URL}create/', json=request.data)
            logger.info('Auth Service returned status %s', resp.status_code)
            data = resp.json() if resp.text else ''
            return Response(data, status=resp.status_code)
        except requests.RequestException as exc:
            logger.error('Failed to contact auth service: %s', exc, exc_info=True)
            return Response({'detail': 'Authentication service unavailable'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

class LoginAttemptsView_v1(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        logger.debug('Received login attempts request')
        try:
            logger.debug('Requesting %s', AUTH_ATTEMPTS_URL)
            resp = requests.get(AUTH_ATTEMPTS_URL)
            logger.info('Auth Service returned status %s', resp.status_code)
            data = resp.json()
            return Response(data, status=resp.status_code)
        except requests.RequestException as exc:
            logger.error('Failed to contact auth service: %s', exc, exc_info=True)
            return Response({'detail': 'Authentication service unavailable'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

class CryptaGroupsView_v1(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        logger.debug('Received crypta groups request')
        try:
            logger.debug('Requesting %s', AUTH_GROUPS_URL)
            resp = requests.get(AUTH_GROUPS_URL)
            logger.info('Auth Service returned status %s', resp.status_code)
            data = resp.json()
            return Response(data, status=resp.status_code)
        except requests.RequestException as exc:
            logger.error('Failed to contact auth service: %s', exc, exc_info=True)
            return Response({'detail': 'Authentication service unavailable'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

class CryptaGroupDetailView_v1(APIView):
    permission_classes = [permissions.AllowAny]

    def delete(self, request, pk, *args, **kwargs):
        logger.debug('Delete crypta group %s request', pk)
        try:
            resp = requests.delete(f"{AUTH_GROUPS_URL}{pk}/")
            logger.info('Auth Service returned status %s', resp.status_code)
            data = resp.json() if resp.text else ''
            return Response(data, status=resp.status_code)
        except requests.RequestException as exc:
            logger.error('Failed to contact auth service: %s', exc, exc_info=True)
            return Response({'detail': 'Authentication service unavailable'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    def post(self, request, *args, **kwargs):
        logger.debug('Create crypta group request')
        try:
            resp = requests.post(f'{AUTH_GROUPS_URL}create/', json=request.data)
            logger.info('Auth Service returned status %s', resp.status_code)
            data = resp.json() if resp.text else ''
            return Response(data, status=resp.status_code)
        except requests.RequestException as exc:
            logger.error('Failed to contact auth service: %s', exc, exc_info=True)
            return Response({'detail': 'Authentication service unavailable'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

class QueryPermissionsView_v1(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        logger.debug('Received query permissions request')
        try:
            logger.debug('Requesting %s', AUTH_PERMS_URL)
            resp = requests.get(AUTH_PERMS_URL)
            logger.info('Auth Service returned status %s', resp.status_code)
            data = resp.json()
            return Response(data, status=resp.status_code)
        except requests.RequestException as exc:
            logger.error('Failed to contact auth service: %s', exc, exc_info=True)
            return Response({'detail': 'Authentication service unavailable'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

class QueryPermissionDetailView_v1(APIView):
    permission_classes = [permissions.AllowAny]

    def delete(self, request, pk, *args, **kwargs):
        logger.debug('Delete query permission %s request', pk)
        try:
            resp = requests.delete(f"{AUTH_PERMS_URL}{pk}/")
            logger.info('Auth Service returned status %s', resp.status_code)
            data = resp.json() if resp.text else ''
            return Response(data, status=resp.status_code)
        except requests.RequestException as exc:
            logger.error('Failed to contact auth service: %s', exc, exc_info=True)
            return Response({'detail': 'Authentication service unavailable'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    def post(self, request, *args, **kwargs):
        logger.debug('Create query permission request')
        try:
            resp = requests.post(f'{AUTH_PERMS_URL}create/', json=request.data)
            logger.info('Auth Service returned status %s', resp.status_code)
            data = resp.json() if resp.text else ''
            return Response(data, status=resp.status_code)
        except requests.RequestException as exc:
            logger.error('Failed to contact auth service: %s', exc, exc_info=True)
            return Response({'detail': 'Authentication service unavailable'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

class VerifyMfaView_v1(APIView):
    """Proxy MFA verification to the authentication service."""

    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        logger.debug('Verify MFA request')
        try:
            logger.debug('Forwarding data to auth service at %s', AUTH_VERIFY_MFA_URL)
            resp = requests.post(AUTH_VERIFY_MFA_URL, json=request.data)
            logger.info('Auth Service returned status %s', resp.status_code)
            content_type = resp.headers.get('Content-Type', '')
            data = resp.json() if content_type.startswith('application/json') else resp.text
            return Response(data, status=resp.status_code)
        except requests.RequestException as exc:
            logger.error('Failed to contact auth service: %s', exc, exc_info=True)
            return Response({'detail': 'Authentication service unavailable'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

class SSOLoginView_v1(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        logger.debug('Proxy SSO login request')
        try:
            # Don't follow redirects so the frontend can handle them
            resp = requests.get(AUTH_SSO_LOGIN_URL, allow_redirects=False)
            logger.info('Auth Service returned status %s', resp.status_code)
            data = resp.json() if resp.headers.get('Content-Type', '').startswith('application/json') else resp.text
            headers = {}
            if 'Location' in resp.headers:
                headers['Location'] = resp.headers['Location']
            return Response(data, status=resp.status_code, headers=headers)
        except requests.RequestException as exc:
            logger.error('Failed to contact auth service: %s', exc, exc_info=True)
            return Response({'detail': 'Authentication service unavailable'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

class SSOCallbackView_v1(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        logger.debug('Proxy SSO callback request')
        try:
            resp = requests.get(AUTH_SSO_CALLBACK_URL, params=request.query_params)
            logger.info('Auth Service returned status %s', resp.status_code)
            data = resp.json() if resp.headers.get('Content-Type', '').startswith('application/json') else resp.text
            return Response(data, status=resp.status_code)
        except requests.RequestException as exc:
            logger.error('Failed to contact auth service: %s', exc, exc_info=True)
            return Response({'detail': 'Authentication service unavailable'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

class FilterTreeView_v1(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, *args, **kwargs):
        logger.debug('Filter Tree request recieved.')

        try:
            logger.debug('Forwarding fetch request to crypta service at %s', CRYPTA_FETCHTREE_URL)
            resp = requests.get(CRYPTA_FETCHTREE_URL, params=request.query_params)
            logger.info('Crypta Service returned status %s', resp.status_code)
            content_type = resp.headers.get('Content-Type', '')
            data = resp.json() if content_type.startswith('application/json') else resp.text
            return Response(data, status=resp.status_code)
        except requests.RequestException as exc:
            logger.error('Failed to contact crypta service: %s', exc, exc_info=True)
            return Response({'detail': 'Crypta Service unavailable'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

class FilterResultsView_v1(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, *args, **kwargs):
        logger.debug('Filter Results request recieved.')

        try:
            logger.debug('Forwarding fetch request to crypta service at %s', CRYPTA_FILTERRESULTS_URL)
            resp = requests.get(CRYPTA_FILTERRESULTS_URL, params=request.query_params)
            logger.info('Crypta Service returned status %s', resp.status_code)
            content_type = resp.headers.get('Content-Type', '')
            data = resp.json() if content_type.startswith('application/json') else resp.text
            return Response(data, status=resp.status_code)
        except requests.RequestException as exc:
            logger.error('Failed to contact crypta service: %s', exc, exc_info=True)
            return Response({'detail': 'Crypta service unavailable'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

class SearchResultsView_v1(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, *args, **kwargs):
        logger.debug('Search Results request recieved.')
        try:
            logger.debug('Forwarding search request to crypta service at %s', CRYPTA_SEARCH_URL)
            resp = requests.get(CRYPTA_SEARCH_URL, params=request.query_params)
            logger.info('Crypta Service returned status %s', resp.status_code)
            content_type = resp.headers.get('Content-Type', '')
            data = resp.json() if content_type.startswith('application/json') else resp.text
            return Response(data, status=resp.status_code)
        except requests.RequestException as exc:
            logger.error('Failed to contact crypta service: %s', exc, exc_info=True)
            return Response({'detail': 'Crypta service unavailable'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
