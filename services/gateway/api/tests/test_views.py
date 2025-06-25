"""Used for testing views.py in my application."""
import os
from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework.test import APITestCase

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
            'username': 'testuser',
            'password': 'pass',
            'email': 'user@example.com'
        }
        url = reverse('register')
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 201)
        mock_post.assert_called_once_with(
            os.getenv('AUTH_REGISTER_URL', 'http://localhost:8002/api/v1/user/register/'),
            data=data,
        )
