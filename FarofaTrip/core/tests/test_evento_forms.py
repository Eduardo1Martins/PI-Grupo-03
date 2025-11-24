from datetime import date
from decimal import Decimal

from django.test import TestCase

from core.forms import EventoForm


class EventoFormTest(TestCase):
    """
    Testes do formulário EventoForm:
    - Validação de dados obrigatórios
    - Comportamento de campos numéricos
    - Regras de data e default de excursão
    """

    def test_form_valido(self):
        """
        Formulário com todos os campos válidos deve:
        - ser considerado válido
        - salvar um objeto Evento com os valores esperados
        """
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

        # O formulário deve ser válido com esses dados
        self.assertTrue(form.is_valid())
        evento = form.save()

        # Confirma se os campos foram persistidos corretamente
        self.assertEqual(evento.nome, "Show Teste")
        self.assertEqual(evento.ingresso, Decimal("150.00"))
        self.assertEqual(evento.excursao, Decimal("50.00"))

    def test_form_invalido_sem_nome(self):
        """
        Se o campo 'nome' não for informado, o formulário deve ser inválido
        e conter erro especificamente no campo 'nome'.
        """
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
        """
        Exemplo de regra de negócio onde datas passadas não são aceitas.

        Observação: a validação de data passada precisa existir no EventoForm
        para este teste fazer sentido (clean_data ou validação customizada).
        """
        form = EventoForm(
            data={
                "nome": "Evento",
                "local": "Local",
                "cidade": "Cidade",
                "data": "2000-01-01",  # Data bem no passado
                "descricao": "Descrição",
                "ingresso": "50.00",
                "excursao": "0",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("data", form.errors)

    def test_excursao_default_zero(self):
        """
        Se o campo 'excursao' não for enviado,
        o formulário deve assumir o valor padrão 0 no modelo.
        """
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

        # excursao deve usar o valor padrão definido no modelo
        self.assertEqual(evento.excursao, Decimal("0"))
