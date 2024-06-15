from rest_framework import serializers
from SafeTagAPI.models.user_model import CustomUser


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["username", "email"]
