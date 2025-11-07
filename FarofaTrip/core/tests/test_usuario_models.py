from django.test import TestCase
from core.models import Usuario
from datetime import date
from decimal import Decimal

class UsuarioModelTest(TestCase):

    def test_criacao_usuario(self):
        usuario = Usuario.objects.create(
            nome="João Silva",
            cpf="123.456.789-00",
            telefone="(11) 99999-9999",
            endereco="Rua A, 123"
        )

        # Testa se foi salvo corretamente
        self.assertEqual(Usuario.objects.count(), 1)
        self.assertEqual(usuario.nome, "João Silva")
        self.assertEqual(str(usuario), "João Silva (123.456.789-00)")

    def test_cpf_unico(self):
        Usuario.objects.create(nome="Maria", cpf="123.456.789-00")
        with self.assertRaises(Exception):
            # CPF duplicado deve gerar erro
            Usuario.objects.create(nome="José", cpf="123.456.789-00")
