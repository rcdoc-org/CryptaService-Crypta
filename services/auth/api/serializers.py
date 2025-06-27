from rest_framework import serializers
# from django.contrib.auth import get_user_model
from . import models

# User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = models.User
        fields = ['id','username','email', 'password']
    
    # def create(self, validated_data):
    #     user = User (
    #         username = validated_data['email'],
    #         email=validated_data['email']
    #     )
    #     user.set_password(validated_data['password'])
    #     user.save()
    #     return user
    def create(self, validated_data):
        password = validated_data.pop('password')
        # validated_data['password_hash'] = make_password(password)
        # return super().create(validated_data)
        user = models.User(**validated_data)
        user.set_password(password)
        user.save()
        return user

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
