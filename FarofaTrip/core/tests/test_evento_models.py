from django.test import TestCase
from core.models import Evento
from datetime import date
from decimal import Decimal

class EventoModelTest(TestCase):

    def test_criacao_evento(self):
        evento = Evento.objects.create(
            nome="Show do Legião Urbana",
            local="Arena SP",
            cidade="São Paulo",
            data=date(2025, 12, 25),
            descricao="Um tributo à Legião Urbana",
            imagem="https://example.com/legiao.jpg",
            preco=Decimal("199.90")
        )

        # Testa se foi criado
        self.assertEqual(Evento.objects.count(), 1)
        self.assertEqual(evento.nome, "Show do Legião Urbana")
        self.assertEqual(str(evento), "Show do Legião Urbana - São Paulo")

    def test_preco_decimal(self):
        evento = Evento.objects.create(
            nome="Evento Teste",
            local="Local Teste",
            cidade="Cidade Teste",
            data=date.today(),
            descricao="Evento para teste",
            imagem="https://example.com/img.jpg",
            preco=Decimal("59.99")
        )
        self.assertIsInstance(evento.preco, Decimal)
        self.assertEqual(evento.preco, Decimal("59.99"))
