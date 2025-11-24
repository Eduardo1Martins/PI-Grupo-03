from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class LogoutViewTests(APITestCase):
    """
    Testes da LogoutView (endpoint /auth/logout/).

    Cobre:
    - blacklist de refresh token válido
    - comportamento com token inválido
    - ausência de campo 'refresh'.
    """

    def setUp(self):
        """
        Cria um usuário e define as URLs auxiliares:
        login, refresh e logout.
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
        self.logout_url = reverse("api_logout")

    def _get_tokens(self):
        """
        Helper para obter access/refresh via endpoint de login.

        Retorna: (access, refresh)
        """
        resp = self.client.post(
            self.login_url,
            {"username": "user1", "password": "StrongPass123!"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", resp.data)
        self.assertIn("refresh", resp.data)
        return resp.data["access"], resp.data["refresh"]

    def test_logout_com_refresh_valido_invalida_token(self):
        """
        Deve aceitar um refresh token válido, fazer logout (blacklist)
        e o mesmo refresh não pode mais ser usado no endpoint de refresh.
        """
        access, refresh = self._get_tokens()

        # autentica o cliente para passar no IsAuthenticated da LogoutView
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        # logout usando o refresh token
        response = self.client.post(
            self.logout_url,
            {"refresh": refresh},
            format="json",
        )

        # se sua view retorna 200 em vez de 205, troque para HTTP_200_OK
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

        # tentar reutilizar o mesmo refresh depois do logout deve falhar
        refresh_response = self.client.post(
            self.refresh_url,
            {"refresh": refresh},
            format="json",
        )

        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", refresh_response.data)
        self.assertIn("code", refresh_response.data)
        self.assertEqual(refresh_response.data["code"], "token_not_valid")

    def test_logout_com_refresh_invalido(self):
        """
        Refresh token inválido deve retornar 400 (erro de requisição),
        desde que o usuário esteja autenticado.
        """
        access, _ = self._get_tokens()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        response = self.client.post(
            self.logout_url,
            {"refresh": "token-totalmente-invalido"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_sem_refresh(self):
        """
        Sem o campo 'refresh' deve retornar 400
        (view acessível apenas para usuário autenticado).
        """
        access, _ = self._get_tokens()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        response = self.client.post(self.logout_url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
