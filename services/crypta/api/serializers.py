from rest_framework import serializers

from .models import Person, Location
from .utilities import get_query_permissions

class PermissionSerializerMixin(serializers.ModelSerializer):
    """Mixin that limits fields based on gateway-provided query permissions."""

    resource_type = None

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request")
        if not request or not self.resource_type:
            return fields
        perms = get_query_permissions(request)
        allowed = None
        for perm in perms:
            if perm.get("resource") == self.resource_type:
                allowed = perm.get("view_limits", {}).get("fields")
                break
        if allowed:
            for name in list(fields.keys()):
                if name not in allowed:
                    fields.pop(name)
        return fields

class PersonSerializer(PermissionSerializerMixin):
    resource_type = "person"

    class Meta:
        model = Person
        fields = [
            "id",
            "name_first",
            "name_last",
            "personType",
            "prefix",
            "residencyType",
        ]

class LocationSerializer(PermissionSerializerMixin):
    resource_type = "location"

    class Meta:
        model = Location
        fields = [
            "id",
            "name",
            "type",
        ]