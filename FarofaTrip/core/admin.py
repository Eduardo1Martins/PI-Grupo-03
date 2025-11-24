from django.contrib import admin
from .models import Perfil, Evento, Pedido


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    """
    Configura a interface de administração para o modelo Perfil.
    Define quais campos aparecem na listagem e quais podem ser usados na busca.
    """
    # Colunas exibidas na listagem de Perfis
    list_display = ("id", "user", "cpf", "telefone")

    # Campos usados na barra de busca do Django Admin
    search_fields = (
        "cpf",
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
    )


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    """
    Configura a interface de administração para o modelo Evento.
    """
    list_display = ("id", "nome", "cidade", "data", "ingresso", "excursao")
    search_fields = ("nome", "cidade",)


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    """
    Configura a interface de administração para o modelo Pedido.
    """
    list_display = (
        "id",
        "criado_em",
        "atualizado_em",
        "status",
        "forma_pagamento",
        "valor_total",
        "observacoes",
    )
