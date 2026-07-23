"""
IDEUSS — Diagnóstico OOIA
Backend FastAPI
Endpoints: /generate-pdf  /export-notion  /save  /list  /load/{id}
"""

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Any
import uuid, json, os, tempfile, httpx
from datetime import datetime
from pdf_gen import generate as generate_pdf
from ai_agent import analyze
import auth
import gmail_client
import pipedrive
import tokens


def _parse_allowed_origins(origins_raw: str | None) -> list[str]:
    if not origins_raw:
        return ["*"]
    origins = [origin.strip() for origin in origins_raw.split(",") if origin.strip()]
    return origins or ["*"]


def _resolve_data_dir() -> str:
    configured = os.getenv("DATA_DIR", "../data")
    if os.path.isabs(configured):
        return configured
    return os.path.abspath(os.path.join(os.path.dirname(__file__), configured))


def _normalize_storage_backend(raw_backend: str | None) -> str:
    backend = (raw_backend or "file").strip().lower()
    if backend not in {"file", "supabase"}:
        return "file"
    return backend


def _supabase_base_url() -> str:
    if not SUPABASE_URL:
        raise HTTPException(status_code=500, detail="SUPABASE_URL no configurado")
    return f"{SUPABASE_URL.rstrip('/')}/rest/v1/{SUPABASE_TABLE}"


def _supabase_headers(prefer: str | None = None) -> dict[str, str]:
    if not SUPABASE_SERVICE_ROLE_KEY:
        raise HTTPException(status_code=500, detail="SUPABASE_SERVICE_ROLE_KEY no configurado")
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
    }
    if prefer:
        headers["Prefer"] = prefer
    return headers


def _supabase_request(method: str, *, params: Optional[dict[str, str]] = None, payload: Any = None, prefer: str | None = None) -> httpx.Response:
    url = _supabase_base_url()
    headers = _supabase_headers(prefer)
    try:
        response = httpx.request(method, url, headers=headers, params=params, json=payload, timeout=20)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Error de conexión con Supabase: {exc}")

    if response.status_code >= 400:
        detail = response.text[:300] if response.text else "Error de Supabase"
        raise HTTPException(status_code=500, detail=f"Supabase devolvió error: {detail}")
    return response

# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(title="IDEUSS Diagnóstico API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_parse_allowed_origins(os.getenv("CORS_ALLOW_ORIGINS")),
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = _resolve_data_dir()
STORAGE_BACKEND = _normalize_storage_backend(os.getenv("STORAGE_BACKEND"))
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
SUPABASE_TABLE = os.getenv("SUPABASE_TABLE", "diagnosticos")
BACKEND_PUBLIC_URL = os.getenv("BACKEND_PUBLIC_URL", "http://localhost:8000").rstrip("/")
# Etapa "Triaje" del pipeline "AI Agency & Automation" en Pipedrive (confirmado via API 2026-07-23).
PIPEDRIVE_TRIAJE_STAGE_ID = int(os.getenv("PIPEDRIVE_TRIAJE_STAGE_ID", "109"))
os.makedirs(DATA_DIR, exist_ok=True)


@app.on_event("startup")
async def _bootstrap_admin_on_startup():
    await auth.bootstrap_admin()


# ── Modelos ────────────────────────────────────────────────────────────────────
class DiagnosticoPayload(BaseModel):
    data: dict[str, Any]                   # Todas las respuestas de los formularios
    empresa_nombre: Optional[str] = ""
    empresa_contacto: Optional[str] = ""
    roadmap: Optional[dict] = {}
    analysis_report: Optional[dict[str, Any]] = None
    pipedrive_lead_id: Optional[str] = None
    diag_id: Optional[str] = None


class NotionExportPayload(BaseModel):
    data: dict[str, Any]
    notion_token: str
    notion_page_id: str
    empresa_nombre: Optional[str] = ""


class LoginPayload(BaseModel):
    username: str
    password: str


class CreateUserPayload(BaseModel):
    username: str
    password: str
    is_admin: bool = False


class SetUserActivePayload(BaseModel):
    is_active: bool


# ── Helpers ────────────────────────────────────────────────────────────────────
def diagnostico_path(diag_id: str) -> str:
    return os.path.join(DATA_DIR, f"{diag_id}.json")


def load_diagnostico(diag_id: str) -> dict:
    if STORAGE_BACKEND == "supabase":
        response = _supabase_request(
            "GET",
            params={"id": f"eq.{diag_id}", "select": "*", "limit": "1"},
        )
        rows = response.json()
        if not rows:
            raise HTTPException(status_code=404, detail=f"Diagnóstico '{diag_id}' no encontrado")
        return rows[0]

    path = diagnostico_path(diag_id)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"Diagnóstico '{diag_id}' no encontrado")
    with open(path) as f:
        return json.load(f)


def build_record(payload: DiagnosticoPayload, diag_id: str, pipedrive_lead_id: Optional[str] = None) -> dict[str, Any]:
    return {
        "id": diag_id,
        "empresa": payload.empresa_nombre or "Sin nombre",
        "contacto": payload.empresa_contacto or "",
        "fecha": datetime.now().isoformat(),
        "data": payload.data,
        "roadmap": payload.roadmap,
        "pipedrive_lead_id": pipedrive_lead_id,
    }


# ── Endpoints ──────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "ok", "service": "IDEUSS Diagnóstico API v1.0"}


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "storage_backend": STORAGE_BACKEND,
    }


# ── Autenticación ──────────────────────────────────────────────────────────────
@app.post("/auth/login")
async def login(payload: LoginPayload):
    """Valida usuario/contraseña contra Supabase y retorna un token firmado."""
    user = await auth.get_user_by_username(payload.username)
    if not user or not user.get("is_active") or not auth.verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    token = auth.create_token(user["username"], user.get("is_admin", False))
    return {
        "token": token,
        "username": user["username"],
        "is_admin": user.get("is_admin", False),
        "expires_at": auth.verify_token(token)["exp"],
    }


@app.get("/auth/me")
async def me(user: dict = Depends(auth.get_current_user)):
    return user


@app.get("/admin/users")
async def admin_list_users(admin: dict = Depends(auth.require_admin)):
    return {"users": await auth.list_users()}


@app.post("/admin/users")
async def admin_create_user(payload: CreateUserPayload, admin: dict = Depends(auth.require_admin)):
    if await auth.get_user_by_username(payload.username):
        raise HTTPException(status_code=409, detail="El usuario ya existe")
    user = await auth.create_user(payload.username, payload.password, payload.is_admin)
    return {"id": user.get("id"), "username": user.get("username"), "is_admin": user.get("is_admin"), "is_active": user.get("is_active")}


@app.patch("/admin/users/{user_id}")
async def admin_set_user_active(user_id: str, payload: SetUserActivePayload, admin: dict = Depends(auth.require_admin)):
    user = await auth.set_user_active(user_id, payload.is_active)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


# 1. Guardar diagnóstico
@app.post("/save")
async def save_diagnostico(payload: DiagnosticoPayload, user: dict = Depends(auth.get_current_user)):
    """Guarda un diagnóstico, crea el prospecto en Pipedrive (si esta configurado) y retorna su ID."""
    diag_id = str(uuid.uuid4())[:8]

    pipedrive_lead_id = None
    try:
        pipedrive_lead_id = await pipedrive.create_lead_for_diagnostico(
            empresa_nombre=payload.empresa_nombre or "",
            contacto=payload.empresa_contacto or "",
            contacto_email=payload.data.get("empresa_contacto_email", ""),
            contacto_whatsapp=payload.data.get("empresa_contacto_whatsapp", ""),
            data=payload.data,
            contacto_cargo=payload.data.get("empresa_contacto_cargo", ""),
            contacto_nivel_decision=payload.data.get("empresa_contacto_nivel_decision", ""),
        )
    except Exception as e:
        print(f"[pipedrive] Error creando prospecto: {e}")

    record = build_record(payload, diag_id, pipedrive_lead_id)

    if STORAGE_BACKEND == "supabase":
        response = _supabase_request("POST", payload=record, prefer="return=representation")
        rows = response.json()
        inserted = rows[0] if isinstance(rows, list) and rows else record
        return {"id": inserted["id"], "empresa": inserted["empresa"], "fecha": inserted["fecha"], "pipedrive_lead_id": pipedrive_lead_id}

    with open(diagnostico_path(diag_id), "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    return {"id": diag_id, "empresa": record["empresa"], "fecha": record["fecha"], "pipedrive_lead_id": pipedrive_lead_id}


# 2. Listar diagnósticos guardados
@app.get("/list")
def list_diagnosticos(user: dict = Depends(auth.get_current_user)):
    """Retorna todos los diagnósticos guardados."""
    if STORAGE_BACKEND == "supabase":
        response = _supabase_request(
            "GET",
            params={"select": "id,empresa,contacto,fecha", "order": "fecha.desc"},
        )
        rows = response.json()
        return {"diagnosticos": rows, "total": len(rows)}

    items = []
    for fname in sorted(os.listdir(DATA_DIR), reverse=True):
        if fname.endswith(".json"):
            try:
                with open(os.path.join(DATA_DIR, fname)) as f:
                    rec = json.load(f)
                items.append({
                    "id": rec.get("id"),
                    "empresa": rec.get("empresa", "—"),
                    "contacto": rec.get("contacto", "—"),
                    "fecha": rec.get("fecha", "—"),
                })
            except Exception:
                pass
    return {"diagnosticos": items, "total": len(items)}


# 3. Cargar un diagnóstico por ID
@app.get("/load/{diag_id}")
def load(diag_id: str, user: dict = Depends(auth.get_current_user)):
    """Carga un diagnóstico completo por su ID."""
    return load_diagnostico(diag_id)


# 4. Eliminar un diagnóstico
@app.delete("/delete/{diag_id}")
def delete(diag_id: str, user: dict = Depends(auth.get_current_user)):
    if STORAGE_BACKEND == "supabase":
        response = _supabase_request(
            "DELETE",
            params={"id": f"eq.{diag_id}", "select": "id"},
            prefer="return=representation",
        )
        rows = response.json()
        if not rows:
            raise HTTPException(status_code=404, detail="No encontrado")
        return {"deleted": diag_id}

    path = diagnostico_path(diag_id)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="No encontrado")
    os.remove(path)
    return {"deleted": diag_id}


# 5. Generar y enviar el informe: adjunta el PDF al prospecto en Pipedrive y prepara un
#    borrador de correo con la propuesta de Roadmap (no se descarga directamente).
@app.post("/generate-pdf")
async def gen_pdf(payload: DiagnosticoPayload, user: dict = Depends(auth.get_current_user)):
    """Genera el PDF del diagnóstico, lo asocia al prospecto en Pipedrive y crea el borrador de invitación al Roadmap."""
    merged = {
        **payload.data,
        "empresa_nombre": payload.empresa_nombre,
        "empresa_contacto": payload.empresa_contacto,
        "roadmap": payload.roadmap,
        "analysis_report": payload.analysis_report,
    }
    empresa_slug = (payload.empresa_nombre or "diagnostico").replace(" ", "_")[:30]
    fecha_slug = datetime.now().strftime("%Y%m%d")
    filename = f"Diagnostico_OOIA_{empresa_slug}_{fecha_slug}.pdf"

    tmp = tempfile.mktemp(suffix=".pdf")
    try:
        generate_pdf(merged, tmp)

        lead_id = payload.pipedrive_lead_id
        gmail_draft_id = None
        try:
            if not lead_id:
                lead_id = await pipedrive.create_lead_for_diagnostico(
                    empresa_nombre=payload.empresa_nombre or "",
                    contacto=payload.empresa_contacto or "",
                    contacto_email=payload.data.get("empresa_contacto_email", ""),
                    contacto_whatsapp=payload.data.get("empresa_contacto_whatsapp", ""),
                    data=payload.data,
                    contacto_cargo=payload.data.get("empresa_contacto_cargo", ""),
                    contacto_nivel_decision=payload.data.get("empresa_contacto_nivel_decision", ""),
                )
            if lead_id:
                await pipedrive.attach_file_to_lead(lead_id, tmp, filename)

            if lead_id and payload.diag_id:
                continue_url = f"{BACKEND_PUBLIC_URL}/continue/{tokens.sign_continue_token(lead_id, payload.diag_id)}"
                gmail_draft_id = await gmail_client.create_draft(
                    to_email=payload.data.get("empresa_contacto_email", ""),
                    subject=f"Propuesta OOIA — {payload.empresa_nombre or 'tu empresa'}",
                    html_body=gmail_client.build_roadmap_invitation_html(
                        payload.empresa_nombre or "",
                        payload.empresa_contacto or "",
                        payload.data.get("empresa_contacto_cargo", ""),
                        continue_url,
                    ),
                    attachment_path=tmp,
                    attachment_filename=filename,
                )
                if gmail_draft_id:
                    await pipedrive.add_note(
                        "lead_id", lead_id, "Invitación de Roadmap enviada por correo (borrador creado en ventas@ideuss.com)."
                    )
        except Exception as e:
            print(f"[generate-pdf] Error preparando el envío: {e}")

        return JSONResponse({"success": True, "lead_id": lead_id, "gmail_draft_id": gmail_draft_id})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando PDF: {str(e)}")
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


# Enlace "Quiero continuar" del correo de invitación al Roadmap: convierte el Lead en
# Deal en la etapa Triaje y dispara el correo con las instrucciones de pago.
@app.get("/continue/{token}")
async def continue_from_email(token: str):
    try:
        claims = tokens.verify_continue_token(token)
    except Exception:
        return HTMLResponse(
            "<h1>Enlace no válido o vencido</h1><p>Por favor contáctanos para reenviarte la invitación.</p>",
            status_code=400,
        )

    try:
        deal_id = await pipedrive.convert_lead_to_deal(claims["lead_id"], PIPEDRIVE_TRIAJE_STAGE_ID)

        record = load_diagnostico(claims["diag_id"])
        empresa = record.get("empresa", "")
        contacto = record.get("contacto", "")
        contacto_email = (record.get("data") or {}).get("empresa_contacto_email", "")

        if deal_id:
            await pipedrive.add_note("deal_id", deal_id, "Prospecto confirmó interés — instrucciones de pago enviadas.")

        await gmail_client.create_draft(
            to_email=contacto_email,
            subject=f"Instrucciones de pago — {empresa or 'tu empresa'}",
            html_body=gmail_client.build_payment_instructions_html(empresa, contacto),
        )
    except Exception as e:
        print(f"[continue] Error procesando confirmación: {e}")

    return HTMLResponse("<h1>¡Gracias!</h1><p>Hemos recibido tu confirmación. Nuestro equipo te contactará en breve.</p>")


@app.post("/analyze")
async def analyze_diagnostico(payload: DiagnosticoPayload, user: dict = Depends(auth.get_current_user)):
    """Analiza el diagnóstico con Anthropic y retorna JSON estructurado."""
    try:
        result = await analyze({
            **payload.data,
            "empresa_nombre": payload.empresa_nombre,
            "empresa_contacto": payload.empresa_contacto,
            "roadmap": payload.roadmap,
        })
        return JSONResponse(content=result)
    except EnvironmentError as env_err:
        raise HTTPException(status_code=500, detail=str(env_err))
    except ValueError as val_err:
        raise HTTPException(status_code=502, detail=str(val_err))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analizando diagnostico: {str(e)}")


# 6. Exportar a Notion
@app.post("/export-notion")
async def export_notion(payload: NotionExportPayload, user: dict = Depends(auth.get_current_user)):
    """Crea una página en Notion con el diagnóstico completo."""
    data = payload.data
    empresa = payload.empresa_nombre or data.get("empresa_nombre", "Empresa")
    fecha = datetime.now().strftime("%d/%m/%Y")

    def block(btype, text, props=None):
        b = {"object": "block", "type": btype,
             btype: {"rich_text": [{"type": "text", "text": {"content": text[:2000]}}]}}
        if props:
            b[btype].update(props)
        return b

    def h1(t): return block("heading_1", t)
    def h2(t): return block("heading_2", t)
    def h3(t): return block("heading_3", t)
    def p(t):  return block("paragraph", t) if t else block("paragraph", "Sin respuesta registrada.")
    def divider(): return {"object": "block", "type": "divider", "divider": {}}
    def callout(t, emoji="💡"):
        return {"object": "block", "type": "callout",
                "callout": {"rich_text": [{"type": "text", "text": {"content": t[:2000]}}],
                            "icon": {"type": "emoji", "emoji": emoji}}}

    area_data = [
        ("Ventas", "v", "💰"), ("Mercadeo", "m", "📢"),
        ("Delivery", "d", "🚚"), ("Administración", "a", "📋"),
        ("Producción", "p", "⚙️"),
    ]

    children = [
        h1(f"Diagnóstico OOIA — {empresa}"),
        p(f"Fecha: {fecha}  |  Contacto: {data.get('empresa_contacto','—')}"),
        divider(),
        h2("📊 Resumen — Dolores por área"),
    ]

    for area, px, emoji in area_data:
        dolor = data.get(f"{px}_dolor", "Sin respuesta")
        children.append(callout(f"{area}: {dolor}", emoji))

    children += [
        divider(),
        h2("🤖 Automatización e IA por área"),
    ]
    for area, px, _ in area_data:
        auto = data.get(f"{px}_auto_yn", "—")
        ia   = data.get(f"{px}_ia_yn", "—")
        det  = data.get(f"{px}_ia_detalle", "")
        children.append(p(f"{area} — Automatización: {auto}  |  IA: {ia}"))
        if det:
            children.append(p(f"   Detalle IA: {det}"))

    roadmap = data.get("roadmap", {})
    children += [divider(), h2("🗺️ Roadmap de implementación")]
    for label, key, emoji in [("⚡ Fase 0 — Quick wins","p0",""), ("🏗️ Fase 1 — Estructurales","p1",""), ("🚀 Fase 2 — Estratégicos","p2","")]:
        children.append(h3(label))
        for r in roadmap.get(key, []):
            if r.get("opp"):
                children.append(p(f"• {r['opp']} | {r.get('area','—')} | {r.get('tool','—')} | {r.get('time','—')} | USD {r.get('cost','—')}"))

    children += [
        divider(),
        h2("🎯 Criterios de éxito (KPIs)"),
    ]
    for area, px, _ in area_data:
        children.append(p(f"{area}: {data.get(f'{px}_exito','Sin respuesta')}"))

    children += [
        divider(),
        h2("📝 Notas para el dibujo BPMN"),
    ]
    for area, px, emoji in area_data:
        auto = data.get(f"{px}_auto_yn", "—")
        children.append(callout(
            f"{area} — Automatizaciones existentes: {auto}. Iniciar BPMN desde el dolor: {data.get(f'{px}_dolor','—')[:120]}",
            "📌"
        ))

    page_id = payload.notion_page_id.replace("-", "").strip()
    headers = {
        "Authorization": f"Bearer {payload.notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }
    body = {
        "parent": {"page_id": page_id},
        "icon": {"type": "emoji", "emoji": "📊"},
        "properties": {
            "title": {"title": [{"type": "text", "text": {"content": f"Diagnóstico OOIA — {empresa} — {fecha}"}}]}
        },
        "children": children[:100],
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post("https://api.notion.com/v1/pages", json=body, headers=headers)

    if resp.status_code == 200:
        result = resp.json()
        return {"success": True, "url": result.get("url", ""), "id": result.get("id", "")}
    else:
        error = resp.json()
        raise HTTPException(status_code=resp.status_code,
                            detail=error.get("message", "Error de Notion API"))
