from rest_framework import serializers
from .models import Usuario
from .models import Evento
from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction

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
    
User = get_user_model()

class RegisterSerializer(serializers.Serializer):
    # Campos do auth.User
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    last_name  = serializers.CharField(required=False, allow_blank=True, max_length=150)
    email      = serializers.EmailField()
    password   = serializers.CharField(write_only=True, trim_whitespace=False)

    # Campos opcionais do domínio Usuario
    nome     = serializers.CharField(required=False, allow_blank=True, max_length=100)
    cpf      = serializers.CharField(required=False, allow_blank=True, max_length=14)
    telefone = serializers.CharField(required=False, allow_blank=True, max_length=15)
    endereco = serializers.CharField(required=False, allow_blank=True, max_length=255)

    def validate_email(self, value):
        email = (value or "").strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("Já existe um usuário com este e-mail.")
        return email

    def validate_password(self, value):
        validate_password(value)
        return value

    @transaction.atomic
    def create(self, validated_data):
        # separa campos do domínio "Usuario"
        usuario_fields = {k: validated_data.pop(k, None) for k in ("nome", "cpf", "telefone", "endereco")}
        password = validated_data.pop("password")
        email = validated_data.pop("email").strip().lower()

        # cria o usuário usando o e-mail como username
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            **validated_data  # first_name / last_name se enviados
        )

        # cria Usuario **somente** se CPF for informado (é unique e obrigatório no seu model)
        from .models import Usuario
        cpf = (usuario_fields.get("cpf") or "").strip()
        if cpf:
            nome = (usuario_fields.get("nome") or "").strip()
            if not nome:
                nome = f"{user.first_name} {user.last_name}".strip() or email
            Usuario.objects.create(
                nome=nome,
                cpf=cpf,
                telefone=(usuario_fields.get("telefone") or None),
                endereco=(usuario_fields.get("endereco") or None),
            )

        return user

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'


class EventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evento
        fields = '__all__'