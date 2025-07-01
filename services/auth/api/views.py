import logging
from datetime import datetime
from django.utils import timezone
from rest_framework import generics, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
import pyotp

from .models import (
    Role,
    Token,
    Organization,
    LoginAttempt,
    CryptaGroup,
    QueryPermission,
    UserProfile,
)
from .serializers import (
    UserSerializer,
    RoleSerializer,
    TokenSerializer,
    OrganizationSerializer,
    LoginAttemptSerializer,
    CryptaGroupSerializer,
    QueryPermissionSerializer,
)

logger = logging.getLogger("api")

User = get_user_model()


# Create your views here.
class LoggingTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Serializer that logs login attempts and stores issued tokens."""
    otp = serializers.CharField(required=True)

    def validate(self, attrs):
        request = self.context.get('request')
        logger.debug('Request data in tokenObtain: %s', attrs)
        logger.debug('Login attempt for %s', attrs.get('username'))
        logger.debug('User password used: %s', attrs.get('password'))
        logger.debug('OTP recieved as %s', attrs.get('otp'))
        ip_address = request.META.get('REMOTE_ADDR') if request else ''
        otp = attrs.pop('otp', None)
        username = attrs.get('username')
        user_obj = None
        if username:
            try:
                user_obj = User.objects.get(username=username)
            except User.DoesNotExist:
                user_obj = None

        try:
            data = super().validate(attrs)
        except AuthenticationFailed:
            logger.warning('Authentication failed for %s', username)
            if user_obj:
                LoginAttempt.objects.create(
                    user=user_obj,
                    time=timezone.now(),
                    successful=False,
                    ip_address=ip_address,
                )
            raise

        profile = self.user.profile
        logger.debug('Profile: %s', profile)
        totp = pyotp.TOTP(profile.mfa_secret_hash)
        logger.debug('OTP: %s', otp)
        logger.debug('TOTP: %s', totp)
        if not otp or not totp.verify(otp):
            logger.warning('Invalid OTP for %s', username)
            LoginAttempt.objects.create(
                user=self.user,
                time=timezone.now(),
                successful=False,
                ip_address=ip_address,
            )
            raise AuthenticationFailed('Invalid OTP')

        # Successful login
        logger.info('Successful login for %s', username)
        LoginAttempt.objects.create(
            user=self.user,
            time=timezone.now(),
            successful=True,
            ip_address=ip_address,
        )

        refresh = self.get_token(self.user)
        access = refresh.access_token
        
        # inject custom claims into the JWT payload
        access['username'] = self.user.username
        access['email'] = self.user.email
        # access['roles'] = [role.name for role in self.user.roles.all()]
        # access['query_permissions'] = [perm.code for perm in self.user.query_permissions.all()]

        Token.objects.create(
            user=self.user,
            token=refresh["jti"],
            type=Token.TokenType.REFRESH,
            expiration=datetime.fromtimestamp(refresh["exp"], tz=timezone.get_default_timezone())
        )

        Token.objects.create(
            user=self.user,
            token=access["jti"],
            type=Token.TokenType.ACCESS,
            expiration=datetime.fromtimestamp(access["exp"], tz=timezone.get_default_timezone()),
        )

        data["refresh"] = str(refresh)
        data["access"] = str(access)
        return data


class LoggingTokenObtainPairView(TokenObtainPairView):
    """View that uses ``LoggingTokenObtainPairSerializer``."""

    serializer_class = LoggingTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        logger.debug('Token obtain request received')
        logger.debug('Data received: %s', request.data)
        return super().post(request, *args, **kwargs)

class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        logger.debug('Received registration request')
        return super().post(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        logger.debug('Creating user %s', request.data.get('username'))
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        logger.debug('creating secret')
        secret = pyotp.random_base32()
        logger.debug('creating user profile')
        UserProfile.objects.create(
            user=user,
            name_first='',
            name_last='',
            mfa_method=UserProfile.MfaMethod.AUTHENTICATOR,
            mfa_secret_hash=secret,
            # secret_answer_1_hash='',
            # secret_answer_2_hash='',
        )
        headers = self.get_success_headers(serializer.data)
        return Response({'id': user.id, 'mfa_secret': secret}, status=status.HTTP_201_CREATED, headers=headers)

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        logger.debug('User list requested')
        response = super().get(request, *args, **kwargs)

        users = list(response.data)
        
        for user in users:
            if 'date_joined' in user and user['date_joined']:
                try:
                    user['date_joined'] = user['date_joined'].split('T')[0]
                except AtrributeError:
                    user['date_joined'] = user['date_joined'].date().isoformat()
                    
        logger.info('Returned %d users', len(response.data))
        logger.debug('Returned Data: %s', response.data)
        return Response(users)
    
class RoleListCreateView(generics.ListCreateAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        logger.debug('Role list requested')
        response = super().get(request, *args, **kwargs)
        logger.info('Returned %d roles', len(response.data))
        return response

    def post(self, request, *args, **kwargs):
        logger.debug('Create role request')
        logger.debug('Data: %s', request.data)
        return super().post(request, *args, **kwargs)


class TokenListView(generics.ListAPIView):
    queryset = Token.objects.all()
    serializer_class = TokenSerializer
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        logger.debug('Token list requested')
        response = super().get(request, *args, **kwargs)
        logger.debug('Data: %s', response.data)
        logger.info('Returned %d tokens', len(response.data))
        return response


class OrganizationListCreateView(generics.ListCreateAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        logger.debug('Organization list requested')
        response = super().get(request, *args, **kwargs)
        logger.info('Returned %d organizations', len(response.data))
        return response

    def post(self, request, *args, **kwargs):
        logger.debug('Create organization request')
        request.data['ref_location'] = int(request.data['ref_location'])
        logger.debug('Data: %s', request.data)
        return super().post(request, *args, **kwargs)


class LoginAttemptListView(generics.ListAPIView):
    queryset = LoginAttempt.objects.all()
    serializer_class = LoginAttemptSerializer
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        logger.debug('Login attempt list requested')
        response = super().get(request, *args, **kwargs)
        logger.info('Returned %d login attempts', len(response.data))
        return response



class QueryPermissionListCreateView(generics.ListCreateAPIView):
    queryset = QueryPermission.objects.all()
    serializer_class = QueryPermissionSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        logger.debug('Query permission list requested')
        response = super().get(request, *args, **kwargs)
        logger.info('Returned %d permissions', len(response.data))
        return response

    def post(self, request, *args, **kwargs):
        logger.debug('Create permission request')
        return super().post(request, *args, **kwargs)


class RoleDetailView(generics.RetrieveDestroyAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        logger.debug('Retrieve role %s', kwargs.get('pk'))
        return super().get(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        logger.debug('Delete role %s', kwargs.get('pk'))
        return super().delete(request, *args, **kwargs)


class OrganizationDetailView(generics.RetrieveDestroyAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        logger.debug('Retrieve organization %s', kwargs.get('pk'))
        return super().get(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        logger.debug('Delete organization %s', kwargs.get('pk'))
        return super().delete(request, *args, **kwargs)


class CryptaGroupListCreateView(generics.ListCreateAPIView):
    queryset = CryptaGroup.objects.all()
    serializer_class = CryptaGroupSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        logger.debug('Crypta group list requested')
        response = super().get(request, *args, **kwargs)
        logger.info('Returned %d groups', len(response.data))
        return response

    def post(self, request, *args, **kwargs):
        logger.debug('Create group request')
        return super().post(request, *args, **kwargs)


class CryptaGroupDetailView(generics.RetrieveDestroyAPIView):
    queryset = CryptaGroup.objects.all()
    serializer_class = CryptaGroupSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        logger.debug('Retrieve crypta group %s', kwargs.get('pk'))
        return super().get(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        logger.debug('Delete crypta group %s', kwargs.get('pk'))
        return super().delete(request, *args, **kwargs)


class QueryPermissionDetailView(generics.RetrieveDestroyAPIView):
    queryset = QueryPermission.objects.all()
    serializer_class = QueryPermissionSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        logger.debug('Retrieve permission %s', kwargs.get('pk'))
        return super().get(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        logger.debug('Delete permission %s', kwargs.get('pk'))
        return super().delete(request, *args, **kwargs)


class UserDetailView(generics.RetrieveDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        logger.debug('Retrieve user %s', kwargs.get('pk'))
        return super().get(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        logger.debug('Delete user %s', kwargs.get('pk'))
        return super().delete(request, *args, **kwargs)


class VerifyMfaView(generics.GenericAPIView):
    """Verify MFA OTP for a user during registration."""

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        otp = request.data.get('otp')
        logger.debug('Verify MFA for user %s', user_id)
        if not user_id or not otp:
            return Response({'detail': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=user_id)
            profile = user.profile
        except (User.DoesNotExist, UserProfile.DoesNotExist):
            logger.warning('User %s not found during MFA verify', user_id)
            return Response({'detail': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)

        totp = pyotp.TOTP(profile.mfa_secret_hash)
        if not totp.verify(otp, valid_window=1):
            logger.warning('Invalid OTP for user %s', user_id)
            return Response({'detail': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

        profile.mfa_enabled = True
        profile.mfa_verified_at = timezone.now()
        profile.save()
        logger.info('MFA verified for user %s', user_id)
        return Response({'detail': 'MFA verified'}, status=status.HTTP_200_OK)
