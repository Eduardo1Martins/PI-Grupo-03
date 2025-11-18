from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import Perfil
from core.serializers import PerfilSerializer

User = get_user_model()


class PerfilSerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="usuario_teste",
            email="teste@example.com",
            password="senha123",
            first_name="Nome",
            last_name="Sobrenome",
        )
        self.perfil = Perfil.objects.create(
            user=self.user,
            cpf="123.456.789-00",
            telefone="11988887777",
            endereco="Rua Antiga, 123",
        )

    def test_perfil_serializer_representacao(self):
        """
        Garante que o serializer retorna os campos combinados de User + Perfil corretamente.
        """
        serializer = PerfilSerializer(instance=self.perfil)
        data = serializer.data

        self.assertEqual(data["id"], self.user.id)
        self.assertEqual(data["username"], self.user.username)
        self.assertEqual(data["email"], self.user.email)
        self.assertEqual(data["first_name"], self.user.first_name)
        self.assertEqual(data["last_name"], self.user.last_name)
        self.assertEqual(data["cpf"], self.perfil.cpf)
        self.assertEqual(data["telefone"], self.perfil.telefone)
        self.assertEqual(data["endereco"], self.perfil.endereco)

    def test_perfil_serializer_update_atualiza_user_e_perfil(self):
        """
        Garante que o update atualiza tanto os campos de User quanto do Perfil.
        """
        payload = {
            "username": "novo_usuario",
            "email": "novo_email@example.com",
            "first_name": "NovoNome",
            "last_name": "NovoSobrenome",
            "cpf": "987.654.321-00",
            "telefone": "11999998888",
            "endereco": "Rua Nova, 456",
        }

        serializer = PerfilSerializer(instance=self.perfil, data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        perfil_atualizado = serializer.save()

        self.user.refresh_from_db()
        perfil_atualizado.refresh_from_db()

        self.assertEqual(self.user.username, payload["username"])
        self.assertEqual(self.user.email, payload["email"])
        self.assertEqual(self.user.first_name, payload["first_name"])
        self.assertEqual(self.user.last_name, payload["last_name"])

        self.assertEqual(perfil_atualizado.cpf, payload["cpf"])
        self.assertEqual(perfil_atualizado.telefone, payload["telefone"])
        self.assertEqual(perfil_atualizado.endereco, payload["endereco"])

    def test_perfil_serializer_nao_permite_editar_id(self):
        """
        Garante que o campo id (user.id) é somente leitura e não é alterado via payload.
        """
        old_id = self.user.id

        payload = {
            "id": old_id + 1, 
            "username": "usuario_mesmo_id",
            "email": "mesmoid@example.com",
            "cpf": "111.222.333-44",
        }

        serializer = PerfilSerializer(instance=self.perfil, data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        perfil_atualizado = serializer.save()
        self.user.refresh_from_db()
        perfil_atualizado.refresh_from_db()

        self.assertEqual(self.user.id, old_id)
        self.assertEqual(perfil_atualizado.user.id, old_id)
        self.assertEqual(self.user.username, payload["username"])
        self.assertEqual(self.user.email, payload["email"])
        self.assertEqual(perfil_atualizado.cpf, payload["cpf"])
