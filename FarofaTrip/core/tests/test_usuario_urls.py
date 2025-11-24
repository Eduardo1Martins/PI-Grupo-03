from django.test import SimpleTestCase
from django.urls import reverse, resolve
from core.views import UsuarioViewSet


class TestUsuarioURLs(SimpleTestCase):
    """
    Testes de roteamento de URLs para o recurso 'usuario'.

    Garante que o router do DRF registrou corretamente:
    - usuario-list
    - usuario-detail
    apontando para o UsuarioViewSet.
    """

    def test_url_list_existe(self):
        """
        A URL nomeada 'usuario-list' deve existir e resolver para UsuarioViewSet.
        """
        url = reverse('usuario-list')
        resolver = resolve(url)
        self.assertEqual(resolver.func.cls, UsuarioViewSet)

    def test_url_detail_existe(self):
        """
        A URL nomeada 'usuario-detail' deve existir e resolver para UsuarioViewSet.
        """
        url = reverse('usuario-detail', kwargs={'pk': 1})
        resolver = resolve(url)
        self.assertEqual(resolver.func.cls, UsuarioViewSet)
