from django.test import SimpleTestCase
from django.urls import reverse, resolve
from core.views import EventoViewSet


class TestEventoURLs(SimpleTestCase):
    """
    Testa o mapeamento de URLs relacionadas ao recurso 'evento'.

    Verifica se as rotas geradas pelo router DRF ('evento-list' e 'evento-detail')
    realmente apontam para a classe EventoViewSet.
    """

    def test_url_list_existe(self):
        """
        A URL nomeada 'evento-list' deve existir e estar ligada ao EventoViewSet.
        """
        # Gera a URL usando o nome registrado no router
        url = reverse('evento-list')

        # resolve descobre a view associada à URL
        resolver = resolve(url)

        # Para ViewSets, DRF expõe .cls como a classe original
        self.assertEqual(resolver.func.cls, EventoViewSet)

    def test_url_detail_existe(self):
        """
        A URL nomeada 'evento-detail' (detalhe com pk) deve existir
        e estar ligada ao EventoViewSet.
        """
        url = reverse('evento-detail', kwargs={'pk': 1})
        resolver = resolve(url)
        self.assertEqual(resolver.func.cls, EventoViewSet)
