from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers, exceptions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db import transaction
from .models import Perfil, Evento, Pedido, PedidoItem
from decimal import Decimal
from django.contrib.auth.password_validation import validate_password


User = get_user_model()


class EmailOrUsernameTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer customizado para login via JWT,
    permitindo autenticação tanto por username quanto por e-mail.
    """
    # Campo extra para receber e-mail no payload de login
    email = serializers.EmailField(required=False, allow_blank=True)

    def __init__(self, *args, **kwargs):
        """
        Torna o campo username opcional para permitir login apenas com e-mail.
        """
        super().__init__(*args, **kwargs)
        self.fields[self.username_field].required = False
        if hasattr(self.fields[self.username_field], "allow_blank"):
            self.fields[self.username_field].allow_blank = True

    def validate(self, attrs):
        """
        Se o username não for enviado mas o e-mail for,
        tenta resolver o username a partir do e-mail informado.
        """
        username_field = self.username_field
        username = attrs.get(username_field)
        email = attrs.get("email")

        if not username and email:
            try:
                user = User.objects.get(email__iexact=email)
                # Preenche o username no payload para o fluxo padrão do SimpleJWT
                attrs[username_field] = getattr(user, username_field)
            except User.DoesNotExist:
                # Mantém a mensagem padrão de credenciais inválidas
                raise exceptions.AuthenticationFailed(
                    "No active account found with the given credentials"
                )

        return super().validate(attrs)


User = get_user_model()


def split_nome(nome: str):
    """
    Helper para separar um nome completo em first_name e last_name.

    - Remove espaços duplicados.
    - Se houver apenas uma palavra, é usada como first_name.
    """
    nome = " ".join((nome or "").strip().split())
    if not nome:
        return "", ""
    partes = nome.split(" ")
    if len(partes) == 1:
        return partes[0], ""
    return partes[0], " ".join(partes[1:])


class RegisterSerializer(serializers.Serializer):
    """
    Serializer responsável pelo fluxo de registro de usuário.

    Cria um User e um Perfil associado na mesma transação.
    """
    # Nome completo, opcional, usado para derivar first_name/last_name
    nome = serializers.CharField(required=False, allow_blank=True, write_only=True)

    # Dados do usuário do Django
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)

    # Campos do Perfil
    cpf = serializers.CharField(required=True, allow_blank=False)
    telefone = serializers.CharField(required=False, allow_blank=True)
    endereco = serializers.CharField(required=False, allow_blank=True)

    def validate_email(self, value):
        """
        Garante que o e-mail seja único.
        """
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("E-mail já cadastrado.")
        return value

    def validate_password(self, value):
        """
        Valida a senha usando as regras padrão de password_validation.
        """
        validate_password(value)
        return value

    def validate_cpf(self, value):
        """
        Garante que o CPF não esteja associado a outro Perfil.
        """
        if Perfil.objects.filter(cpf=value).exists():
            raise serializers.ValidationError("CPF já cadastrado.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        """
        Cria User + Perfil dentro de uma transação atômica:

        - Se 'nome' foi informado, quebra em first_name/last_name.
        - Usa e-mail como username caso username não seja informado.
        - Cria o usuário e depois o perfil associado.
        """
        nome = validated_data.pop("nome", "").strip()
        if nome:
            fn, ln = split_nome(nome)
            validated_data.setdefault("first_name", fn)
            validated_data.setdefault("last_name", ln)

        # Separa os campos que pertencem ao Perfil
        perfil_fields = {
            k: validated_data.pop(k)
            for k in ["cpf", "telefone", "endereco"]
            if k in validated_data
        }

        # Usa email como username, caso não tenha sido informado outro
        username = validated_data.get("username") or validated_data["email"]
        user = User.objects.create_user(
            username=username,
            email=validated_data["email"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            password=validated_data["password"],
        )

        # Cria ou atualiza o Perfil vinculado ao usuário
        Perfil.objects.update_or_create(
            user=user,
            defaults={
                "cpf": perfil_fields.get("cpf"),
                "telefone": perfil_fields.get("telefone") or None,
                "endereco": perfil_fields.get("endereco") or None,
            },
        )
        return user
    

class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer para troca de senha do usuário autenticado.

    Campos:
    - old_password: senha atual (obrigatória)
    - new_password: nova senha (obrigatória)
    - new_password_confirm: confirmação da nova senha (obrigatória)
    """

    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        """
        Verifica se a senha atual informada confere com a senha do usuário.
        """
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Senha atual incorreta.")
        return value

    def validate(self, attrs):
        """
        Valida se a nova senha e a confirmação coincidem
        e aplica as regras de validação de senha do Django.
        """
        new_password = attrs.get("new_password")
        new_password_confirm = attrs.get("new_password_confirm")

        if new_password != new_password_confirm:
            raise serializers.ValidationError(
                {"new_password_confirm": "A confirmação da nova senha não confere."}
            )

        # valida usando os validadores configurados no projeto
        validate_password(new_password, user=self.context["request"].user)

        return attrs

    def save(self, **kwargs):
        """
        Define a nova senha para o usuário autenticado.
        """
        user = self.context["request"].user
        new_password = self.validated_data["new_password"]
        user.set_password(new_password)
        user.save()
        return user



class PerfilSerializer(serializers.ModelSerializer):
    """
    Serializer para leitura/edição de Perfil,
    incluindo campos do usuário ('user') embutidos.
    """
    id = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(
        source="user.username", required=False, allow_blank=True
    )
    email = serializers.EmailField(
        source="user.email", required=False, allow_blank=True
    )
    first_name = serializers.CharField(
        source="user.first_name", required=False, allow_blank=True
    )
    last_name = serializers.CharField(
        source="user.last_name", required=False, allow_blank=True
    )

    class Meta:
        model = Perfil
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "cpf",
            "telefone",
            "endereco",
        ]

    def update(self, instance, validated_data):
        """
        Atualiza tanto o Perfil quanto o User relacionado, se enviado.
        """
        user_data = validated_data.pop("user", {})
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        instance.user.save()
        return super().update(instance, validated_data)

    def create(self, validated_data):
        """
        Cria um novo User + Perfil a partir do payload aninhado.

        - Define username a partir do e-mail, se não for enviado.
        - Se não vier senha, gera uma senha aleatória.
        """
        user_data = validated_data.pop("user", {})

        username = user_data.get("username") or user_data.get("email")
        if not username:
            raise serializers.ValidationError(
                {"username": "username ou email é obrigatório."}
            )

        user_data["username"] = username

        # Se não vier senha, gera uma senha aleatória
        if "password" in user_data:
            pwd = user_data.pop("password")
        else:
            from django.utils.crypto import get_random_string
            pwd = get_random_string(12)

        user = User.objects.create_user(password=pwd, **user_data)
        perfil = Perfil.objects.create(user=user, **validated_data)
        return perfil


class EventoSerializer(serializers.ModelSerializer):
    """
    Serializer padrão para o modelo Evento.
    """
    class Meta:
        model = Evento
        fields = "__all__"


class PedidoItemSerializer(serializers.ModelSerializer):
    """
    Serializer para itens de pedido.

    - evento_id: usado para escrever (FK).
    - evento_nome: usado apenas para leitura.
    """
    evento_id = serializers.PrimaryKeyRelatedField(
        queryset=Evento.objects.all(),
        source="evento",
        write_only=True,
    )
    evento_nome = serializers.CharField(
        source="evento.nome",
        read_only=True,
    )

    preco_ingresso = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True,
    )

    preco_excursao = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = PedidoItem
        fields = [
            "id",
            "evento_id",
            "evento_nome",
            "quantidade",
            "preco_ingresso",
            "preco_excursao",
            "subtotal",
        ]
        read_only_fields = ["id", "subtotal", "evento_nome"]


class PedidoSerializer(serializers.ModelSerializer):
    """
    Serializer do Pedido, incluindo uma lista de itens aninhados.

    A criação do pedido calcula o valor_total a partir dos itens.
    """
    itens = PedidoItemSerializer(many=True)

    class Meta:
        model = Pedido
        fields = [
            "id",
            "usuario",
            "status",
            "forma_pagamento",
            "valor_total",
            "observacoes",
            "criado_em",
            "itens",
        ]
        read_only_fields = [
            "id",
            "usuario",
            "status",
            "valor_total",
            "criado_em",
        ]

    def create(self, validated_data):
        """
        Cria o Pedido + seus PedidoItem(s):

        - Atribui o usuário autenticado ao pedido, se existir.
        - Usa os preços do evento como padrão caso não venham no payload.
        - Calcula subtotal de cada item e o valor_total do pedido.
        - Define status como 'pago' se houver forma_pagamento, senão 'pendente'.
        """
        itens_data = validated_data.pop("itens", [])

        # Recupera o usuário autenticado a partir do contexto da request
        request = self.context.get("request")
        user = getattr(request, "user", None)

        if user and user.is_authenticated:
            validated_data["usuario"] = user

        # Segurança: remove qualquer campo 'perfil' que venha indevidamente no payload
        validated_data.pop("perfil", None)

        pedido = Pedido.objects.create(**validated_data)

        total = Decimal("0.00")

        for item_data in itens_data:
            evento = item_data["evento"]
            quantidade = item_data.get("quantidade", 1)

            # Se o preço não for enviado, usa o preço do modelo Evento
            preco_ingresso = item_data.get("preco_ingresso")
            if preco_ingresso is None:
                preco_ingresso = evento.ingresso

            preco_excursao = item_data.get("preco_excursao")
            if preco_excursao is None:
                preco_excursao = evento.excursao

            subtotal = (preco_ingresso + preco_excursao) * quantidade

            PedidoItem.objects.create(
                pedido=pedido,
                evento=evento,
                quantidade=quantidade,
                preco_ingresso=preco_ingresso,
                preco_excursao=preco_excursao,
                subtotal=subtotal,
            )

            total += subtotal

        pedido.valor_total = total
        pedido.status = "pago" if pedido.forma_pagamento else "pendente"
        pedido.save()

        return pedido
