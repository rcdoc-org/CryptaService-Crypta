from django.test import TestCase
from api.models import Person
from api.views import _apply_permission_filters

class ApplyPermissionFiltersTests(TestCase):
    def test_permission_on_related_resource(self):
        person = Person.objects.create(
            personType='lay',
            name_first='Jane',
            name_last='Doe',
        )
        perms = [
            {
                'resource': 'person_email',
                'filters': {},
            }
        ]
        qs = Person.objects.all()
        filtered = _apply_permission_filters(qs, perms, 'person')
        self.assertQuerySetEqual(filtered, [person], transform=lambda x: x)
