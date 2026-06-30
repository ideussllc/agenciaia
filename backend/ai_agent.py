import json
import os
import re
from typing import Any
import httpx

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/complete"
ANTHROPIC_MODEL = "claude-sonnet-4-6"


def _extract_json(text: str) -> Any:
    text = text.strip()
    if not text:
        raise ValueError("Respuesta vacía de Anthropic")

    # Extraer el primer y último objeto JSON válido.
    first = text.find('{')
    last = text.rfind('}')
    if first == -1 or last == -1 or last < first:
        raise ValueError("No se encontró un objeto JSON válido en la respuesta de Anthropic")

    candidate = text[first:last + 1]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError as exc:
        # Intentar limpiar caracteres inválidos dentro del cuerpo JSON
        candidate = re.sub(r"\n+", " ", candidate)
        candidate = re.sub(r",\s*}\]", "}]", candidate)
        return json.loads(candidate)


async def analyze(data: dict) -> dict:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("La variable de entorno ANTHROPIC_API_KEY no está definida")

    prompt = (
        "You are an expert consultant in automation and AI solutions. Review the following diagnostic responses and generate a high-level review report for management and technical stakeholders. "
        "Return ONLY valid JSON with the exact structure specified. Do not add any commentary, markdown, or any text outside the JSON object."
        "\n\n"
        "INPUT:\n" + json.dumps(data, ensure_ascii=False, indent=2) + "\n\n"
        "RETURN a JSON object EXACTLY like this schema:\n"
        "{\n"
        "  \"estado_actual\": \"Descripcion clara de la situacion actual y contexto en la empresa.\",\n"
        "  \"comparacion_industria\": \"Nivel encontrado comparado con empresas similares del sector.\",\n"
        "  \"oportunidades_mejora\": [\n"
        "    {\"titulo\": \"...\", \"area\": \"...\", \"descripcion\": \"...\", \"prioridad\": \"...\", \"beneficio\": \"...\"}\n"
        "  ],\n"
        "  \"automatizaciones_sugeridas\": [\n"
        "    {\"solucion\": \"...\", \"area\": \"...\", \"impacto\": \"...\", \"prioridad\": \"...\", \"requisitos\": \"...\"}\n"
        "  ],\n"
        "  \"agentes_ia_sugeridos\": [\n"
        "    {\"nombre\": \"...\", \"funcion\": \"...\", \"beneficio\": \"...\", \"implementacion\": \"...\"}\n"
        "  ],\n"
        "  \"oportunidades\": [\n"
        "    {\"opp\": \"...\", \"area\": \"...\", \"tool\": \"...\", \"phase\": \"...\", \"impacto\": \"...\", \"complejidad\": \"...\", \"justificacion\": \"...\"}\n"
        "  ],\n"
        "  \"alertas_ciberseguridad\": [\n"
        "    {\"area\": \"...\", \"riesgo\": \"...\", \"nivel\": \"...\", \"recomendacion\": \"...\"}\n"
        "  ],\n"
        "  \"resumen_ejecutivo\": \"texto de 3 párrafos\",\n"
        "  \"quick_wins\": [\"texto1\", \"texto2\", \"texto3\"]\n"
        "}"
        "\n\nMake sure the JSON uses double quotes and is parseable by standard JSON parsers."
    )

    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key,
    }

    body = {
        "model": ANTHROPIC_MODEL,
        "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
        "max_tokens_to_sample": 1200,
        "temperature": 0.2,
        "stop_sequences": ["\n\nHuman:"],
    }

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(ANTHROPIC_API_URL, headers=headers, json=body)

    if resp.status_code != 200:
        raise RuntimeError(
            f"Anthropic API returned {resp.status_code}: {resp.text}"
        )

    response_data = resp.json()
    completion = response_data.get("completion") or response_data.get("text") or ""
    parsed = _extract_json(completion)

    return parsed
