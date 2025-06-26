from rest_framework import serializers
from . import models

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = '__all__'

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserProfile
        fields = '__all__'


class LoginAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LoginAttempt
        fields = '__all__'


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Organization
        fields = '__all__'


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Role
        fields = '__all__'


class UserOrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserOrganization
        fields = '__all__'


class CryptaGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CryptaGroup
        fields = '__all__'


class UserCryptaGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserCryptaGroup
        fields = '__all__'


class QueryPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.QueryPermission
        fields = '__all__'


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Feature
        fields = '__all__'


class RoleFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RoleFeature
        fields = '__all__'


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Token
        fields = '__all__'


class OrganizationFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OrganizationFeature
        fields = '__all__'


class PasswordResetSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PasswordReset
        fields = '__all__'


class UserStatusLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserStatusLog
        fields = '__all__'
