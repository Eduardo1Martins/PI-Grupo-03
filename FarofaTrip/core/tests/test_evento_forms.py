from django.test import TestCase
from core.forms import EventoForm
from datetime import date
from decimal import Decimal

class EventoFormTest(TestCase):

    def test_evento_form_valido(self):
        form_data = {
            'nome': 'Show de Rock',
            'local': 'Arena BR',
            'cidade': 'Rio de Janeiro',
            'data': date(2025, 12, 25),
            'descricao': 'Grande show de rock nacional',
            'imagem': 'https://example.com/show.jpg',
            'preco': Decimal('150.00'),
        }
        form = EventoForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_evento_form_campo_obrigatorio(self):
        """Deve falhar se nome estiver ausente"""
        form_data = {
            'local': 'Arena BR',
            'cidade': 'Rio de Janeiro',
            'data': date(2025, 12, 25),
            'descricao': 'Show sem nome',
            'imagem': 'https://example.com/show.jpg',
            'preco': Decimal('99.99'),
        }
        form = EventoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('nome', form.errors)
