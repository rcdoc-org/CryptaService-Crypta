import logging
from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import User
from .serializers import UserSerializer

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