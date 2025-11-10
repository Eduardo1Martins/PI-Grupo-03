from rest_framework import serializers
from .models import Usuario
from .models import Evento
from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField(required=False)  
    password = serializers.CharField(write_only=True, trim_whitespace=False, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop(self.username_field, None)
        if "password" in self.fields:
            self.fields["password"].required = False

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError('E-mail e senha são obrigatórios.')

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('E-mail não encontrado.')
        except User.MultipleObjectsReturned:
            raise serializers.ValidationError('Há mais de um usuário com este e-mail. Contate o suporte.')

        user_ok = authenticate(self.context.get('request'),
                               username=user.get_username(),
                               password=password)
        if user_ok is None:
            raise serializers.ValidationError('Credenciais inválidas.')

        data = super().validate({'username': user_ok.get_username(), 'password': password})

        data['user'] = {
            'id': user_ok.id,
            'username': user_ok.get_username(),
            'email': user_ok.email,
            'first_name': user_ok.first_name,
            'last_name': user_ok.last_name,
        }
        return data


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'


class EventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evento
        fields = '__all__'