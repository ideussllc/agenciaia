import asyncio
import os
from html import escape
from typing import Optional

import httpx

PIPEDRIVE_API_BASE = "https://api.pipedrive.com/v1"
PIPEDRIVE_API_V2_BASE = "https://api.pipedrive.com/v2"

SECTION_PREFIXES = {
    "v": "Ventas",
    "m": "Mercadeo",
    "d": "Delivery / Fulfillment",
    "a": "Administracion",
    "p": "Produccion",
}


def _api_token() -> Optional[str]:
    return os.getenv("PIPEDRIVE_API_TOKEN")


def _humanize(value) -> str:
    if isinstance(value, (list, tuple)):
        return ", ".join(str(item) for item in value)
    return str(value) if value not in (None, "") else "—"


def _normalize_phone(value: str) -> str:
    return "".join(ch for ch in value if ch.isdigit())


async def _find_person_by_email(client: httpx.AsyncClient, api_token: str, email: str) -> Optional[dict]:
    if not email:
        return None
    resp = await client.get(
        f"{PIPEDRIVE_API_BASE}/persons/search",
        params={"api_token": api_token, "term": email, "fields": "email", "exact_match": "true"},
    )
    resp.raise_for_status()
    items = resp.json().get("data", {}).get("items") or []
    return items[0]["item"] if items else None


async def _upsert_person(client: httpx.AsyncClient, api_token: str, name: str, email: str, whatsapp: str) -> int:
    """Busca una Persona existente por correo; si existe, anexa el WhatsApp a su telefono (sin duplicar). Si no, la crea."""
    existing = await _find_person_by_email(client, api_token, email)
    if existing:
        person_id = existing["id"]
        detail_resp = await client.get(f"{PIPEDRIVE_API_BASE}/persons/{person_id}", params={"api_token": api_token})
        detail_resp.raise_for_status()
        phones = [p["value"] for p in (detail_resp.json()["data"].get("phone") or [])]
        if whatsapp and _normalize_phone(whatsapp) not in (_normalize_phone(p) for p in phones):
            phones.append(whatsapp)
            update_resp = await client.put(
                f"{PIPEDRIVE_API_BASE}/persons/{person_id}",
                params={"api_token": api_token},
                json={"phone": phones},
            )
            update_resp.raise_for_status()
        return person_id

    person_payload = {"name": name or "Sin nombre"}
    if email:
        person_payload["email"] = [email]
    if whatsapp:
        person_payload["phone"] = [whatsapp]

    person_resp = await client.post(
        f"{PIPEDRIVE_API_BASE}/persons",
        params={"api_token": api_token},
        json=person_payload,
    )
    person_resp.raise_for_status()
    return person_resp.json()["data"]["id"]


def _build_note_html(
    empresa_nombre: str,
    contacto: str,
    contacto_cargo: str,
    contacto_nivel_decision: str,
    contacto_email: str,
    contacto_whatsapp: str,
    data: dict,
) -> str:
    lines = [
        "<b>Descubrimiento OOIA diligenciado</b>",
        f"Empresa: {escape(empresa_nombre or '—')}",
        f"Contacto: {escape(contacto or '—')}",
        f"Cargo: {escape(contacto_cargo or '—')}",
        f"Nivel de decisión: {escape(contacto_nivel_decision or '—')}",
        f"Correo: {escape(contacto_email or '—')}",
        f"WhatsApp: {escape(contacto_whatsapp or '—')}",
        f"Actividad economica: {escape(_humanize(data.get('empresa_actividad_economica')))}",
        f"Rango de empleados: {escape(_humanize(data.get('empresa_rango_empleados')))}",
        "",
    ]
    for prefix, titulo in SECTION_PREFIXES.items():
        section_fields = {k: v for k, v in data.items() if k.startswith(f"{prefix}_") and v not in (None, "", [])}
        if not section_fields:
            continue
        lines.append(f"<b>{escape(titulo)}</b>")
        for key, value in section_fields.items():
            label = key[len(prefix) + 1:].replace("_", " ").capitalize()
            lines.append(f"- {escape(label)}: {escape(_humanize(value))}")
        lines.append("")
    return "<br>".join(lines)


async def create_lead_for_diagnostico(
    empresa_nombre: str,
    contacto: str,
    contacto_email: str,
    contacto_whatsapp: str,
    data: dict,
    contacto_cargo: str = "",
    contacto_nivel_decision: str = "",
) -> Optional[str]:
    """Crea/actualiza una Persona + Prospecto (Lead) en Pipedrive con una nota resumen. Retorna el lead_id o None si Pipedrive no esta configurado."""
    api_token = _api_token()
    if not api_token:
        return None

    async with httpx.AsyncClient(timeout=30) as client:
        person_id = await _upsert_person(
            client, api_token, contacto or empresa_nombre, contacto_email, contacto_whatsapp
        )

        lead_resp = await client.post(
            f"{PIPEDRIVE_API_BASE}/leads",
            params={"api_token": api_token},
            json={
                "title": f"{empresa_nombre or 'Sin nombre'} prospecto",
                "person_id": person_id,
            },
        )
        lead_resp.raise_for_status()
        lead_id = lead_resp.json()["data"]["id"]

        note_html = _build_note_html(
            empresa_nombre, contacto, contacto_cargo, contacto_nivel_decision, contacto_email, contacto_whatsapp, data
        )
        await add_note("lead_id", lead_id, note_html)

        return lead_id


async def add_note(entity_type: str, entity_id: str, html: str) -> bool:
    """Agrega una nota a un Lead o Deal existente. entity_type es 'lead_id' o 'deal_id'."""
    api_token = _api_token()
    if not api_token or not entity_id:
        return False

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{PIPEDRIVE_API_BASE}/notes",
            params={"api_token": api_token},
            json={"content": html, entity_type: entity_id},
        )
        resp.raise_for_status()
        return True


async def convert_lead_to_deal(lead_id: str, stage_id: int, max_polls: int = 10, poll_interval: float = 1.0) -> Optional[str]:
    """Convierte un Lead en un Deal en la etapa indicada (el pipeline se infiere del stage_id).

    Usa la API v2 de Pipedrive (`POST /leads/{id}/convert/deal`), confirmada contra
    developers.pipedrive.com el 2026-07-23. La conversion es asincrona: se sondea
    `GET /leads/{id}/convert/status/{conversion_id}` hasta que el estado sea 'completed'.
    El nombre del campo `deal_id` en la respuesta de estado esta inferido del texto de
    la documentacion ("Deal ID is only present if the conversion was successfully
    finished") y no fue confirmado contra un payload de ejemplo real - verificar en el
    primer uso en produccion.
    """
    api_token = _api_token()
    if not api_token or not lead_id:
        return None

    async with httpx.AsyncClient(timeout=30) as client:
        convert_resp = await client.post(
            f"{PIPEDRIVE_API_V2_BASE}/leads/{lead_id}/convert/deal",
            params={"api_token": api_token},
            json={"stage_id": stage_id},
        )
        convert_resp.raise_for_status()
        conversion_id = convert_resp.json()["data"]["id"]

        for _ in range(max_polls):
            status_resp = await client.get(
                f"{PIPEDRIVE_API_V2_BASE}/leads/{lead_id}/convert/status/{conversion_id}",
                params={"api_token": api_token},
            )
            status_resp.raise_for_status()
            status_data = status_resp.json().get("data") or {}
            status = status_data.get("status")
            if status == "completed":
                return status_data.get("deal_id")
            if status in ("failed", "rejected"):
                return None
            await asyncio.sleep(poll_interval)

        return None


async def attach_file_to_lead(lead_id: str, file_path: str, filename: str) -> bool:
    """Sube un archivo (por ejemplo el PDF del informe) y lo asocia a un Lead existente."""
    api_token = _api_token()
    if not api_token or not lead_id:
        return False

    async with httpx.AsyncClient(timeout=60) as client:
        with open(file_path, "rb") as f:
            resp = await client.post(
                f"{PIPEDRIVE_API_BASE}/files",
                params={"api_token": api_token},
                data={"lead_id": lead_id},
                files={"file": (filename, f, "application/pdf")},
            )
        resp.raise_for_status()
        return True
