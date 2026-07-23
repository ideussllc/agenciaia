import base64
import hashlib
import hmac
import json
import os
import time

CONTINUE_TOKEN_TTL_SECONDS = 7 * 24 * 60 * 60  # 7 dias


def _secret_key() -> str:
    key = os.getenv("SECRET_KEY")
    if not key:
        raise RuntimeError("SECRET_KEY no configurado")
    return key


def sign_continue_token(pipedrive_lead_id: str, diag_id: str, ttl_seconds: int = CONTINUE_TOKEN_TTL_SECONDS) -> str:
    """Firma un token stateless que autoriza avanzar un prospecto al hacer clic en el enlace del correo."""
    payload = {"lead_id": str(pipedrive_lead_id), "diag_id": diag_id, "exp": int(time.time()) + ttl_seconds}
    payload_bytes = json.dumps(payload, separators=(",", ":")).encode()
    b64 = base64.urlsafe_b64encode(payload_bytes).rstrip(b"=").decode()
    signature = hmac.new(_secret_key().encode(), payload_bytes, hashlib.sha256).hexdigest()
    return f"{b64}.{signature}"


def verify_continue_token(token: str) -> dict:
    b64, _, signature = token.partition(".")
    if not signature:
        raise ValueError("Token mal formado")
    payload_bytes = base64.urlsafe_b64decode(b64 + "=" * (-len(b64) % 4))
    expected_signature = hmac.new(_secret_key().encode(), payload_bytes, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected_signature):
        raise ValueError("Firma invalida")
    payload = json.loads(payload_bytes)
    if payload.get("exp", 0) < time.time():
        raise ValueError("Token vencido")
    return payload
