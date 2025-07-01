from django.test import TestCase
from api.models import User, UserProfile

class UserModelTests(TestCase):
    def test_create_user_with_sso(self):
        user = User.objects.create_user(username='u', email='u@example.com', password='x', sso_id='123')
        self.assertEqual(user.sso_id, '123')
    
class UserProfileModelTests(TestCase):
    def test_department_field(self):
        user = User.objects.create_user(username='u2', email='u2@example.com', password='x')
        profile = UserProfile.objects.create(user=user, name_first='', name_last='', mfa_secret_hash='', secret_answer_1_hash='', secret_answer_2_hash='', department='IT')
        self.assertEqual(profile.department, 'IT')
