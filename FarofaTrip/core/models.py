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
    imagem = models.ImageField(upload_to="eventos/", null=True, blank=True)
    ingresso = models.DecimalField(max_digits=8, decimal_places=2)
    excursao = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def __str__(self):
        return self.nome


class Pedido(models.Model):
    STATUS_CHOICES = (
        ("pendente", "Pendente"),
        ("pago", "Pago"),
        ("cancelado", "Cancelado"),
    )

    FORMA_PAGAMENTO_CHOICES = (
        ("cartao", "Cartão"),
        ("pix", "PIX"),
        ("boleto", "Boleto"),
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pedidos",
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pendente",
    )

    forma_pagamento = models.CharField(
        max_length=20,
        choices=FORMA_PAGAMENTO_CHOICES,
        null=True,
        blank=True,
    )

    valor_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    observacoes = models.TextField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"Pedido #{self.id} - {self.status}"

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"


class PedidoItem(models.Model):
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name="itens",
    )

    evento = models.ForeignKey(
        "core.Evento",
        on_delete=models.PROTECT,
        related_name="itens_pedido",
    )

    quantidade = models.PositiveIntegerField(default=1)

    preco_ingresso = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    preco_excursao = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
    )

    def save(self, *args, **kwargs):
        from decimal import Decimal

        ingresso = self.preco_ingresso or Decimal("0.00")
        excursao = self.preco_excursao or Decimal("0.00")
        self.subtotal = (ingresso + excursao) * self.quantidade
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantidade}x {self.evento.nome} (Pedido #{self.pedido_id})"
