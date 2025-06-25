"""Used for testing views.py in my application."""
import os
from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework.test import APITestCase

REGISTER_URL = os.getenv('AUTH_REGISTER_URL', 'http://localhost:8002/api/v1/user/register/')
LOGIN_URL = os.getenv('AUTH_LOGIN_URL', 'http://localhost:8002/api/v1/token/')
REFRESH_URL = os.getenv('AUTH_REFRESH_URL', 'http://localhost:8002/api/v1/token/refresh/')

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
        flat_data = {k: v[0] if isinstance(v, list) else v for k, v in kwargs['data'].items()}
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
        flat_data = {k: v[0] if isinstance(v, list) else v for k, v in kwargs['data'].items()}
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
        flat_data = {k: v[0] if isinstance(v, list) else v for k, v in kwargs['data'].items()}
        self.assertEqual(flat_data, data)