# FarofaTrip/core/whatsapp.py
import os
import requests
from typing import Optional
from django.conf import settings
from .models import Pedido


WHATSAPP_TARGET_DEFAULT = "+5519971173838"


def _get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    return getattr(settings, name, None) or os.getenv(name, default)


def format_order_message(pedido: Pedido) -> str:
    """
    Monta o texto que será enviado pelo WhatsApp com os dados do pedido.
    Ajuste o texto como quiser.
    """
    usuario = pedido.usuario

    header = [
        f"🧾 *Novo pedido #{pedido.id}*",
        "",
    ]

    if usuario:
        header.append(f"👤 Cliente: {usuario.get_full_name() or usuario.username}")
        header.append(f"📧 Email: {usuario.email}")
        header.append("")

    header.append(f"💳 Forma de pagamento: {pedido.forma_pagamento or 'não informada'}")
    header.append(f"💰 Valor total: R$ {pedido.valor_total:.2f}")
    header.append("")

    itens_lines = ["📦 *Itens do pedido:*"]

    for item in pedido.itens.all():
        partes = [f"- {item.quantidade}x {item.evento.nome}"]

        if item.preco_ingresso:
            partes.append(f"ingresso R$ {item.preco_ingresso:.2f}")
        if item.preco_excursao:
            partes.append(f"excursão R$ {item.preco_excursao:.2f}")

        partes.append(f"subtotal R$ {item.subtotal:.2f}")
        itens_lines.append(" | ".join(partes))

    if not pedido.itens.exists():
        itens_lines.append("- (sem itens cadastrados 😅)")

    if pedido.observacoes:
        itens_lines.extend(
            [
                "",
                "📝 Observações:",
                pedido.observacoes,
            ]
        )

    return "\n".join(header + [""] + itens_lines)


def send_whatsapp_order(pedido: Pedido) -> None:
    """
    Envia a mensagem de WhatsApp via WhatsApp Cloud API.

    Requer as variáveis:
      - WHATSAPP_TOKEN       -> token de acesso (Bearer)
      - WHATSAPP_PHONE_ID    -> phone_number_id da API do WhatsApp
      - WHATSAPP_TARGET      -> número destino (opcional, default é o seu)
    """
    token = _get_env("WHATSAPP_TOKEN")
    phone_id = _get_env("WHATSAPP_PHONE_ID")
    to_number = _get_env("WHATSAPP_TARGET", WHATSAPP_TARGET_DEFAULT)

    # Se não tiver configuração, apenas sai silenciosamente
    if not token or not phone_id:
        # aqui poderia logar com logging.warning se quiser
        return

    text_body = format_order_message(pedido)

    url = f"https://graph.facebook.com/v21.0/{phone_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number.replace("+", ""),  # E.164 sem o "+"
        "type": "text",
        "text": {
            "preview_url": False,
            "body": text_body,
        },
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        (...)
        print(f"[WHATSAPP] Erro ao enviar mensagem do pedido #{pedido.id}: {e}")
