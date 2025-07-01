from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
import pyotp

from api.models import Role, Organization, CryptaGroup, QueryPermission, User, UserProfile

class DetailViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", email="t@e.com", password="pass")
        UserProfile.objects.create(user=self.user, name_first="", name_last="", mfa_secret_hash=pyotp.random_base32())
        self.role = Role.objects.create(name="role")
        self.org = Organization.objects.create(name="org", ref_location_id=1)
        self.group = CryptaGroup.objects.create(name="group", description="d")
        self.permission = QueryPermission.objects.create(
            group=self.group,
            resource_type=QueryPermission.ResourceType.PERSON,
            access_type=QueryPermission.AccessType.READ,
            view_limits={},
            filter_conditions={},
        )

    def test_role_detail_get_delete(self):
        url = reverse("role-detail", args=[self.role.pk])
        self.client.force_authenticate(self.user)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_org_detail_get_delete(self):
        url = reverse("organization-detail", args=[self.org.pk])
        self.client.force_authenticate(self.user)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_group_detail_get_delete(self):
        url = reverse("crypta-group-detail", args=[self.group.pk])
        self.client.force_authenticate(self.user)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_permission_detail_get_delete(self):
        url = reverse("query-permission-detail", args=[self.permission.pk])
        self.client.force_authenticate(self.user)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_detail_get_delete(self):
        url = reverse("user-detail", args=[self.user.pk])
        admin_user = User.objects.create_user(username="admin", email="admin@example.com", password="pass")
        self.client.force_authenticate(admin_user)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

class VerifyMfaViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", email="t@e.com", password="pass")
        secret = pyotp.random_base32()
        self.profile = UserProfile.objects.create(
            user=self.user,
            name_first="test",
            name_last="user",
            mfa_secret_hash=secret,
        )
        self.user.refresh_from_db()

    def test_verify_mfa(self):
        totp = pyotp.TOTP(self.profile.mfa_secret_hash)
        url = reverse("verify-mfa")
        data = {"user_id": self.user.id, "otp": totp.now()}
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

class MicrosoftCallbackViewTests(APITestCase):
    def test_callback_creates_user(self):
        with patch('api.views.msal.ConfidentialClientApplication') as mock_app:
            instance = mock_app.return_value
            instance.acquire_token_by_authorization_code.return_value = {
                'id_token_claims': {
                    'oid': '123',
                    'preferred_username': 'user@example.com',
                    'given_name': 'Test',
                    'family_name': 'User',
                    'department': 'IT',
                }
            }
            url = reverse('sso-callback')
            resp = self.client.get(url, {'code': 'abc'})
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            self.assertTrue(User.objects.filter(sso_id='123').exists())
