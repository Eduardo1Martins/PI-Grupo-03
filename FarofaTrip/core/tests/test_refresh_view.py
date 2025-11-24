from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class RefreshViewTests(APITestCase):
    """
    Testes para o endpoint de refresh de token JWT (/auth/refresh/).

    Cobre:
    - refresh bem-sucedido com token válido
    - erro com token inválido
    - erro quando o refresh token não é enviado.
    """

    def setUp(self):
        """
        Cria um usuário de teste e define as URLs de login e refresh.
        """
        self.user = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="StrongPass123!",
            first_name="User",
            last_name="One",
        )
        self.login_url = reverse("api_login")
        self.refresh_url = reverse("api_refresh")

    def _get_tokens(self):
        """Helper para obter access/refresh via endpoint de login."""
        resp = self.client.post(
            self.login_url,
            {"username": "user1", "password": "StrongPass123!"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", resp.data)
        self.assertIn("refresh", resp.data)
        return resp.data["access"], resp.data["refresh"]

    def test_refresh_token_valido_retorna_novo_access(self):
        """
        Deve aceitar um refresh token válido e retornar um novo access token.
        """
        _, refresh = self._get_tokens()

        response = self.client.post(
            self.refresh_url,
            {"refresh": refresh},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        # não garantimos se vem ou não um novo refresh (depende do SIMPLE_JWT)

    def test_refresh_token_invalido(self):
        """
        Refresh token inválido deve retornar 401 com erro de token não válido.
        """
        response = self.client.post(
            self.refresh_url,
            {"refresh": "token-totalmente-invalido"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # SimpleJWT normalmente retorna detail + code
        self.assertIn("detail", response.data)
        self.assertIn("code", response.data)
        self.assertEqual(response.data["code"], "token_not_valid")

    def test_refresh_sem_token(self):
        """
        Sem o campo 'refresh' deve retornar 400 com erro de campo obrigatório.
        """
        response = self.client.post(self.refresh_url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("refresh", response.data)
