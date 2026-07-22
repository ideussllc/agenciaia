"""
IDEUSS — Diagnóstico OOIA
Backend FastAPI
Endpoints: /generate-pdf  /export-notion  /save  /list  /load/{id}
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Any
import uuid, json, os, tempfile, httpx
from datetime import datetime
from pdf_gen import generate as generate_pdf
from ai_agent import analyze


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
os.makedirs(DATA_DIR, exist_ok=True)


# ── Modelos ────────────────────────────────────────────────────────────────────
class DiagnosticoPayload(BaseModel):
    data: dict[str, Any]                   # Todas las respuestas de los formularios
    empresa_nombre: Optional[str] = ""
    empresa_contacto: Optional[str] = ""
    roadmap: Optional[dict] = {}
    analysis_report: Optional[dict[str, Any]] = None


class NotionExportPayload(BaseModel):
    data: dict[str, Any]
    notion_token: str
    notion_page_id: str
    empresa_nombre: Optional[str] = ""


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


def build_record(payload: DiagnosticoPayload, diag_id: str) -> dict[str, Any]:
    return {
        "id": diag_id,
        "empresa": payload.empresa_nombre or "Sin nombre",
        "contacto": payload.empresa_contacto or "",
        "fecha": datetime.now().isoformat(),
        "data": payload.data,
        "roadmap": payload.roadmap,
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


# 1. Guardar diagnóstico
@app.post("/save")
def save_diagnostico(payload: DiagnosticoPayload):
    """Guarda un diagnóstico y retorna su ID."""
    diag_id = str(uuid.uuid4())[:8]
    record = build_record(payload, diag_id)

    if STORAGE_BACKEND == "supabase":
        response = _supabase_request("POST", payload=record, prefer="return=representation")
        rows = response.json()
        inserted = rows[0] if isinstance(rows, list) and rows else record
        return {"id": inserted["id"], "empresa": inserted["empresa"], "fecha": inserted["fecha"]}

    with open(diagnostico_path(diag_id), "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    return {"id": diag_id, "empresa": record["empresa"], "fecha": record["fecha"]}


# 2. Listar diagnósticos guardados
@app.get("/list")
def list_diagnosticos():
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
def load(diag_id: str):
    """Carga un diagnóstico completo por su ID."""
    return load_diagnostico(diag_id)


# 4. Eliminar un diagnóstico
@app.delete("/delete/{diag_id}")
def delete(diag_id: str):
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


# 5. Generar PDF
@app.post("/generate-pdf")
def gen_pdf(payload: DiagnosticoPayload):
    """Genera el PDF del diagnóstico y lo devuelve como descarga."""
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
        return FileResponse(
            tmp,
            media_type="application/pdf",
            filename=filename,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando PDF: {str(e)}")


@app.post("/analyze")
async def analyze_diagnostico(payload: DiagnosticoPayload):
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
async def export_notion(payload: NotionExportPayload):
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
