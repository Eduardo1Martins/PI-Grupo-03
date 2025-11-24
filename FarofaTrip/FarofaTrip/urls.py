from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Lista principal de rotas do projeto
urlpatterns = [
    # Rota do painel administrativo do Django
    path("admin/", admin.site.urls),

    # Inclui todas as rotas da aplicação "core" sob o prefixo /api/
    path("api/", include("core.urls")),
]

# Quando o DEBUG está ativado (modo de desenvolvimento):
# - Permite servir arquivos de mídia (upload de imagens, fotos, banners)
# - MEDIA_URL = URL pública
# - MEDIA_ROOT = pasta onde os arquivos são armazenados
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
