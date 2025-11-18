from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from core.models import Perfil


User = get_user_model()


class PerfilModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="joaosilva",
            email="joao.silva@example.com",
            password="Senha@123",
            first_name="João",
            last_name="Silva",
        )

    def test_criacao_perfil(self):
        perfil = Perfil.objects.create(
            user=self.user,
            cpf="123.456.789-00",
            telefone="(11) 99999-9999",
            endereco="Rua A, 123",
        )

        self.assertEqual(Perfil.objects.count(), 1)
        self.assertEqual(perfil.cpf, "123.456.789-00")
        self.assertEqual(perfil.telefone, "(11) 99999-9999")
        self.assertEqual(perfil.endereco, "Rua A, 123")
        # __str__ usa o nome completo do usuário quando disponível
        self.assertEqual(str(perfil), "João Silva (123.456.789-00)")

    def test_cpf_unico(self):
        Perfil.objects.create(
            user=self.user,
            cpf="123.456.789-00",
        )
        outro_usuario = User.objects.create_user(
            username="maria",
            email="maria@example.com",
            password="Senha@123",
        )

        # mesmo CPF para outro usuário deve estourar a constraint UNIQUE
        with self.assertRaises(IntegrityError):
            Perfil.objects.create(
                user=outro_usuario,
                cpf="123.456.789-00",
            )

    def test_telefone_e_endereco_opcionais(self):
        perfil = Perfil.objects.create(
            user=self.user,
            cpf="987.654.321-00",
        )

        self.assertIsNone(perfil.telefone)
        self.assertIsNone(perfil.endereco)
        # relação reversa: user.perfil deve apontar para o mesmo objeto
        self.assertEqual(self.user.perfil, perfil)
