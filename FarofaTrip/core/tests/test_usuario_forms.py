from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from core.forms import PerfilForm
from core.models import Perfil


User = get_user_model()


class PerfilFormTest(TestCase):
    """
    Testes unitários para o PerfilForm.

    Foca nas validações de:
    - CPF (tamanho/formato esperado)
    - telefone (tamanho esperado)
    e no fluxo básico de criação de Perfil via formulário.
    """

    def setUp(self):
        """
        Cria um usuário base para associar ao Perfil criado via form.
        """
        self.user = User.objects.create_user(
            username="testeuser",
            email="teste@example.com",
            password="123456",
            first_name="Teste",
            last_name="User",
        )

    def test_form_valido(self):
        """
        Formulário com CPF e telefone em formatos válidos deve ser considerado válido
        e permitir criar um Perfil corretamente.
        """
        form = PerfilForm(
            data={
                "cpf": "123.456.789-00",      # 14 chars
                "telefone": "(11)90000-0000", # 15 chars
                "endereco": "Rua X, 123",
            }
        )

        self.assertTrue(form.is_valid())
        perfil = form.save(commit=False)
        perfil.user = self.user
        perfil.save()

        self.assertEqual(perfil.cpf, "123.456.789-00")
        self.assertEqual(perfil.telefone, "(11)90000-0000")

    # --- TESTES PARA COBRIR clean_cpf ---

    def test_cpf_invalido_menos_caracteres(self):
        """
        CPF com tamanho != 14 deve gerar erro.
        """
        form = PerfilForm(data={"cpf": "123"})  # muito curto

        self.assertFalse(form.is_valid())
        self.assertIn("cpf", form.errors)

    def test_cpf_invalido_mais_caracteres(self):
        """
        CPF com tamanho maior que o esperado também deve falhar.
        """
        form = PerfilForm(data={"cpf": "123.456.789-000"})  # 15 chars

        self.assertFalse(form.is_valid())
        self.assertIn("cpf", form.errors)

    def test_cpf_valido_formato_14_chars(self):
        """
        CPF exatamente com 14 caracteres deve passar pela validação de formato.
        """
        form = PerfilForm(data={"cpf": "123.456.789-00"})  # 14 chars

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["cpf"], "123.456.789-00")

    # --- TESTES PARA COBRIR clean_telefone ---

    def test_telefone_invalido_menos_caracteres(self):
        """
        Telefone com 14 caracteres (menos que o esperado) deve falhar.
        """
        form = PerfilForm(
            data={
                "cpf": "123.456.789-00",
                "telefone": "(11)90000-000",  # 14 chars
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("telefone", form.errors)

    def test_telefone_invalido_mais_caracteres(self):
        """
        Telefone com 16 caracteres (mais que o esperado) deve falhar.
        """
        form = PerfilForm(
            data={
                "cpf": "123.456.789-00",
                "telefone": "(11)90000-00000",  # 16 chars
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("telefone", form.errors)

    def test_telefone_valido_15_chars(self):
        """
        Telefone com 15 caracteres deve passar na validação de formato.
        """
        form = PerfilForm(
            data={
                "cpf": "123.456.789-00",
                "telefone": "(11)90000-0000",  # 15 chars
            }
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["telefone"], "(11)90000-0000")
