from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import UsuarioViewSet, EventoViewSet, PedidoViewSet
from core.views import LoginView, RefreshView, LogoutView, RegisterView, ChangePasswordView

# Criação do router padrão do Django REST Framework
router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'eventos', EventoViewSet, basename='evento')
router.register(r'pedidos', PedidoViewSet, basename='pedido')

# URLs da aplicação "core"
urlpatterns = [
    # Rota do painel administrativo do Django
    path('admin/', admin.site.urls),


    # Endpoints de autenticação JWT

    # --- AUTH COM E SEM BARRA FINAL ---
    path("auth/login/",   LoginView.as_view(),   name="api_login"),
    path("auth/login",    LoginView.as_view(),   name="api_login_no_slash"),

    path("auth/refresh/", RefreshView.as_view(), name="api_refresh"),
    path("auth/refresh",  RefreshView.as_view(), name="api_refresh_no_slash"),

    path("auth/logout/",  LogoutView.as_view(),  name="api_logout"),
    path("auth/logout",   LogoutView.as_view(),  name="api_logout_no_slash"),

    path("auth/register/", RegisterView.as_view(), name="api_register"),
    path("auth/register",  RegisterView.as_view(), name="api_register_no_slash"),

    path('auth/change-password/', ChangePasswordView.as_view(), name='api_change_password'),

    path('', include(router.urls)),
]
