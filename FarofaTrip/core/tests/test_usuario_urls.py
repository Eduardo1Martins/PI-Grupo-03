from django.test import SimpleTestCase
from django.urls import reverse, resolve
from core.views import UsuarioViewSet

class TestUsuarioURLs(SimpleTestCase):
    def test_url_list_existe(self):
        url = reverse('usuario-list')  
        resolver = resolve(url)
        self.assertEqual(resolver.func.cls, UsuarioViewSet)
        
        
    def test_url_detail_existe(self):
        url = reverse('usuario-detail', kwargs={'pk': 1})
        resolver = resolve(url)
        self.assertEqual(resolver.func.cls, UsuarioViewSet)