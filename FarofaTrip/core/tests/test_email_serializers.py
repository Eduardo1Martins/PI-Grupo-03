from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from core.serializers import EmailOrUsernameTokenObtainPairSerializer

User = get_user_model()

class EmailOrUsernameTokenObtainPairSerializerTestCase(TestCase):
    def setUp(self):
        self.password = "SenhaSegura123"
        self.user = User.objects.create_user(
            username="usuario_teste",
            email="teste@example.com",
            password=self.password
        )

    def test_login_with_username_should_succeed(self):
        """
        Cenário Padrão: O usuário fornece o username correto e senha.
        O serializer deve se comportar como o padrão e retornar os tokens.
        """
        data = {
            "username": "usuario_teste",
            "password": self.password
        }
        
        serializer = EmailOrUsernameTokenObtainPairSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        # O método validate do TokenObtainPairSerializer retorna um dict com 'access' e 'refresh'
        result = serializer.validated_data
        self.assertIn("access", result)
        self.assertIn("refresh", result)

    def test_login_with_email_should_succeed(self):
        """
        Cenário Customizado: O usuário deixa o username vazio, mas fornece o e-mail.
        O serializer deve buscar o username pelo e-mail e autenticar.
        """
        data = {
            "username": "",  # Simulando campo vazio vindo do front
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
        Verifica se o login funciona mesmo se o e-mail for enviado com letras maiúsculas
        (visto que o código usa email__iexact).
        """
        data = {
            "email": "TESTE@Example.com", # E-mail misturado
            "password": self.password
        }
        
        serializer = EmailOrUsernameTokenObtainPairSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        result = serializer.validated_data
        self.assertIn("access", result)

    def test_login_should_fail_with_wrong_password(self):
        """
        Deve levantar AuthenticationFailed se a senha estiver incorreta,
        seja usando e-mail ou username.
        """
        data = {
            "email": "teste@example.com",
            "password": "senha_errada"
        }
        
        serializer = EmailOrUsernameTokenObtainPairSerializer(data=data)
        
        # O método validate() do SimpleJWT lança exceção se a auth falhar
        with self.assertRaises(AuthenticationFailed):
             # is_valid chama run_validation -> validate
            if serializer.is_valid():
                 _ = serializer.validated_data

    def test_login_should_fail_with_non_existent_email(self):
        """
        Se o e-mail não existe, o serializer não consegue preencher o username,
        e a autenticação subsequente deve falhar.
        """
        data = {
            "email": "naoexiste@example.com",
            "password": "qualquer_senha"
        }
        
        serializer = EmailOrUsernameTokenObtainPairSerializer(data=data)
        
        # Dependendo da versão do SimpleJWT, pode falhar na validação ou na autenticação.
        # Geralmente lança AuthenticationFailed("No active account found with the given credentials")
        with self.assertRaises(AuthenticationFailed):
            if serializer.is_valid():
                 _ = serializer.validated_data