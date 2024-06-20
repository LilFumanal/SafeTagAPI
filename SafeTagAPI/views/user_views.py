from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from ..models.user_model import CustomUser
from ..serializers.user_serializer import UsersSerializer

User = CustomUser


class UserViewSet(viewsets.ViewSet):
    """
    A viewset for user registration and profile management.
    """

    @action(detail=False, methods=["post"], permission_classes=[permissions.AllowAny])
    def register(self, request):
        """
        Custom action for user registration.
        """
        serializer = UsersSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
