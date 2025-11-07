from django.test import TestCase
from core.forms import UsuarioForm
from datetime import date
from decimal import Decimal

class UsuarioFormTest(TestCase):

    def test_usuario_form_valido(self):
        form_data = {
            'nome': 'João da Silva',
            'cpf': '123.456.789-00',
            'telefone': '(11) 99999-9999',
            'endereco': 'Rua A, 123'
        }
        form = UsuarioForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_usuario_form_cpf_invalido(self):
        """CPF com tamanho incorreto deve falhar"""
        form_data = {
            'nome': 'Maria',
            'cpf': '12345678900',  # sem pontos e traço
            'telefone': '(11) 99999-9999',
            'endereco': 'Rua B, 45'
        }
        form = UsuarioForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('cpf', form.errors)
        self.assertEqual(form.errors['cpf'][0], 'O CPF deve estar no formato 000.000.000-00.')

    def test_telefone_invalido_curto(self):
        """Aciona o ValidationError do clean_telefone"""
        form_data = {
            'nome': 'Carlos',
            'cpf': '111.222.333-44',
            'telefone': '123',  # muito curto, 3 caracteres
            'endereco': 'Rua Teste'
        }
        form = UsuarioForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('telefone', form.errors)
        self.assertEqual(
            form.errors['telefone'][0],
            "O telefone deve estar no formato (00) 00000-0000."
        )
        
        
