from django.test import SimpleTestCase
from django.urls import reverse, resolve
from core.views import EventoViewSet

class TestEventoURLs(SimpleTestCase):
    def test_url_list_existe(self):
        url = reverse('evento-list')
        resolver = resolve(url)
        self.assertEqual(resolver.func.cls, EventoViewSet)
        
        
    def test_url_detail_existe(self):
        url = reverse('evento-detail', kwargs={'pk': 1})
        resolver = resolve(url)
        self.assertEqual(resolver.func.cls, EventoViewSet)