import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings


class Perfil(models.Model):
    """
    Perfil estendido para o usuário padrão do Django.

    - user: relação 1-para-1 com o usuário autenticável.
    - cpf: documento único por perfil.
    - telefone, endereco: dados de contato opcionais.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil"
    )
    cpf = models.CharField(
        max_length=14,
        unique=True,
        null=False,
        blank=False,
        db_index=True,
    )
    telefone = models.CharField(max_length=15, blank=True, null=True)
    endereco = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        """
        Retorna uma representação legível do perfil,
        mostrando nome (ou username/e-mail) + CPF.
        """
        u = self.user
        nome = (u.get_full_name() or u.username or u.email or f"User {u.id}")
        return f"{nome} ({self.cpf})"


class Evento(models.Model):
    """
    Representa um evento disponível para venda de ingressos/excursão.

    - nome, local, cidade, data, descricao: informações básicas do evento.
    - imagem: banner do evento (upload em 'eventos/').
    - ingresso: valor base do ingresso.
    - excursao: valor opcional para excursão/vans/etc.
    """
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
    """
    Representa um pedido de compra, contendo um ou mais itens de eventos.

    - usuario: usuário que fez o pedido (pode ser nulo, ex: pedido anônimo/futuro).
    - status: estado do pedido (pendente, pago, cancelado).
    - forma_pagamento: como o pedido foi/será pago (cartão, pix, boleto).
    - valor_total: soma dos subtotais dos itens.
    - observacoes: campo livre para comentários internos.
    """
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

    # Datas de criação/atualização do pedido
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
        # Ordena pedidos do mais recente para o mais antigo
        ordering = ["-criado_em"]
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"


class PedidoItem(models.Model):
    """
    Item associado a um Pedido.

    - pedido: referência ao pedido pai.
    - evento: evento comprado.
    - quantidade: número de ingressos/excursões.
    - preco_ingresso / preco_excursao: valores unitários usados no cálculo.
    - subtotal: valor total do item (calculado em save()).
    """
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
        """
        Calcula o subtotal antes de salvar:
        (preco_ingresso + preco_excursao) * quantidade.

        Valores nulos são tratados como 0.00.
        """
        from decimal import Decimal

        ingresso = self.preco_ingresso or Decimal("0.00")
        excursao = self.preco_excursao or Decimal("0.00")
        self.subtotal = (ingresso + excursao) * self.quantidade
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantidade}x {self.evento.nome} (Pedido #{self.pedido_id})"
