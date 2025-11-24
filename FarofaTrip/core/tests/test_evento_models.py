from datetime import date
from decimal import Decimal

from django.test import TestCase

from core.models import Evento


class EventoModelTest(TestCase):
    """
    Testes unitários para o modelo Evento:
    - Criação com e sem excursão
    - Valores padrão
    - Tipos dos campos monetários
    """

    def test_criacao_evento_com_excursao(self):
        """
        Garante que um Evento com excursão explícita seja criado corretamente
        e que o __str__ retorne apenas o nome do evento.
        """
        evento = Evento.objects.create(
            nome="Show do Legião Urbana",
            local="Arena SP",
            cidade="São Paulo",
            data=date(2025, 12, 25),
            descricao="Um tributo à Legião Urbana",
            imagem="eventos/legiao.jpg",
            ingresso=Decimal("199.90"),
            excursao=Decimal("100.00"),
        )

        self.assertEqual(Evento.objects.count(), 1)
        self.assertEqual(evento.nome, "Show do Legião Urbana")
        self.assertEqual(evento.local, "Arena SP")
        self.assertEqual(evento.cidade, "São Paulo")
        self.assertEqual(evento.ingresso, Decimal("199.90"))
        self.assertEqual(evento.excursao, Decimal("100.00"))

        # __str__ do modelo deve retornar apenas o nome
        self.assertEqual(str(evento), "Show do Legião Urbana")

    def test_excursao_default_zero(self):
        """
        Quando 'excursao' não é informado na criação,
        o modelo deve assumir o valor default=0.
        """
        evento = Evento.objects.create(
            nome="Evento sem excursão",
            local="Arena de Teste",
            cidade="Campinas",
            data=date.today(),
            descricao="Somente ingresso, sem excursão",
            imagem="eventos/sem_excursao.jpg",
            ingresso=Decimal("59.90"),
            # excursao não informado -> deve usar default do campo
        )

        self.assertEqual(evento.excursao, Decimal("0"))

    def test_ingresso_e_excursao_sao_decimal(self):
        """
        Garante que os campos monetários sejam instâncias de Decimal,
        evitando problemas com ponto flutuante.
        """
        evento = Evento.objects.create(
            nome="Evento Teste",
            local="Local Teste",
            cidade="Cidade Teste",
            data=date.today(),
            descricao="Evento para teste",
            imagem="eventos/img.jpg",
            ingresso=Decimal("59.99"),
            excursao=Decimal("15.50"),
        )

        self.assertIsInstance(evento.ingresso, Decimal)
        self.assertIsInstance(evento.excursao, Decimal)
