from datetime import date, timedelta
from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Evento


class EventoViewSetTests(APITestCase):
    """
    Testes de integração para o EventoViewSet (API REST).

    Cobre:
    - filtragem por scope (future, past, all)
    - busca (search)
    - ordenação (ordering)
    - criação, atualização e exclusão de eventos via API.
    """

    def setUp(self):
        # URL base da lista de eventos (gerada pelo router DRF)
        self.list_url = reverse("evento-list")

    def _cria_evento(
        self,
        nome="Show Teste",
        local="Casa de Shows",
        cidade="Cidade X",
        data=None,
        descricao="Evento de teste",
        ingresso="50.00",
        excursao="0.00",
    ):
        """
        Helper para criar eventos com valores padrão, permitindo sobrescritas.
        Facilita a criação de cenários de teste.
        """
        if data is None:
            data = date.today()
        return Evento.objects.create(
            nome=nome,
            local=local,
            cidade=cidade,
            data=data,
            descricao=descricao,
            ingresso=Decimal(ingresso),
            excursao=Decimal(excursao),
        )

    def test_list_default_scope_future_retorna_hoje_e_futuros(self):
        """
        Sem parâmetro scope, deve usar 'future' (data >= hoje).
        """
        today = date.today()
        past = today - timedelta(days=1)
        future = today + timedelta(days=1)

        ev_past = self._cria_evento(nome="Evento Passado", data=past)
        ev_today = self._cria_evento(nome="Evento Hoje", data=today)
        ev_future = self._cria_evento(nome="Evento Futuro", data=future)

        response = self.client.get(self.list_url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        nomes = {item["nome"] for item in response.data}

        self.assertIn(ev_today.nome, nomes)
        self.assertIn(ev_future.nome, nomes)
        self.assertNotIn(ev_past.nome, nomes)

    def test_list_scope_past_retorna_apenas_passados(self):
        """
        scope=past deve retornar apenas eventos com data < hoje.
        """
        today = date.today()
        past = today - timedelta(days=1)
        future = today + timedelta(days=1)

        ev_past = self._cria_evento(nome="Evento Passado", data=past)
        self._cria_evento(nome="Evento Hoje", data=today)
        self._cria_evento(nome="Evento Futuro", data=future)

        response = self.client.get(f"{self.list_url}?scope=past", format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        nomes = {item["nome"] for item in response.data}
        self.assertEqual(nomes, {ev_past.nome})

    def test_list_scope_all_retorna_todos(self):
        """
        scope=all deve ignorar filtro de data e retornar todos os eventos.
        """
        today = date.today()
        past = today - timedelta(days=1)
        future = today + timedelta(days=1)

        ev_past = self._cria_evento(nome="Evento Passado", data=past)
        ev_today = self._cria_evento(nome="Evento Hoje", data=today)
        ev_future = self._cria_evento(nome="Evento Futuro", data=future)

        response = self.client.get(f"{self.list_url}?scope=all", format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        nomes = {item["nome"] for item in response.data}
        self.assertSetEqual(
            nomes,
            {ev_past.nome, ev_today.nome, ev_future.nome},
        )

    def test_search_por_nome(self):
        """
        search deve filtrar por nome/cidade/local/descricao.
        Aqui filtramos pelo termo 'Rock'.
        """
        self._cria_evento(nome="Festival de Rock", cidade="São Paulo")
        self._cria_evento(nome="Feira de Tecnologia", cidade="Campinas")

        response = self.client.get(
            f"{self.list_url}?scope=all&search=Rock",
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["nome"], "Festival de Rock")

    def test_ordering_por_nome(self):
        """
        ordering=nome deve ordenar alfabeticamente pelo campo nome.
        """
        today = date.today()
        self._cria_evento(nome="Z Evento", data=today)
        self._cria_evento(nome="A Evento", data=today)
        self._cria_evento(nome="M Evento", data=today)

        response = self.client.get(
            f"{self.list_url}?scope=all&ordering=nome",
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        nomes = [item["nome"] for item in response.data]
        # a lista retornada deve estar em ordem alfabética
        self.assertEqual(nomes, sorted(nomes))

    def test_create_evento_cria_registro(self):
        """
        POST /eventos/ deve criar um novo Evento com os campos enviados.
        """
        payload = {
            "nome": "Show de Teste",
            "local": "Arena Principal",
            "cidade": "Cidade Teste",
            "data": str(date.today()),
            "descricao": "Um show incrível de teste.",
            "ingresso": "100.00",
            "excursao": "20.00",
            # imagem é opcional (null/blank)
        }

        response = self.client.post(self.list_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Evento.objects.count(), 1)

        evento = Evento.objects.first()
        self.assertIsNotNone(evento)
        self.assertEqual(evento.nome, payload["nome"])
        self.assertEqual(evento.local, payload["local"])
        self.assertEqual(evento.cidade, payload["cidade"])
        self.assertEqual(str(evento.data), payload["data"])
        self.assertEqual(evento.descricao, payload["descricao"])
        self.assertEqual(evento.ingresso, Decimal("100.00"))
        self.assertEqual(evento.excursao, Decimal("20.00"))

    def test_update_evento_atualiza_campos(self):
        """
        PATCH /eventos/{pk}/ deve atualizar campos do evento.
        """
        evento = self._cria_evento(
            nome="Evento Original",
            ingresso="50.00",
            excursao="0.00",
        )
        detail_url = reverse("evento-detail", args=[evento.pk])

        payload = {
            "nome": "Evento Atualizado",
            "ingresso": "75.50",
        }

        response = self.client.patch(detail_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        evento.refresh_from_db()
        self.assertEqual(evento.nome, "Evento Atualizado")
        self.assertEqual(evento.ingresso, Decimal("75.50"))

    def test_delete_evento_remove_registro(self):
        """
        DELETE /eventos/{pk}/ deve remover o evento.
        """
        evento = self._cria_evento(nome="Evento a Deletar")
        detail_url = reverse("evento-detail", args=[evento.pk])

        response = self.client.delete(detail_url, format="json")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Evento.objects.count(), 0)
