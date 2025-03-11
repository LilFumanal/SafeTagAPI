from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from ..models.user_model import CustomUser
from ..serializers.user_serializer import UsersSerializer

User = CustomUser

class UserView(ListCreateAPIView):
    """Generic View for Listing and Creating User Profiles"""

    queryset = CustomUser.objects.all()
    serializer_class = UsersSerializer
    permission_classes = [AllowAny]

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user


# class CustomTokenObtainPairView(TokenObtainPairView):
#     """
#     Custom view for JWT token generation.
#     """
#     serializer_class = CustomTokenObtainPairSerializer

# class CustomTokenRefreshView(TokenRefreshView):
#     """
#     Custom view for refreshing JWT tokens.
#     """
#     serializer_class = CustomTokenObtainPairSerializer
