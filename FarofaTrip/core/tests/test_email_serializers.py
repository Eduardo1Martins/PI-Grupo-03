from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from core.serializers import EmailOrUsernameTokenObtainPairSerializer

# Atalho para o modelo de usuário configurado no projeto
User = get_user_model()


class EmailOrUsernameTokenObtainPairSerializerTestCase(TestCase):
    """
    Testes do serializer customizado de login (JWT) que aceita username ou e-mail.
    """

    def setUp(self):
        """
        Cria um usuário de teste para ser usado em todos os cenários.
        """
        self.password = "SenhaSegura123"
        self.user = User.objects.create_user(
            username="usuario_teste",
            email="teste@example.com",
            password=self.password
        )

    def test_login_with_username_should_succeed(self):
        """
        Cenário padrão:
        - Usuário envia username + senha corretos.
        - Deve receber tokens 'access' e 'refresh'.
        """
        data = {
            "username": "usuario_teste",
            "password": self.password
        }

        # Instancia o serializer com os dados de login
        serializer = EmailOrUsernameTokenObtainPairSerializer(data=data)

        # is_valid executa a validação interna (incluindo authenticate)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        # validated_data deve conter os tokens gerados pelo SimpleJWT
        result = serializer.validated_data
        self.assertIn("access", result)
        self.assertIn("refresh", result)

    def test_login_with_email_should_succeed(self):
        """
        Cenário customizado:
        - Usuário envia e-mail + senha, deixando username vazio.
        - O serializer deve resolver o username pelo e-mail e autenticar.
        """
        data = {
            "username": "",  # Simula envio de campo vazio pelo front
            "email": "teste@example.com",
            "password": self.password
        }

        serializer = EmailOrUsernameTokenObtainPairSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        result = serializer.validated_data
        self.assertIn("access", result)
        self.assertIn("refresh", result)

    def test_login_with_email_case_insensitive(self):
        """
        Verifica se o login funciona mesmo com e-mail em caixa alta/mista,
        já que o código usa filtro email__iexact.
        """
        data = {
            "email": "TESTE@Example.com",  # E-mail com maiúsculas
            "password": self.password
        }

        serializer = EmailOrUsernameTokenObtainPairSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        result = serializer.validated_data
        self.assertIn("access", result)

    def test_login_should_fail_with_wrong_password(self):
        """
        Se a senha estiver errada, o serializer deve lançar AuthenticationFailed.
        """
        data = {
            "email": "teste@example.com",
            "password": "senha_errada"
        }

        serializer = EmailOrUsernameTokenObtainPairSerializer(data=data)

        # validate() deve disparar AuthenticationFailed em caso de falha
        with self.assertRaises(AuthenticationFailed):
            # is_valid chama run_validation -> validate
            if serializer.is_valid():
                _ = serializer.validated_data

    def test_login_should_fail_with_non_existent_email(self):
        """
        Se o e-mail não existir, o serializer não encontra o usuário
        e deve lançar AuthenticationFailed.
        """
        data = {
            "email": "naoexiste@example.com",
            "password": "qualquer_senha"
        }

        serializer = EmailOrUsernameTokenObtainPairSerializer(data=data)

        # Para e-mail inexistente, o fluxo também resulta em AuthenticationFailed
        with self.assertRaises(AuthenticationFailed):
            if serializer.is_valid():
                _ = serializer.validated_data
