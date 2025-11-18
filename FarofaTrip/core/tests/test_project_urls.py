from importlib import reload
from django.test import SimpleTestCase, override_settings


class ProjectUrlsTest(SimpleTestCase):
    @override_settings(DEBUG=True, MEDIA_URL="/media/", MEDIA_ROOT="/tmp")
    def test_static_urls_are_added_when_debug_true(self):
        """
        Garante que, com DEBUG=True, o bloco de static() em FarofaTrip/urls.py
        é executado e adiciona rotas de media em urlpatterns.
        """
        import FarofaTrip.urls as project_urls

        reload(project_urls)

        self.assertGreaterEqual(len(project_urls.urlpatterns), 3)
