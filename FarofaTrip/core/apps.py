from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    Configuração principal da aplicação Django 'core'.

    - default_auto_field define o tipo padrão de chave primária.
    - name é o caminho da app dentro do projeto.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
