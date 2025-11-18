from datetime import date
from decimal import Decimal

from django.test import TestCase

from core.forms import EventoForm


class EventoFormTest(TestCase):
    def test_form_valido(self):
        form = EventoForm(
            data={
                "nome": "Show Teste",
                "local": "Arena Teste",
                "cidade": "São Paulo",
                "data": "2025-12-20",
                "descricao": "Descrição do evento",
                "ingresso": "150.00",
                "excursao": "50.00",
            }
        )

        self.assertTrue(form.is_valid())
        evento = form.save()
        self.assertEqual(evento.nome, "Show Teste")
        self.assertEqual(evento.ingresso, Decimal("150.00"))
        self.assertEqual(evento.excursao, Decimal("50.00"))

    def test_form_invalido_sem_nome(self):
        form = EventoForm(
            data={
                "local": "Arena Teste",
                "cidade": "São Paulo",
                "data": "2025-12-20",
                "descricao": "Evento sem nome",
                "ingresso": "100.00",
                "excursao": "0",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("nome", form.errors)

    def test_form_invalido_data_passada(self):
        form = EventoForm(
            data={
                "nome": "Evento",
                "local": "Local",
                "cidade": "Cidade",
                "data": "2000-01-01",
                "descricao": "Descrição",
                "ingresso": "50.00",
                "excursao": "0",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("data", form.errors)

    def test_excursao_default_zero(self):
        form = EventoForm(
            data={
                "nome": "Evento sem excursão",
                "local": "Local",
                "cidade": "Cidade",
                "data": "2025-01-01",
                "descricao": "Teste",
                "ingresso": "80.00",
                # campo excursao omitido
            }
        )

        self.assertTrue(form.is_valid())
        evento = form.save()
        self.assertEqual(evento.excursao, Decimal("0"))
