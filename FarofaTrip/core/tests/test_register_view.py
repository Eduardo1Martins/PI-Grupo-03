from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Perfil

User = get_user_model()


class RegisterViewTests(APITestCase):
    """
    Testes de integração para o endpoint de registro (/auth/register/).

    Cobre:
    - criação bem-sucedida de User + Perfil
    - validação de e-mail duplicado
    - validação de CPF duplicado
    - validação de senha fraca
    - payload incompleto.
    """

    def setUp(self):
        """
        Define a URL de registro e um payload base válido.
        """
        self.url = reverse("api_register")

        # payload base VÁLIDO de acordo com o RegisterSerializer (campos planos)
        self.valid_payload = {
            "nome": "User One",  # opcional, mas ajuda a cobrir o split_nome
            "username": "user1",
            "email": "user1@example.com",
            "first_name": "User",
            "last_name": "One",
            "password": "StrongPass123!",

            "cpf": "12345678910",
            "telefone": "11999999999",
            "endereco": "Rua de Teste, 123",
        }

    def test_register_sucesso_cria_user_e_perfil(self):
        """
        POST válido deve criar um User e um Perfil associados.
        """
        resp = self.client.post(self.url, self.valid_payload, format="json")

        # RegisterView SEMPRE retorna 201_CREATED
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Um usuário e um perfil devem ter sido criados
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Perfil.objects.count(), 1)

        perfil = Perfil.objects.first()
        self.assertIsNotNone(perfil)
        self.assertEqual(perfil.cpf, self.valid_payload["cpf"])
        self.assertEqual(perfil.user.email, self.valid_payload["email"])
        self.assertEqual(perfil.user.username, self.valid_payload["username"])

        # resposta deve conter dados básicos do user
        self.assertIn("user", resp.data)
        self.assertEqual(resp.data["user"]["email"], self.valid_payload["email"])
        self.assertEqual(resp.data["user"]["username"], self.valid_payload["username"])

    def test_register_email_duplicado_retorna_400(self):
        """
        Não deve permitir cadastrar outro usuário com o mesmo email.
        """
        # 1º cadastro OK
        resp1 = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(resp1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Perfil.objects.count(), 1)

        # 2º cadastro com MESMO email e cpf diferente
        payload_dup_email = {
            **self.valid_payload,
            "cpf": "99988877766",
            "username": "user2",
        }
        resp2 = self.client.post(self.url, payload_dup_email, format="json")

        self.assertEqual(resp2.status_code, status.HTTP_400_BAD_REQUEST)
        # validação específica do serializer
        self.assertIn("email", resp2.data)
        self.assertIn("E-mail já cadastrado.", resp2.data["email"])

        # não cria novos registros
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Perfil.objects.count(), 1)

    def test_register_cpf_duplicado_retorna_400(self):
        """
        Não deve permitir cadastrar outro perfil com o mesmo CPF.
        """
        # 1º cadastro OK
        resp1 = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(resp1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Perfil.objects.count(), 1)

        # 2º cadastro com MESMO CPF e email diferente
        payload_dup_cpf = {
            **self.valid_payload,
            "email": "user2@example.com",
            "username": "user2",
        }
        resp2 = self.client.post(self.url, payload_dup_cpf, format="json")

        self.assertEqual(resp2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("cpf", resp2.data)
        self.assertIn("CPF já cadastrado.", resp2.data["cpf"])

        # continua só um user/perfil
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Perfil.objects.count(), 1)

    def test_register_senha_fraca_retorna_400(self):
        """
        Senha fraca deve falhar na validação de senha (validate_password)
        e não criar registros.
        """
        weak_payload = {
            **self.valid_payload,
            "email": "weak@example.com",
            "username": "user_weak",
            "cpf": "22233344455",
            "password": "123",  # fraca de propósito
        }

        resp = self.client.post(self.url, weak_payload, format="json")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", resp.data)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(Perfil.objects.count(), 0)

    def test_register_payload_incompleto_retorna_400(self):
        """
        Campos obrigatórios faltando (ex.: cpf) devem gerar erro 400.
        """
        incomplete_payload = {
            "email": "incompleto@example.com",
            "password": "StrongPass123!",
            # faltando cpf (obrigatório)
        }

        resp = self.client.post(self.url, incomplete_payload, format="json")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("cpf", resp.data)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(Perfil.objects.count(), 0)
