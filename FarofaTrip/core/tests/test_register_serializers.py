from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import Perfil
from core.serializers import RegisterSerializer

User = get_user_model()


class RegisterSerializerTestCase(TestCase):
    """
    Testes unitários para o RegisterSerializer.

    Foca na lógica de:
    - criação de User + Perfil
    - validação de e-mail e CPF únicos
    - comportamento do campo 'nome' (split em first_name / last_name)
    - uso do e-mail como username quando username não é enviado
    - validação de senha.
    """

    def setUp(self):
        """
        Define um payload base com dados válidos para reuso nos testes.
        """
        self.valid_data = {
            "nome": "Fulano da Silva",
            "email": "fulano@example.com",
            "password": "SenhaForte123!",
            "cpf": "123.456.789-00",
            "telefone": "(11) 99999-9999",
            "endereco": "Rua Teste, 123"
        }

    def test_should_register_user_successfully(self):
        """
        Deve criar um Usuário e um Perfil com sucesso quando os dados são válidos.
        Verifica também se a lógica de separar 'nome' em first_name e last_name funciona.
        """
        serializer = RegisterSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        user = serializer.save()

        self.assertIsInstance(user, User)
        self.assertEqual(user.email, self.valid_data['email'])
        self.assertEqual(user.first_name, "Fulano")
        self.assertEqual(user.last_name, "da Silva")

        self.assertTrue(Perfil.objects.filter(user=user).exists())
        self.assertEqual(user.perfil.cpf, self.valid_data['cpf'])
        self.assertEqual(user.perfil.telefone, self.valid_data['telefone'])

    def test_should_fail_with_duplicate_email(self):
        """
        Não deve permitir cadastro se o e-mail já existir no banco (User).
        """
        User.objects.create_user(
            username="existente",
            email="fulano@example.com",
            password="password"
        )

        serializer = RegisterSerializer(data=self.valid_data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
        self.assertEqual(str(serializer.errors['email'][0]), "E-mail já cadastrado.")

    def test_should_fail_with_duplicate_cpf(self):
        """
        Não deve permitir cadastro se o CPF já existir no banco (Perfil).
        """
        user_existente = User.objects.create_user(
            username="outro",
            email="outro@example.com",
            password="password"
        )
        Perfil.objects.create(user=user_existente, cpf="123.456.789-00")

        serializer = RegisterSerializer(data=self.valid_data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('cpf', serializer.errors)
        self.assertEqual(str(serializer.errors['cpf'][0]), "CPF já cadastrado.")

    def test_username_should_default_to_email_if_missing(self):
        """
        Se o campo 'username' não for enviado, o serializer deve usar o e-mail como username
        conforme lógica no método create.
        """
        data_sem_username = self.valid_data.copy()
        if 'username' in data_sem_username:
            del data_sem_username['username']

        serializer = RegisterSerializer(data=data_sem_username)
        self.assertTrue(serializer.is_valid())

        user = serializer.save()
        self.assertEqual(user.username, self.valid_data['email'])

    def test_password_validation(self):
        """
        Verifica se a validação de senha (validate_password do Django) está sendo chamada.
        Nota: Isso depende das configurações do settings.py do Django.
        Geralmente senhas vazias ou muito curtas falham.
        """
        data_senha_fraca = self.valid_data.copy()
        data_senha_fraca['password'] = ""

        serializer = RegisterSerializer(data=data_senha_fraca)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

    def test_split_nome_edge_cases(self):
        """
        Testa a lógica de divisão de nome com apenas um nome (sem sobrenome).
        """
        data = self.valid_data.copy()
        data['nome'] = "Monônimo"
        data['email'] = "novo@teste.com"
        data['cpf'] = "999.999.999-99"

        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        self.assertEqual(user.first_name, "Monônimo")
        self.assertEqual(user.last_name, "")
