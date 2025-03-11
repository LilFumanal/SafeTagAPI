from rest_framework import serializers
from SafeTagAPI.models.user_model import CustomUser


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["username", "email"]
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}
    
    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user