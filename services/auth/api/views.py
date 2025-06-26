import logging
from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import ( 
    User,
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


# Create your views here.
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
    
class RoleListView(generics.ListAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [AllowAny]


class TokenListView(generics.ListAPIView):
    queryset = Token.objects.all()
    serializer_class = TokenSerializer
    permission_classes = [AllowAny]


class OrganizationListView(generics.ListAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [AllowAny]


class LoginAttemptListView(generics.ListAPIView):
    queryset = LoginAttempt.objects.all()
    serializer_class = LoginAttemptSerializer
    permission_classes = [AllowAny]


class CryptaGroupListView(generics.ListAPIView):
    queryset = CryptaGroup.objects.all()
    serializer_class = CryptaGroupSerializer
    permission_classes = [AllowAny]


class QueryPermissionListView(generics.ListAPIView):
    queryset = QueryPermission.objects.all()
    serializer_class = QueryPermissionSerializer
    permission_classes = [AllowAny]