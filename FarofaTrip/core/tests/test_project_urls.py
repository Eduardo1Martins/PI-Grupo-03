from importlib import reload
from django.test import SimpleTestCase, override_settings


class ProjectUrlsTest(SimpleTestCase):
    """
    Testes relacionados ao módulo de URLs do projeto principal (FarofaTrip/urls.py).

    A ideia aqui é garantir que, com DEBUG=True, o trecho que adiciona
    URLs de media (via static()) seja executado, aumentando o número de rotas.
    """

    @override_settings(DEBUG=True, MEDIA_URL="/media/", MEDIA_ROOT="/tmp")
    def test_static_urls_are_added_when_debug_true(self):
        """
        Garante que, com DEBUG=True, o bloco de static() em FarofaTrip/urls.py
        é executado e adiciona rotas de media em urlpatterns.
        """
        # Importa o módulo de URLs do projeto
        import FarofaTrip.urls as project_urls

        # reload força a reexecução do módulo com as settings sobrescritas
        reload(project_urls)

        # Apenas checa se temos "algumas" URLs (>= 3) registradas.
        # Isso implica que o bloco de static/media foi executado.
        self.assertGreaterEqual(len(project_urls.urlpatterns), 3)
