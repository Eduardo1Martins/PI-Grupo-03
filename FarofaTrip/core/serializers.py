from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db import transaction
from .models import Perfil, Evento

User = get_user_model()

class EmailOrUsernameTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField(required=False, allow_blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field].required = False
        if hasattr(self.fields[self.username_field], "allow_blank"):
            self.fields[self.username_field].allow_blank = True

    def validate(self, attrs):
        username_field = self.username_field
        username = attrs.get(username_field)
        email = attrs.get("email")

        if not username and email:
            try:
                user = User.objects.get(email__iexact=email)
                attrs[username_field] = getattr(user, username_field)
            except User.DoesNotExist:
                pass

        return super().validate(attrs)


User = get_user_model()

def split_nome(nome: str):
    nome = " ".join((nome or "").strip().split())
    if not nome:
        return "", ""
    partes = nome.split(" ")
    if len(partes) == 1:
        return partes[0], ""                
    return partes[0], " ".join(partes[1:]) 

class RegisterSerializer(serializers.Serializer):
    
    nome = serializers.CharField(required=False, allow_blank=True, write_only=True)

    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)

    cpf = serializers.CharField(required=True, allow_blank=False)
    telefone = serializers.CharField(required=False, allow_blank=True)
    endereco = serializers.CharField(required=False, allow_blank=True)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("E-mail já cadastrado.")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value
    
    def validate_cpf(self, value):
        if Perfil.objects.filter(cpf=value).exists():
            raise serializers.ValidationError("CPF já cadastrado.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        nome = validated_data.pop("nome", "").strip()
        if nome:
            fn, ln = split_nome(nome)
            validated_data.setdefault("first_name", fn)
            validated_data.setdefault("last_name", ln)

        perfil_fields = {k: validated_data.pop(k) for k in ["cpf", "telefone", "endereco"] if k in validated_data}

        username = validated_data.get("username") or validated_data["email"]
        user = User.objects.create_user(
            username=username,
            email=validated_data["email"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            password=validated_data["password"],
        )

        Perfil.objects.update_or_create(
            user=user,
            defaults={
                "cpf": perfil_fields.get("cpf"),
                "telefone": perfil_fields.get("telefone") or None,
                "endereco": perfil_fields.get("endereco") or None,
            },
        )
        return user


class PerfilSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", required=False, allow_blank=True)
    email = serializers.EmailField(source="user.email", required=False, allow_blank=True)
    first_name = serializers.CharField(source="user.first_name", required=False, allow_blank=True)
    last_name = serializers.CharField(source="user.last_name", required=False, allow_blank=True)

    class Meta:
        model = Perfil
        fields = [
            "id", "username", "email", "first_name", "last_name",
            "cpf", "telefone", "endereco",
        ]

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        instance.user.save()
        return super().update(instance, validated_data)

    def create(self, validated_data):
        user_data = validated_data.pop("user", {})
        username = user_data.get("username") or user_data.get("email")
        if not username:
            raise serializers.ValidationError({"username": "username ou email é obrigatório."})

        if "password" in user_data:
            pwd = user_data.pop("password")
        else:
            from django.utils.crypto import get_random_string
            pwd = get_random_string(12)

        user = User.objects.create_user(password=pwd, **user_data, username=username)
        perfil = Perfil.objects.create(user=user, **validated_data)
        return perfil


class EventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evento
        fields = "__all__"
