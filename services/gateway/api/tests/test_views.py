"""Used for testing views.py in my application."""
import os
from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework.test import APITestCase

REGISTER_URL = os.getenv('AUTH_REGISTER_URL', 'http://localhost:8002/api/v1/users/register/')
LOGIN_URL = os.getenv('AUTH_LOGIN_URL', 'http://localhost:8002/api/v1/tokens/retrieve/')
REFRESH_URL = os.getenv('AUTH_REFRESH_URL', 'http://localhost:8002/api/v1/tokens/refresh/')
VERIFY_URL = os.getenv('AUTH_VERIFY_MFA_URL', 'http://localhost:8002/api/v1/users/verify_mfa/')
SSO_LOGIN_URL = os.getenv('AUTH_SSO_LOGIN_URL', 'http://localhost:8002/api/v1/sso/login/')
SSO_CALLBACK_URL = os.getenv('AUTH_SSO_CALLBACK_URL', 'http://localhost:8002/api/v1/sso/callback/')
CRYPTA_FETCHTREE_URL = os.getenv('CRYPTA_FETCHTREE_URL', 'http://localhost:8001/api/v1/filter_tree')
CRYPTA_FILTERRESULTS_URL = os.getenv('CRYPTA_FILTERRESULTS_URL', 'http://localhost:8001/api/v1/filter_results')

class RegisterViewTests(APITestCase):
    """Used for testing registration of users."""
    @patch('api.views.requests.post')
    def test_register_route_calls_auth_service(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.json.return_value = {'id': 1}
        mock_post.return_value = mock_response

        data = {
            'username': 'user@example.com',
            'password': 'pass',
            'email': 'user@example.com'
        }
        url = reverse('register')
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 201)
        # mock_post.assert_called_once_with(
        #     REGISTER_URL,
        #     data=data,
        # )
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], REGISTER_URL)
        flat_data = kwargs['json']
        if hasattr(flat_data, "dict"):
            flat_data = flat_data.dict()
        self.assertEqual(flat_data, data)

class LoginViewTests(APITestCase):
    """Used for testing login of users."""

    @patch('api.views.requests.post')
    def test_login_route_calls_auth_service(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.json.return_value = {'access': 'token', 'refresh': 'token'}
        mock_post.return_value = mock_response

        data = {
            'username': 'user@example.com',
            'password': 'pass'
        }
        url = reverse('login')
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], LOGIN_URL)
        flat_data = kwargs['json']
        if hasattr(flat_data, "dict"):
            flat_data = flat_data.dict()
        self.assertEqual(flat_data, data)


class TokenRefreshViewTests(APITestCase):
    """Used for testing token refresh route."""

    @patch('api.views.requests.post')
    def test_refresh_route_calls_auth_service(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.json.return_value = {'access': 'new_token'}
        mock_post.return_value = mock_response

        data = {'refresh': 'old_token'}
        url = reverse('token_refresh')
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], REFRESH_URL)
        flat_data = kwargs['json']
        if hasattr(flat_data, "dict"):
            flat_data = flat_data.dict()
        self.assertEqual(flat_data, data)


class VerifyMfaViewTests(APITestCase):
    """Used for testing MFA verification."""

    @patch('api.views.requests.post')
    def test_verify_route_calls_auth_service(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.json.return_value = {'detail': 'MFA verified'}
        mock_post.return_value = mock_response

        data = {'user_id': 1, 'otp': '123456'}
        url = reverse('verify_mfa')
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], VERIFY_URL)
        flat_data = kwargs['json']
        if hasattr(flat_data, "dict"):
            flat_data = flat_data.dict()
        try:
            flat_data['user_id'] = int(flat_data['user_id'])
        except:
            pass
        self.assertEqual(flat_data, data)

class SSOLoginViewTests(APITestCase):
    @patch('api.views.requests.get')
    def test_sso_login_proxy(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 302
        mock_response.headers = {'Content-Type': 'application/json', 'Location': 'http://microsoft'}
        mock_response.json.return_value = {'url': 'http://microsoft'}
        mock_get.return_value = mock_response

        url = reverse('sso_login')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        mock_get.assert_called_once_with(SSO_LOGIN_URL, allow_redirects=False)

class SSOCallbackViewTests(APITestCase):
    @patch('api.views.requests.get')
    def test_sso_callback_proxy(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.json.return_value = {'access': 'a', 'refresh': 'r'}
        mock_get.return_value = mock_response

        url = reverse('sso_callback')
        response = self.client.get(url, {'code': 'abc'})

        self.assertEqual(response.status_code, 200)
        mock_get.assert_called_once()

class UsersViewTests(APITestCase):
    @patch('api.views.requests.get')
    def test_users_list_calls_auth_service(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        url = reverse('users')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        mock_get.assert_called_once()

    @patch('api.views.requests.delete')
    def test_users_delete_calls_auth_service(self, mock_delete):
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_response.json.return_value = {}
        mock_delete.return_value = mock_response

        url = reverse('user-detail', args=[1])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 204)
        mock_delete.assert_called_once()

class RolesViewTests(APITestCase):
    @patch('api.views.requests.get')
    def test_roles_list_calls_auth_service(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        url = reverse('roles')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        mock_get.assert_called_once()

class RoleDetailViewTests(APITestCase):
    @patch('api.views.requests.delete')
    def test_role_delete_calls_auth_service(self, mock_delete):
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_response.json.return_value = {}
        mock_delete.return_value = mock_response

        url = reverse('role-detail', args=[1])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 204)
        mock_delete.assert_called_once()

    @patch('api.views.requests.post')
    def test_role_create_calls_auth_service(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        url = reverse('roles-create')
        response = self.client.post(url, {'name': 'r'})

        self.assertEqual(response.status_code, 201)
        mock_post.assert_called_once()

class TokensViewTests(APITestCase):
    @patch('api.views.requests.get')
    def test_tokens_list_calls_auth_service(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        url = reverse('tokens')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        mock_get.assert_called_once()

class OrganizationsViewTests(APITestCase):
    @patch('api.views.requests.get')
    def test_orgs_list_calls_auth_service(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        url = reverse('organizations')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        mock_get.assert_called_once()

class OrganizationDetailViewTests(APITestCase):
    @patch('api.views.requests.delete')
    def test_org_delete_calls_auth_service(self, mock_delete):
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_response.json.return_value = {}
        mock_delete.return_value = mock_response

        url = reverse('organization-detail', args=[1])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 204)
        mock_delete.assert_called_once()

    @patch('api.views.requests.post')
    def test_org_create_calls_auth_service(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        url = reverse('organization-detail')
        response = self.client.post(url, {'name': 'o'})

        self.assertEqual(response.status_code, 201)
        mock_post.assert_called_once()

class LoginAttemptsViewTests(APITestCase):
    @patch('api.views.requests.get')
    def test_attempts_list_calls_auth_service(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        url = reverse('login_attempts')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        mock_get.assert_called_once()

class CryptaGroupsViewTests(APITestCase):
    @patch('api.views.requests.get')
    def test_groups_list_calls_auth_service(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        url = reverse('crypta_groups')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        mock_get.assert_called_once()

class CryptaGroupDetailViewTests(APITestCase):
    @patch('api.views.requests.delete')
    def test_group_delete_calls_auth_service(self, mock_delete):
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_response.json.return_value = {}
        mock_delete.return_value = mock_response

        url = reverse('crypta_group-detail', args=[1])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 204)
        mock_delete.assert_called_once()

    @patch('api.views.requests.post')
    def test_group_create_calls_auth_service(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        url = reverse('crypta_group-detail')
        response = self.client.post(url, {'name': 'g'})

        self.assertEqual(response.status_code, 201)
        mock_post.assert_called_once()

class QueryPermissionsViewTests(APITestCase):
    @patch('api.views.requests.get')
    def test_perms_list_calls_auth_service(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        url = reverse('query_permissions')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        mock_get.assert_called_once()

class QueryPermissionDetailViewTests(APITestCase):
    @patch('api.views.requests.delete')
    def test_perm_delete_calls_auth_service(self, mock_delete):
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_response.json.return_value = {}
        mock_delete.return_value = mock_response

        url = reverse('query_permission-detail', args=[1])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 204)
        mock_delete.assert_called_once()

    @patch('api.views.requests.post')
    def test_perm_create_calls_auth_service(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        url = reverse('query_permission-detail')
        response = self.client.post(url, {'name': 'p'})

        self.assertEqual(response.status_code, 201)
        mock_post.assert_called_once()

class CryptaFilterTreeViewTests(APITestCase):
    @patch('api.views.requests.get')
    def test_crypta_filter_tree_service(self, mock_delete):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_delete.return_value = mock_response
        
        url = reverse('filter_tree')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        mock_delete.assert_called_once()

class CryptaFilterResultsViewTests(APITestCase):
    @patch('api.views.requests.get')
    def test_crypta_filter_results_service(self, mock_delete):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_delete.return_value = mock_response
        
        url = reverse('filter_tree')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        mock_delete.assert_called_once()
