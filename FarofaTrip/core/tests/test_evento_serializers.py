from datetime import date
from decimal import Decimal
from django.test import TestCase
from core.models import Evento
from core.serializers import EventoSerializer


class EventoSerializerTestCase(TestCase):
    def setUp(self):
        self.valid_data = {
            "nome": "Show de Teste",
            "local": "Casa de Shows",
            "cidade": "São Paulo",
            "data": "2025-01-01",
            "descricao": "Um evento de teste",
            "ingresso": "150.50",
        }

    def test_evento_serializer_com_dados_validos_cria_evento(self):
        serializer = EventoSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        evento = serializer.save()

        self.assertIsInstance(evento, Evento)
        self.assertEqual(evento.nome, self.valid_data["nome"])
        self.assertEqual(evento.local, self.valid_data["local"])
        self.assertEqual(evento.cidade, self.valid_data["cidade"])
        self.assertEqual(str(evento.ingresso), self.valid_data["ingresso"])
        self.assertEqual(evento.excursao, Decimal("0"))

    def test_evento_serializer_campos_obrigatorios(self):
        data = self.valid_data.copy()
        data.pop("nome")

        serializer = EventoSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("nome", serializer.errors)

    def test_evento_serializer_representacao(self):
        evento = Evento.objects.create(
            nome="Show 2",
            local="Arena Principal",
            cidade="Rio de Janeiro",
            data=date(2025, 1, 2),
            descricao="Outro evento",
            ingresso=Decimal("100.00"),
            excursao=Decimal("50.00"),
        )

        serializer = EventoSerializer(instance=evento)
        data = serializer.data

        self.assertEqual(data["nome"], "Show 2")
        self.assertEqual(data["local"], "Arena Principal")
        self.assertEqual(data["cidade"], "Rio de Janeiro")
        self.assertEqual(data["ingresso"], "100.00")
        self.assertEqual(data["excursao"], "50.00")
