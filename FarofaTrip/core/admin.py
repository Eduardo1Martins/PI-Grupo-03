from django.contrib import admin
from .models import Usuario, Evento
from .forms import UsuarioForm, EventoForm


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    # Campos que aparecem na listagem
    form = UsuarioForm
    list_display = ('nome', 'cpf', 'telefone', 'endereco')

    # Campos de pesquisa
    search_fields = ('nome', 'cpf')

    # Ordenação padrão
    ordering = ('nome',)

    # Campos exibidos no formulário de edição
    fields = ('nome', 'cpf', 'telefone', 'endereco')

    # Quantos registros aparecem por página
    list_per_page = 30

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    form = EventoForm
    list_display = ('nome', 'local', 'cidade', 'data', 'descricao', 'imagem', 'preco')
    search_fields = ('nome', 'cidade', 'local')
    list_filter = ('cidade', 'data')
    ordering = ('data',)