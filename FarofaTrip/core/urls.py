from rest_framework.routers import DefaultRouter
from .views import UsuarioViewSet, EventoViewSet

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'eventos', EventoViewSet, basename='evento')

urlpatterns = router.urls
