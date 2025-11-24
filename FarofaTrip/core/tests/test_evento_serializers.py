from datetime import date
from decimal import Decimal

from django.test import TestCase

from core.models import Evento
from core.serializers import EventoSerializer


class EventoSerializerTestCase(TestCase):
    """
    Testes do serializer EventoSerializer:
    - Criação de eventos a partir de dados válidos
    - Validação de campos obrigatórios
    - Representação (serialização) de instâncias existentes
    """

    def setUp(self):
        """
        Define um payload válido padrão para ser reutilizado nos testes.
        """
        self.valid_data = {
            "nome": "Show de Teste",
            "local": "Casa de Shows",
            "cidade": "São Paulo",
            "data": "2025-01-01",
            "descricao": "Um evento de teste",
            "ingresso": "150.50",
            # 'excursao' não é enviado, deve assumir default=0
        }

    def test_evento_serializer_com_dados_validos_cria_evento(self):
        """
        Dado um payload válido, o serializer deve:
        - ser válido
        - salvar um objeto Evento
        - definir excursao com o default (0)
        """
        serializer = EventoSerializer(data=self.valid_data)

        # Serializer deve considerar o payload válido
        self.assertTrue(serializer.is_valid(), serializer.errors)

        evento = serializer.save()

        # Confere se o objeto criado é um Evento real
        self.assertIsInstance(evento, Evento)
        self.assertEqual(evento.nome, self.valid_data["nome"])
        self.assertEqual(evento.local, self.valid_data["local"])
        self.assertEqual(evento.cidade, self.valid_data["cidade"])
        self.assertEqual(str(evento.ingresso), self.valid_data["ingresso"])

        # Como 'excursao' não foi enviado, deve usar default=0
        self.assertEqual(evento.excursao, Decimal("0"))

    def test_evento_serializer_campos_obrigatorios(self):
        """
        Remove o campo 'nome' do payload e verifica se o serializer
        marca-o como obrigatório, adicionando erro nesse campo.
        """
        data = self.valid_data.copy()
        data.pop("nome")

        serializer = EventoSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("nome", serializer.errors)

    def test_evento_serializer_representacao(self):
        """
        Cria um Evento diretamente no banco e verifica se o serializer
        retorna os mesmos valores nos campos serializados.
        """
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

        # Os dados serializados devem refletir exatamente o objeto
        self.assertEqual(data["nome"], "Show 2")
        self.assertEqual(data["local"], "Arena Principal")
        self.assertEqual(data["cidade"], "Rio de Janeiro")
        self.assertEqual(data["ingresso"], "100.00")
        self.assertEqual(data["excursao"], "50.00")
