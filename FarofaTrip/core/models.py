import uuid
from decimal import Decimal
from django.db import models


class Usuario(models.Model):
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, unique=True)
    telefone = models.CharField(max_length=15, blank=True, null=True)
    endereco = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.nome} ({self.cpf})"


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
