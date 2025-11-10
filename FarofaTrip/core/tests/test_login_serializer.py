from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
from django.core.exceptions import ValidationError
from core.serializers import EmailTokenObtainPairSerializer

User = get_user_model()

class EmailTokenObtainPairSerializerTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username="eduardo",
            email="eduardo@fatec.sp.gov.br",
            password="100Senha"
        )

    def _make_req(self):
        return self.factory.post('/api/auth/login/')

    def test_success_returns_tokens_and_user_payload(self):
        data = {"email": "eduardo@fatec.sp.gov.br", "password": "100Senha"}
        ser = EmailTokenObtainPairSerializer(data=data, context={"request": self._make_req()})
        self.assertTrue(ser.is_valid(), ser.errors)

        out = ser.validated_data
        self.assertIn("access", out)
        self.assertIn("refresh", out)
        self.assertIn("user", out)
        self.assertEqual(out["user"]["id"], self.user.id)
        self.assertEqual(out["user"]["email"], self.user.email)

    def test_invalid_password_raises_validation_error(self):
        data = {"email": "eduardo@fatec.sp.gov.br", "password": "errada"}
        ser = EmailTokenObtainPairSerializer(data=data, context={"request": self._make_req()})
        self.assertFalse(ser.is_valid())
        self.assertIn("Credenciais inválidas.", str(ser.errors))

    def test_email_not_found_raises_validation_error(self):
        data = {"email": "desconhecido@example.com", "password": "foo"}
        ser = EmailTokenObtainPairSerializer(data=data, context={"request": self._make_req()})
        self.assertFalse(ser.is_valid())
        self.assertIn("E-mail não encontrado.", str(ser.errors))

    def test_missing_fields_raise_single_message(self):
        ser = EmailTokenObtainPairSerializer(data={}, context={"request": self._make_req()})
        self.assertFalse(ser.is_valid())
        self.assertIn("E-mail e senha são obrigatórios.", str(ser.errors))

        ser2 = EmailTokenObtainPairSerializer(data={"email": "x@y.com"}, context={"request": self._make_req()})
        self.assertFalse(ser2.is_valid())
        self.assertIn("E-mail e senha são obrigatórios.", str(ser2.errors))

        ser3 = EmailTokenObtainPairSerializer(data={"password": "123"}, context={"request": self._make_req()})
        self.assertFalse(ser3.is_valid())
        self.assertIn("E-mail e senha são obrigatórios.", str(ser3.errors))

    def test_case_insensitive_email_lookup(self):
        u = User.objects.create_user(
            username="maiusculo",
            email="CAIXA@DOMINIO.COM",
            password="Abc12345"
        )
        data = {"email": "caixa@dominio.com", "password": "Abc12345"}
        ser = EmailTokenObtainPairSerializer(data=data, context={"request": self._make_req()})
        self.assertTrue(ser.is_valid(), ser.errors)
        self.assertEqual(ser.validated_data["user"]["id"], u.id)

    def test_duplicate_email_raises_specific_error(self):
        email_dup = "dup@exemplo.com"
        User.objects.create_user(username="dup1", email=email_dup, password="Senha@123")
        User.objects.create_user(username="dup2", email=email_dup, password="Senha@123")
        ser = EmailTokenObtainPairSerializer(
            data={"email": email_dup, "password": "Senha@123"},
            context={"request": self._make_req()}
        )
        self.assertFalse(ser.is_valid())
        self.assertIn("Há mais de um usuário com este e-mail", str(ser.errors))
