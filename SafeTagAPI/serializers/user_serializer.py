from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from SafeTagAPI.models.user_model import CustomUser


class UsersSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )
    
    class Meta:
        model = CustomUser
        fields = ["email","password"]
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 5},
            'username': {'read_only': True}  # Le username est en lecture seule
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser.objects.create_user(password=password,**validated_data)
        user.save()
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = CustomUser.USERNAME_FIELD

    def validate(self, attrs):
        credentials = {
            'email': attrs.get('email'),
            'password': attrs.get('password')
        }
        try:
            user = CustomUser.objects.filter(email=credentials['email']).first()
            if user:
                print(f"Utilisateur trouvé : {user.email}")
                if user.check_password(credentials['password']):
                    print("Mot de passe correct")
                    if not user.is_active:
                        raise serializers.ValidationError("Ce compte est désactivé.")
                    refresh = RefreshToken.for_user(user)
                    data = {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'username': user.username
                    }
                    return data
                else:
                    print("Mot de passe incorrect")
                    raise serializers.ValidationError("Mot de passe incorrect")
            else:
                print("Utilisateur non trouvé")
                raise serializers.ValidationError("Utilisateur non trouvé")
        except Exception as e:
            print(f"Erreur lors de la validation : {e}")
            raise serializers.ValidationError("Erreur lors de la validation")

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        refresh = RefreshToken(attrs['refresh'])

        data = {'access': str(refresh.access_token)}

        # Ajout de l'email de l'utilisateur dans la réponse
        user = CustomUser.objects.get(id=refresh['user_id'])
        data['email'] = user.email

        return data