from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Perfil

User = get_user_model()


class UsuarioViewSetTests(APITestCase):
    def setUp(self):
        self.list_url = reverse("usuario-list")

    def _cria_user_e_perfil(
        self,
        username="user1",
        email="user1@example.com",
        first_name="User",
        last_name="One",
        cpf="12345678910",
        telefone="11999999999",
        endereco="Rua de Teste, 123",
    ):
        user = User.objects.create_user(
            username=username,
            email=email,
            password="StrongPass123!",
            first_name=first_name,
            last_name=last_name,
        )
        perfil = Perfil.objects.create(
            user=user,
            cpf=cpf,
            telefone=telefone,
            endereco=endereco,
        )
        return user, perfil

    def test_list_usuarios_retorna_perfis(self):
        """
        GET /usuarios/ deve retornar a lista de perfis serializados.
        """
        _, perfil1 = self._cria_user_e_perfil(
            username="user1",
            email="user1@example.com",
            cpf="11111111111",
        )
        _, perfil2 = self._cria_user_e_perfil(
            username="user2",
            email="user2@example.com",
            cpf="22222222222",
        )

        response = self.client.get(self.list_url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # assumindo que não há paginação configurada
        self.assertEqual(len(response.data), 2)

        returned_ids = sorted([item["id"] for item in response.data])
        self.assertEqual(returned_ids, sorted([perfil1.user.id, perfil2.user.id]))

    def test_retrieve_usuario_retorna_um_perfil(self):
        """
        GET /usuarios/{pk}/ deve retornar os dados de um perfil específico.
        pk é o id do Perfil, mas o campo 'id' na resposta é o id do User.
        """
        user, perfil = self._cria_user_e_perfil(
            username="user_detail",
            email="detail@example.com",
            cpf="33333333333",
        )
        detail_url = reverse("usuario-detail", args=[perfil.pk])

        response = self.client.get(detail_url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], user.id)
        self.assertEqual(response.data["username"], user.username)
        self.assertEqual(response.data["email"], user.email)
        self.assertEqual(response.data["cpf"], perfil.cpf)

    def test_create_usuario_cria_user_e_perfil(self):
        """
        POST /usuarios/ deve criar um novo User + Perfil via PerfilSerializer.create.
        """
        payload = {
            # campos mapeados para user.*
            "username": "novo_user",
            "email": "novo_user@example.com",
            "first_name": "Novo",
            "last_name": "User",
            # campos do Perfil
            "cpf": "44444444444",
            "telefone": "11888888888",
            "endereco": "Rua Nova, 456",
        }

        response = self.client.post(self.list_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # deve ter criado exatamente 1 User e 1 Perfil
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Perfil.objects.count(), 1)

        perfil = Perfil.objects.select_related("user").first()
        self.assertIsNotNone(perfil)
        self.assertEqual(perfil.user.username, payload["username"])
        self.assertEqual(perfil.user.email, payload["email"])
        self.assertEqual(perfil.cpf, payload["cpf"])
        self.assertEqual(perfil.telefone, payload["telefone"])
        self.assertEqual(perfil.endereco, payload["endereco"])

        # resposta deve bater com os dados criados
        self.assertEqual(response.data["id"], perfil.user.id)
        self.assertEqual(response.data["username"], payload["username"])
        self.assertEqual(response.data["email"], payload["email"])
        self.assertEqual(response.data["cpf"], payload["cpf"])

    def test_update_usuario_atualiza_user_e_perfil(self):
        """
        PUT/PATCH /usuarios/{pk}/ deve atualizar dados do User e do Perfil.
        """
        user, perfil = self._cria_user_e_perfil(
            username="user_update",
            email="update@example.com",
            cpf="55555555555",
            telefone="11000000000",
            endereco="Rua Velha, 100",
        )
        detail_url = reverse("usuario-detail", args=[perfil.pk])

        payload = {
            "first_name": "Atualizado",
            "last_name": "Silva",
            "telefone": "11999990000",
            "endereco": "Rua Atualizada, 999",
        }

        response = self.client.patch(detail_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # recarrega do banco
        user.refresh_from_db()
        perfil.refresh_from_db()

        self.assertEqual(user.first_name, "Atualizado")
        self.assertEqual(user.last_name, "Silva")
        self.assertEqual(perfil.telefone, "11999990000")
        self.assertEqual(perfil.endereco, "Rua Atualizada, 999")

        # resposta deve refletir as alterações
        self.assertEqual(response.data["first_name"], "Atualizado")
        self.assertEqual(response.data["last_name"], "Silva")
        self.assertEqual(response.data["telefone"], "11999990000")
        self.assertEqual(response.data["endereco"], "Rua Atualizada, 999")

    def test_delete_usuario_remove_apenas_perfil(self):
        """
        DELETE /usuarios/{pk}/ deve remover o Perfil, mas o User permanece
        (on_delete=CASCADE está na direção User -> Perfil).
        """
        user, perfil = self._cria_user_e_perfil(
            username="user_delete",
            email="delete@example.com",
            cpf="66666666666",
        )
        detail_url = reverse("usuario-detail", args=[perfil.pk])

        response = self.client.delete(detail_url, format="json")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Perfil removido
        self.assertEqual(Perfil.objects.count(), 0)

        # User ainda existe
        self.assertTrue(User.objects.filter(id=user.id).exists())
