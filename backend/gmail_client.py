import base64
import os
import time
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional, Sequence, Tuple

import httpx

GMAIL_TOKEN_URL = "https://oauth2.googleapis.com/token"
GMAIL_API_BASE = "https://gmail.googleapis.com/gmail/v1/users/me"

_token_cache: dict = {"access_token": None, "expires_at": 0}


async def _get_access_token() -> Optional[str]:
    """Refresca (y cachea en memoria por su vigencia) el access token de Gmail a partir del refresh token."""
    refresh_token = os.getenv("GMAIL_REFRESH_TOKEN")
    if not refresh_token:
        return None

    if _token_cache["access_token"] and _token_cache["expires_at"] > time.time() + 30:
        return _token_cache["access_token"]

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(
            GMAIL_TOKEN_URL,
            data={
                "client_id": os.getenv("GMAIL_CLIENT_ID", ""),
                "client_secret": os.getenv("GMAIL_CLIENT_SECRET", ""),
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
        )
    resp.raise_for_status()
    token_data = resp.json()
    _token_cache["access_token"] = token_data["access_token"]
    _token_cache["expires_at"] = time.time() + token_data.get("expires_in", 3600)
    return _token_cache["access_token"]


def _build_mime_message(
    to_email: str,
    subject: str,
    html_body: str,
    attachments: Optional[Sequence[Tuple[str, str]]] = None,
) -> bytes:
    """attachments es una lista de (file_path, filename)."""
    message = MIMEMultipart("mixed")
    message["To"] = to_email
    message["From"] = os.getenv("GMAIL_SENDER", "")
    message["Subject"] = subject
    message.attach(MIMEText(html_body, "html"))

    for attachment_path, attachment_filename in attachments or []:
        with open(attachment_path, "rb") as f:
            attachment = MIMEApplication(f.read(), _subtype="pdf")
        attachment.add_header("Content-Disposition", "attachment", filename=attachment_filename or "adjunto.pdf")
        message.attach(attachment)

    return message.as_bytes()


async def create_draft(
    to_email: str,
    subject: str,
    html_body: str,
    attachments: Optional[Sequence[Tuple[str, str]]] = None,
) -> Optional[str]:
    """Crea un borrador (no lo envia) en la bandeja de GMAIL_SENDER. Retorna el draft_id o None si Gmail no esta configurado."""
    if not to_email:
        return None

    access_token = await _get_access_token()
    if not access_token:
        return None

    raw = base64.urlsafe_b64encode(_build_mime_message(to_email, subject, html_body, attachments)).decode()

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{GMAIL_API_BASE}/drafts",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"message": {"raw": raw}},
        )
    resp.raise_for_status()
    return resp.json().get("id")


def build_roadmap_invitation_html(empresa_nombre: str, contacto: str, cargo: str, continue_url: str) -> str:
    saludo = contacto or (f"equipo de {empresa_nombre}" if empresa_nombre else "equipo")
    saludo_cargo = f" ({cargo})" if cargo else ""
    return f"""
    <div style="font-family: Arial, sans-serif; color: #101828; line-height: 1.6;">
      <p>Hola {saludo}{saludo_cargo},</p>
      <p>Adjunto el informe de Descubrimiento OOIA para <strong>{empresa_nombre or 'tu empresa'}</strong>, con los hallazgos y oportunidades identificadas.</p>
      <p>El siguiente paso natural es la <strong>Fase 1 — Descubrimiento y Estrategia</strong>, cuyo entregable es un <strong>Road Map estratégico</strong> con alcance, fases y tiempos de implementación. Tenemos dos alternativas según la profundidad que necesites:</p>
      <ul>
        <li><strong>Contextualización 1 área crítica</strong> — USD $2.500 (2 semanas)</li>
        <li><strong>Contextualización completa, hasta 4 áreas</strong> — USD $8.900 (6-8 semanas)</li>
      </ul>
      <p>Condiciones de pago: 50% al inicio, 30% a 30 días y saldo a 60 días. Opción de facturar en COP al TRM del día.</p>
      <p style="background:#FFF7ED; border:1px solid #F6D1A8; border-radius:12px; padding:12px 16px;">
        🎁 <strong>Bono:</strong> si eliges a IDEUSS como implementador del Road Map, el 50% de esta inversión se descuenta directamente de la propuesta de implementación.
      </p>
      <p>Si quieres continuar, confírmalo aquí:</p>
      <p>
        <a href="{continue_url}" style="display:inline-block; background:#F28C18; color:#ffffff; text-decoration:none; padding:12px 20px; border-radius:24px; font-weight:bold;">
          Quiero continuar
        </a>
      </p>
      <p>Cualquier duda, con gusto la resolvemos.</p>
      <p>Equipo IDEUSS</p>
    </div>
    """


def build_payment_instructions_html(empresa_nombre: str, contacto: str) -> str:
    saludo = contacto or (f"equipo de {empresa_nombre}" if empresa_nombre else "equipo")
    return f"""
    <div style="font-family: Arial, sans-serif; color: #101828; line-height: 1.6;">
      <p>Hola {saludo},</p>
      <p>¡Gracias por confirmar que quieren continuar con la Fase 1 — Descubrimiento y Estrategia para <strong>{empresa_nombre or 'su empresa'}</strong>!</p>
      <p>Aquí las instrucciones de pago según el origen del pago:</p>
      <div style="display:flex; gap:16px; flex-wrap:wrap;">
        <div style="flex:1; min-width:220px; background:#FFF7ED; border:1px solid #F6D1A8; border-radius:12px; padding:16px;">
          <p style="margin:0 0 8px; font-weight:bold;">Pagos en Colombia (COP)</p>
          <p style="margin:0;">ePayco — [PENDIENTE: enlace/cuenta ePayco]</p>
        </div>
        <div style="flex:1; min-width:220px; background:#F0F9FF; border:1px solid #BAE6FD; border-radius:12px; padding:16px;">
          <p style="margin:0 0 8px; font-weight:bold;">Pagos fuera de Colombia (USD)</p>
          <p style="margin:0;">Stripe — [PENDIENTE: enlace/cuenta Stripe]</p>
        </div>
      </div>
      <p>Condiciones: 50% al inicio, 30% a 30 días y saldo a 60 días.</p>
      <p>Cualquier duda, con gusto la resolvemos.</p>
      <p>Equipo IDEUSS</p>
    </div>
    """
