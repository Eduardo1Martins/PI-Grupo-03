import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings


class Perfil(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil"
    )
    cpf = models.CharField(max_length=14, unique=True, null=False, blank=False, db_index=True)
    telefone = models.CharField(max_length=15, blank=True, null=True)
    endereco = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        u = self.user
        nome = (u.get_full_name() or u.username or u.email or f"User {u.id}")
        return f"{nome} ({self.cpf})"


class Evento(models.Model):
    nome = models.CharField(max_length=150)
    local = models.CharField(max_length=150)
    cidade = models.CharField(max_length=100)
    data = models.DateField()
    descricao = models.CharField(max_length=250)
    imagem = models.URLField(max_length=300)
    preco = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.nome} - {self.cidade}"
