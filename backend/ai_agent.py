import json
import os
import re
from typing import Any

from anthropic import AsyncAnthropic

MODEL = "claude-opus-4-8"

SYSTEM_PROMPT = (
    "Eres un agente experto en optimización y automatización de procesos empresariales, "
    "con amplia experiencia asesorando empresas en transformación digital e inteligencia artificial aplicada. "
    "Respondes siempre en español, con un tono estratégico y orientado a resultados de negocio."
)


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
    except json.JSONDecodeError:
        # Intentar limpiar caracteres inválidos dentro del cuerpo JSON
        candidate = re.sub(r"\n+", " ", candidate)
        candidate = re.sub(r",\s*}\]", "}]", candidate)
        return json.loads(candidate)


async def analyze(data: dict) -> dict:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("La variable de entorno ANTHROPIC_API_KEY no está definida")

    client = AsyncAnthropic(api_key=api_key)

    perfil_empresa = {
        "actividad_economica": data.get("empresa_actividad_economica", ""),
        "numero_empleados": data.get("empresa_rango_empleados", ""),
        "cliente_ideal": data.get("m_buyer", ""),
        "propuesta_valor": data.get("m_prop", ""),
        "dolores_por_proceso": {
            "ventas": data.get("v_dolor", ""),
            "mercadeo": data.get("m_dolor", ""),
            "delivery": data.get("d_dolor", ""),
            "administracion": data.get("a_dolor", ""),
            "produccion": data.get("p_dolor", ""),
        },
    }

    prompt = (
        "Revisa las siguientes respuestas de un diagnóstico de descubrimiento operativo y genera un "
        "informe estratégico de alto nivel para gerencia y equipo técnico.\n\n"
        "RESPUESTAS DEL DESCUBRIMIENTO:\n" + json.dumps(data, ensure_ascii=False, indent=2) + "\n\n"
        "PERFIL DE LA EMPRESA (para la sección de casos de uso):\n"
        + json.dumps(perfil_empresa, ensure_ascii=False, indent=2) + "\n\n"
        "Para la sección \"casos_uso_aplicados\": realiza una investigación profunda (usa la herramienta de "
        "búsqueda web) sobre casos de uso reales de inteligencia artificial en el mundo empresarial, teniendo "
        "en cuenta la actividad económica, el número de empleados, el cliente ideal, la propuesta de valor y "
        "los dolores reportados en cada proceso (ventas, mercadeo, delivery, administración, producción) "
        "descritos en el perfil de la empresa. Prioriza casos de uso que atiendan directamente los procesos con "
        "dolores reportados. Reporta entre 3 y 5 casos de uso concretos y aplicados que la empresa podría "
        "considerar implementar para mejorar sus niveles de productividad y rentabilidad.\n\n"
        "Devuelve ÚNICAMENTE un objeto JSON válido con la siguiente estructura exacta. No agregues comentarios, "
        "markdown, ni ningún texto fuera del objeto JSON.\n\n"
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
        "  \"casos_uso_aplicados\": [\n"
        "    {\"caso\": \"...\", \"proceso_relacionado\": \"...\", \"descripcion\": \"...\", \"sector_referencia\": \"...\", \"impacto_esperado\": \"...\"}\n"
        "  ],\n"
        "  \"oportunidades\": [\n"
        "    {\"opp\": \"...\", \"area\": \"...\", \"tool\": \"...\", \"phase\": \"...\", \"impacto\": \"...\", \"complejidad\": \"...\", \"justificacion\": \"...\"}\n"
        "  ],\n"
        "  \"alertas_ciberseguridad\": [\n"
        "    {\"area\": \"...\", \"riesgo\": \"...\", \"nivel\": \"...\", \"recomendacion\": \"...\"}\n"
        "  ],\n"
        "  \"resumen_ejecutivo\": \"texto de 3 párrafos\",\n"
        "  \"quick_wins\": [\"texto1\", \"texto2\", \"texto3\"]\n"
        "}\n\n"
        "Asegúrate de que el JSON use comillas dobles y sea parseable por un parser JSON estándar."
    )

    response = await client.messages.create(
        model=MODEL,
        max_tokens=12000,
        thinking={"type": "adaptive"},
        output_config={"effort": "high"},
        system=SYSTEM_PROMPT,
        tools=[{"type": "web_search_20260209", "name": "web_search", "max_uses": 8}],
        messages=[{"role": "user", "content": prompt}],
    )

    completion = "\n".join(block.text for block in response.content if block.type == "text")
    if not completion.strip():
        raise RuntimeError("Anthropic no devolvió contenido de texto en la respuesta")

    return _extract_json(completion)
