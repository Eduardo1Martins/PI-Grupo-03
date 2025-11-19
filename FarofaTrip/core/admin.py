from django.contrib import admin
from .models import Perfil, Evento, Pedido

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "cpf", "telefone")
    search_fields = ("cpf", "user__username", "user__email", "user__first_name", "user__last_name")

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ("id", "nome", "cidade", "data", "ingresso", "excursao")
    search_fields = ("nome", "cidade",)

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ("id", "criado_em", "atualizado_em", "status", "forma_pagamento", "valor_total", "observacoes")