import base64
import hashlib
import hmac
import json
import os
import time
from typing import Any, Optional

import httpx
from fastapi import Depends, Header, HTTPException

PBKDF2_ITERATIONS = 200_000
TOKEN_TTL_SECONDS = 12 * 60 * 60  # 12 horas


def _secret_key() -> str:
    key = os.getenv("SECRET_KEY")
    if not key:
        raise RuntimeError("SECRET_KEY no configurado")
    return key


# ── Contraseñas (PBKDF2, sin dependencias externas) ──────────────────────────
def hash_password(password: str) -> str:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PBKDF2_ITERATIONS)
    return f"{PBKDF2_ITERATIONS}${salt.hex()}${dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        iterations_str, salt_hex, hash_hex = stored.split("$")
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), int(iterations_str))
        return hmac.compare_digest(dk.hex(), hash_hex)
    except (ValueError, AttributeError):
        return False


# ── Tokens de sesión (HMAC firmado, sin JWT) ─────────────────────────────────
def create_token(username: str, is_admin: bool, ttl_seconds: int = TOKEN_TTL_SECONDS) -> str:
    payload = {"sub": username, "is_admin": is_admin, "exp": int(time.time()) + ttl_seconds}
    payload_bytes = json.dumps(payload, separators=(",", ":")).encode()
    b64 = base64.urlsafe_b64encode(payload_bytes).rstrip(b"=").decode()
    signature = hmac.new(_secret_key().encode(), payload_bytes, hashlib.sha256).hexdigest()
    return f"{b64}.{signature}"


def verify_token(token: str) -> dict:
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


# ── Tabla `usuarios` en Supabase (unica fuente de persistencia, sobrevive redeploys) ──
def _users_base_url() -> str:
    supabase_url = os.getenv("SUPABASE_URL", "")
    if not supabase_url:
        raise RuntimeError("SUPABASE_URL no configurado")
    return f"{supabase_url.rstrip('/')}/rest/v1/usuarios"


def _users_headers(prefer: Optional[str] = None) -> dict[str, str]:
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    if not key:
        raise RuntimeError("SUPABASE_SERVICE_ROLE_KEY no configurado")
    headers = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    if prefer:
        headers["Prefer"] = prefer
    return headers


async def _users_request(method: str, *, params: Optional[dict[str, str]] = None, payload: Any = None, prefer: Optional[str] = None) -> httpx.Response:
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.request(method, _users_base_url(), headers=_users_headers(prefer), params=params, json=payload)
    if response.status_code >= 400:
        raise RuntimeError(f"Supabase (usuarios) devolvió error: {response.text[:300]}")
    return response


async def get_user_by_username(username: str) -> Optional[dict]:
    resp = await _users_request("GET", params={"username": f"eq.{username}", "select": "*", "limit": "1"})
    rows = resp.json()
    return rows[0] if rows else None


async def create_user(username: str, password: str, is_admin: bool = False) -> dict:
    payload = {"username": username, "password_hash": hash_password(password), "is_admin": is_admin, "is_active": True}
    resp = await _users_request("POST", payload=payload, prefer="return=representation")
    rows = resp.json()
    return rows[0] if rows else payload


async def list_users() -> list[dict]:
    resp = await _users_request("GET", params={"select": "id,username,is_admin,is_active,created_at", "order": "created_at.desc"})
    return resp.json()


async def set_user_active(user_id: str, is_active: bool) -> dict:
    resp = await _users_request("PATCH", params={"id": f"eq.{user_id}"}, payload={"is_active": is_active}, prefer="return=representation")
    rows = resp.json()
    return rows[0] if rows else {}


# ── Dependencias FastAPI ──────────────────────────────────────────────────────
async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No autenticado")
    try:
        return verify_token(authorization[len("Bearer "):])
    except Exception:
        raise HTTPException(status_code=401, detail="Token invalido o vencido")


async def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Requiere permisos de administrador")
    # Revalida en vivo contra Supabase para que un admin desactivado no siga
    # operando con un token todavia vigente.
    db_user = await get_user_by_username(user["sub"])
    if not db_user or not db_user.get("is_admin") or not db_user.get("is_active"):
        raise HTTPException(status_code=403, detail="Requiere permisos de administrador")
    return user


async def bootstrap_admin() -> None:
    """Crea el primer usuario admin desde variables de entorno si la tabla usuarios esta vacia."""
    username = os.getenv("ADMIN_BOOTSTRAP_USERNAME")
    password = os.getenv("ADMIN_BOOTSTRAP_PASSWORD")
    if not username or not password:
        return
    try:
        if await list_users():
            return
        await create_user(username, password, is_admin=True)
        print(f"[auth] Usuario admin inicial creado: {username}")
    except Exception as e:
        print(f"[auth] No se pudo inicializar el admin bootstrap: {e}")
