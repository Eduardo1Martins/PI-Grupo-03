from django.test import TestCase
from django.contrib.auth import get_user_model
from core.forms import LoginForm

# Modelo de usuário configurado no projeto
User = get_user_model()


class LoginFormTests(TestCase):
    """
    Testes unitários para o LoginForm.

    Cobre:
    - autenticação bem-sucedida
    - e-mails não institucionais
    - case-insensitive no e-mail
    - erros para e-mail duplicado, inexistente, senha errada
    - mensagens de erro em campos obrigatórios.
    """

    def setUp(self):
        """
        Cria um usuário base para os testes.
        """
        self.user = User.objects.create_user(
            username="eduardo",
            email="eduardo@fatec.sp.gov.br",
            password="100Senha"
        )

    def test_valid_credentials_sets_user(self):
        """
        Credenciais válidas devem marcar o formulário como válido
        e definir o atributo form.user com o usuário autenticado.
        """
        form = LoginForm(data={
            "email": "eduardo@fatec.sp.gov.br",
            "password": "100Senha"
        })
        self.assertTrue(form.is_valid(), form.errors.as_json())
        self.assertTrue(hasattr(form, "user"))
        self.assertEqual(form.user.pk, self.user.pk)

    def test_accepts_non_institutional_email(self):
        """
        O formulário deve aceitar qualquer domínio de e-mail,
        não apenas institucional.
        """
        u = User.objects.create_user(
            username="ed_gmail",
            email="eduardo@gmail.com",
            password="Segredo123"
        )
        form = LoginForm(data={
            "email": "eduardo@gmail.com",
            "password": "Segredo123"
        })
        self.assertTrue(form.is_valid(), form.errors.as_json())
        self.assertEqual(form.user.pk, u.pk)

    def test_case_insensitive_email_lookup(self):
        """
        A busca por e-mail deve ser case-insensitive (email__iexact).
        """
        u = User.objects.create_user(
            username="maiusculo",
            email="caixa@dominio.com",
            password="Abc12345"
        )
        form = LoginForm(data={
            "email": "CAIXA@DOMINIO.COM",
            "password": "Abc12345"
        })
        self.assertTrue(form.is_valid(), form.errors.as_json())
        self.assertEqual(form.user.pk, u.pk)

    def test_duplicate_email_generates_form_error(self):
        """
        Se existirem múltiplos usuários com o mesmo e-mail,
        o formulário deve acusar erro de ambiguidade.
        """
        email_dup = "dup@exemplo.com"
        User.objects.create_user(username="dup1", email=email_dup, password="Senha@123")
        User.objects.create_user(username="dup2", email=email_dup, password="Senha@123")
        form = LoginForm(data={"email": email_dup, "password": "Senha@123"})

        self.assertFalse(form.is_valid())
        self.assertIn(
            "Há mais de um usuário com este e-mail",
            " ".join(form.non_field_errors())
        )

    def test_unknown_email_generates_form_error(self):
        """
        E-mail inexistente deve gerar erro informando que não foi encontrado.
        """
        form = LoginForm(data={
            "email": "naoexiste@gmail.com",
            "password": "100Senha"
        })
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Usuário com esse e-mail não encontrado.",
            form.non_field_errors()
        )

    def test_wrong_password_generates_form_error(self):
        """
        Senha incorreta deve gerar erro apropriado.
        """
        form = LoginForm(data={
            "email": "eduardo@fatec.sp.gov.br",
            "password": "senha_errada"
        })
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Senha incorreta para o e-mail informado.",
            form.non_field_errors()
        )

    def test_email_required_message(self):
        """
        Campo email vazio deve disparar a mensagem configurada no form.
        """
        form = LoginForm(data={
            "email": "",
            "password": "100Senha"
        })
        self.assertFalse(form.is_valid())
        self.assertIn("Informe o e-mail.", form.errors.get("email", []))

    def test_password_required(self):
        """
        Campo password vazio deve gerar erro de campo obrigatório.
        """
        form = LoginForm(data={
            "email": "eduardo@fatec.sp.gov.br",
            "password": ""
        })
        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)
