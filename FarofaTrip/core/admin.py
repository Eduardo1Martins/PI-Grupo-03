from django.contrib import admin
from .models import Perfil, Evento

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "cpf", "telefone")
    search_fields = ("cpf", "user__username", "user__email", "user__first_name", "user__last_name")

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ("id", "nome", "cidade", "data", "preco")
    search_fields = ("nome", "cidade",)
