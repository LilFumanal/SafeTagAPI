from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from ..models.user_model import CustomUser
from ..serializers.user_serializer import CustomTokenObtainPairSerializer, UsersSerializer
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

User = CustomUser

class UserCreateView(CreateAPIView):
    """Generic View for Listing and Creating User Profiles"""

    queryset = CustomUser.objects.all()
    serializer_class = UsersSerializer
    permission_classes = [AllowAny]

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom view for JWT token generation.
    """
    serializer_class = CustomTokenObtainPairSerializer

class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom view for refreshing JWT tokens.
    """
    serializer_class = TokenRefreshSerializer
