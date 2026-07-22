# IDEUSS — Sistema de Diagnóstico OOIA

Aplicación para gestionar diagnósticos de procesos empresariales con exportación a PDF y Notion.

## Estructura

```
ideuss-diagnostico/
├── backend/          ← API FastAPI (Python)
│   ├── main.py       ← Endpoints principales
│   ├── pdf_gen.py    ← Generación de PDF con ReportLab
│   └── requirements.txt
├── data/             ← Diagnósticos guardados (JSON)
└── README.md
```

## Arrancar el backend

### 1. Instalar dependencias

```bash
cd backend
pip install -r requirements.txt
```

### 2. Iniciar el servidor

```bash
uvicorn main:app --reload --port 8000
```

El servidor queda disponible en: **http://localhost:8000**

Documentación interactiva (Swagger): **http://localhost:8000/docs**

---

## Endpoints disponibles

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Estado del servidor |
| GET | `/health` | Health check |
| POST | `/save` | Guardar diagnóstico en disco |
| GET | `/list` | Listar todos los diagnósticos guardados |
| GET | `/load/{id}` | Cargar un diagnóstico por ID |
| DELETE | `/delete/{id}` | Eliminar un diagnóstico |
| POST | `/generate-pdf` | Generar y descargar el PDF del informe |
| POST | `/export-notion` | Exportar diagnóstico a Notion |

---

## Ejemplo de uso desde el frontend (fetch)

### Guardar un diagnóstico

```javascript
const res = await fetch('http://localhost:8000/save', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    empresa_nombre: 'Mi Empresa S.A.S.',
    empresa_contacto: 'Juan Pérez',
    data: { v_volumen: 'Entre USD $50.000 y $500.000 / año', ... },
    roadmap: { p0: [], p1: [], p2: [] }
  })
});
const { id } = await res.json();
console.log('Guardado con ID:', id);
```

### Generar PDF

```javascript
const res = await fetch('http://localhost:8000/generate-pdf', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ data: formData, empresa_nombre: 'Mi Empresa' })
});
const blob = await res.blob();
const url = URL.createObjectURL(blob);
window.open(url); // Abre el PDF en el navegador
```

### Exportar a Notion

```javascript
const res = await fetch('http://localhost:8000/export-notion', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    data: formData,
    notion_token: 'secret_xxx...',
    notion_page_id: 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
    empresa_nombre: 'Mi Empresa'
  })
});
const { url } = await res.json();
window.open(url); // Abre la página creada en Notion
```

---

## Próximos pasos sugeridos

1. **Frontend React** — `npm create vite@latest frontend -- --template react`
2. **Migrar formularios** — Un componente por área en `src/forms/`
3. **Agente IA** — Endpoint `/analyze` que llama a Anthropic API y sugiere el roadmap
4. **Autenticación simple** — Proteger endpoints con una API key local

---

## Variables de entorno (opcional)

Crear un archivo `.env` en `/backend`:

```env
ANTHROPIC_API_KEY=sk-ant-...   # Para el agente IA (futuro)
DATA_DIR=../data                # Ruta de almacenamiento de diagnósticos
CORS_ALLOW_ORIGINS=http://localhost:5173
```

Para el frontend, crear `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## Desplegar formulario web para clientes

### 1. Backend (Render/Railway/Fly.io)

1. Publica la carpeta `backend/` como servicio web Python.
2. Comando de arranque sugerido:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

3. Variables de entorno mínimas:

```env
DATA_DIR=../data
CORS_ALLOW_ORIGINS=https://TU-FRONTEND.onrender.com
ANTHROPIC_API_KEY=sk-ant-...   # opcional, solo para /analyze
```

### 2. Frontend (Vercel/Netlify/Render Static)

1. Publica la carpeta `frontend/` como sitio estático Vite.
2. Build command: `npm run build`
3. Publish directory: `dist`
4. Variable de entorno:

```env
VITE_API_BASE_URL=https://TU-BACKEND.onrender.com
```

### 3. Verificación final

1. Abre la URL pública del frontend.
2. Diligencia y guarda un diagnóstico (endpoint `/save`).
3. Prueba descargar PDF (`/generate-pdf`).
4. Si falla por CORS, agrega el dominio exacto del frontend en `CORS_ALLOW_ORIGINS`.

---

## Ruta recomendada: Render (API) + Vercel (Frontend)

### Paso A — Subir el backend a Render

1. En Render, seleccionar **New +** → **Blueprint**.
2. Conectar este repositorio y desplegar usando `render.yaml` (raíz del proyecto).
3. Al terminar, copiar la URL pública del backend (ejemplo: `https://ideuss-diagnostico-api.onrender.com`).
4. En Render, abrir variables del servicio backend y ajustar:

```env
DATA_DIR=../data
CORS_ALLOW_ORIGINS=https://TU-FRONTEND.vercel.app
ANTHROPIC_API_KEY=sk-ant-...   # opcional
```

### Paso B — Subir el frontend a Vercel

1. En Vercel, seleccionar **Add New** → **Project**.
2. Importar este mismo repositorio.
3. Configurar:
  - **Root Directory**: `frontend`
  - **Build Command**: `npm run build`
  - **Output Directory**: `dist`
4. Agregar variable de entorno:

```env
VITE_API_BASE_URL=https://TU-BACKEND.onrender.com
```

5. Desplegar y copiar la URL de Vercel.

### Paso C — Cerrar el loop de CORS

1. Volver a Render.
2. Cambiar `CORS_ALLOW_ORIGINS` por la URL real de Vercel.
3. Guardar y redeploy del backend.

### Archivos ya preparados en este repo

- `render.yaml` (deploy del backend en Render)
- `frontend/vercel.json` (rewrite SPA para evitar 404 al refrescar rutas)
- `frontend/.env.example`
- `backend/.env.example`

---

## Ruta de menor costo (Vercel + Supabase Free)

Si tu proveedor del backend te exige tarjeta para persistencia de disco, usa Supabase como almacenamiento y evita depender de archivos locales.

### 1) Crear proyecto en Supabase (plan Free)

1. Crear proyecto en https://supabase.com
2. Ir a **SQL Editor** y ejecutar:

```sql
create table if not exists public.diagnosticos (
  id text primary key,
  empresa text,
  contacto text,
  fecha timestamptz,
  data jsonb,
  roadmap jsonb
);
```

### 2) Configurar backend para Supabase

Variables en el backend:

```env
STORAGE_BACKEND=supabase
SUPABASE_URL=https://TU-PROYECTO.supabase.co
SUPABASE_SERVICE_ROLE_KEY=tu_service_role_key
SUPABASE_TABLE=diagnosticos
CORS_ALLOW_ORIGINS=https://TU-FRONTEND.vercel.app
ANTHROPIC_API_KEY=sk-ant-...   # opcional
```

Con esto, los endpoints `/save`, `/list`, `/load/{id}` y `/delete/{id}` leen/escriben en Supabase en lugar de `data/*.json`.

### 3) Frontend en Vercel

```env
VITE_API_BASE_URL=https://TU-BACKEND
```

### 4) Verificar

1. Guardar un diagnóstico.
2. Consultar `/list` y validar que aparece.
3. Generar PDF.
