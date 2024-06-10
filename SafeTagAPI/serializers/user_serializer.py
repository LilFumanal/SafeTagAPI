from rest_framework import serializers
from ..models.user_model import User

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
