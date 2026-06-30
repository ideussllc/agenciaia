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
```
