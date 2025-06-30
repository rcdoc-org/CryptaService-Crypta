import logging
from datetime import datetime
from django.utils import timezone
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model

from .models import ( 
    Role,
    Token,
    Organization,
    LoginAttempt,
    CryptaGroup,
    QueryPermission,
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

    def validate(self, attrs):
        request = self.context.get('request')
        ip_address = request.META.get('REMOTE_ADDR') if request else ''
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
            if user_obj:
                LoginAttempt.objects.create(
                    user=user_obj,
                    time=timezone.now(),
                    successful=False,
                    ip_address=ip_address,
                )
            raise

        # Successful login
        LoginAttempt.objects.create(
            user=self.user,
            time=timezone.now(),
            successful=True,
            ip_address=ip_address,
        )

        refresh = self.get_token(self.user)
        access = refresh.access_token

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

class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        logger.debug('Received registration request')
        return super().post(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        logger.debug('Creating user %s', request.data.get('username'))
        return super().create(request, *args, **kwargs)

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


class OrganizationDetailView(generics.RetrieveDestroyAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [AllowAny]


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


class QueryPermissionDetailView(generics.RetrieveDestroyAPIView):
    queryset = QueryPermission.objects.all()
    serializer_class = QueryPermissionSerializer
    permission_classes = [AllowAny]


class UserDetailView(generics.RetrieveDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
