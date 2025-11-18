from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class LoginViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="StrongPass123!",
            first_name="User",
            last_name="One",
        )
        self.url = reverse("api_login")

    def test_login_com_username(self):
        """Deve logar com username e password válidos, retornando access e refresh."""
        data = {
            "username": "user1",
            "password": "StrongPass123!",
        }
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_com_email(self):
        """Deve logar usando apenas email + password."""
        data = {
            "email": "user1@example.com",
            "password": "StrongPass123!",
        }
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_com_email_case_insensitive(self):
        """Email deve ser tratado de forma case-insensitive (email__iexact)."""
        data = {
            "email": "USER1@EXAMPLE.COM",
            "password": "StrongPass123!",
        }
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_email_inexistente(self):
        """Email inexistente deve retornar 401 com mensagem de credenciais inválidas."""
        data = {
            "email": "naoexiste@example.com",
            "password": "qualquercoisa",
        }
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # mensagem definida no EmailOrUsernameTokenObtainPairSerializer
        self.assertEqual(
            response.data.get("detail"),
            "No active account found with the given credentials",
        )

    def test_login_senha_incorreta(self):
        """Senha incorreta deve retornar 401 com mensagem de credenciais inválidas."""
        data = {
            "email": "user1@example.com",
            "password": "SenhaErrada",
        }
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data.get("detail"),
            "No active account found with the given credentials",
        )

    def test_login_sem_credenciais(self):
        """
        Sem username/email ou password:
        deve retornar 400 com erro de campo obrigatório (password).
        """
        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # TokenObtainPairSerializer exige password
        self.assertIn("password", response.data)
