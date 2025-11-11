from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import UsuarioViewSet, EventoViewSet 
from core.views import LoginView, RefreshView, LogoutView, RegisterView

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'eventos', EventoViewSet, basename='evento')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/login/',   LoginView.as_view(),   name='api_login'),
    path('auth/refresh/', RefreshView.as_view(), name='api_refresh'),
    path('auth/logout/',  LogoutView.as_view(),  name='api_logout'),
     path('auth/register/', RegisterView.as_view(), name='api_register'),
    path('', include(router.urls)),
]
