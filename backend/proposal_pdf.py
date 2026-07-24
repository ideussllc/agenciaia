import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import HRFlowable, Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

import pricing
from pdf_gen import BORDER, DARK, GRAY, LGRAY, ORANGE, S, WHITE, section_header

DEFAULT_TIER = {"area_1": 2500, "area_4": 8900, "produccion_addon": 2000}

MESES_ES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]


def _fecha_es(dt: datetime) -> str:
    return f"{dt.day} de {MESES_ES[dt.month - 1]} de {dt.year}"


def _fmt_usd(amount: int) -> str:
    return "USD ${:,.0f}".format(amount).replace(",", ".")


def generate(data: dict, output_path: str) -> str:
    """Genera la Propuesta Comercial Fase 1 (Descubrimiento y Estrategia), personalizada con
    los datos de la empresa/contacto y con precios segun el rango de ventas anuales reportado."""
    empresa = data.get("empresa_nombre") or "[Empresa]"
    contacto = data.get("empresa_contacto") or ""
    moneda = data.get("empresa_moneda", "COP")
    rango_ventas = data.get("empresa_rango_ventas_cop", "")
    fecha = _fecha_es(datetime.now())

    tier = pricing.get_pricing(moneda, rango_ventas) or DEFAULT_TIER
    precio_1_area = _fmt_usd(tier["area_1"])
    precio_4_areas = _fmt_usd(tier["area_4"])
    precio_produccion = _fmt_usd(tier["produccion_addon"])
    credito_bono = _fmt_usd(round(tier["area_1"] / 2))

    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm,
        title=f"Propuesta OOIA — {empresa}",
    )
    story = []

    logo_path = os.path.join(os.path.dirname(__file__), "assets", "ideuss-logo.jpg")
    if os.path.exists(logo_path):
        story.append(Image(logo_path, width=5 * cm, height=2.2 * cm))
    story.append(Spacer(1, 0.6 * cm))
    story.append(HRFlowable(width="100%", thickness=2, color=ORANGE, spaceAfter=18))
    story.append(Paragraph("Propuesta Comercial", S["cover_title"]))
    story.append(Paragraph("Ecosistema de Orquestación de Procesos y Agentes IA", S["cover_sub"]))
    story.append(Spacer(1, 0.4 * cm))

    meta_rows = [
        ["Para:", f"{contacto} — {empresa}" if contacto else empresa],
        ["Por:", "Alejandro Torres | CEO, IDEUSS"],
        ["Fecha de elaboración:", fecha],
        ["Vigencia:", "30 días"],
    ]
    meta_tbl = Table(meta_rows, colWidths=[4 * cm, 13 * cm])
    meta_tbl.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"), ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10), ("TEXTCOLOR", (0, 0), (0, -1), GRAY),
        ("TEXTCOLOR", (1, 0), (1, -1), DARK), ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5), ("LINEBELOW", (0, -1), (-1, -1), 0.5, BORDER),
    ]))
    story.append(meta_tbl)
    story.append(Spacer(1, 0.6 * cm))

    def section(title, html):
        story.append(section_header(title))
        story.append(Spacer(1, 8))
        story.append(Paragraph(html, S["body"]))
        story.append(Spacer(1, 12))

    section("Tu problema", (
        "Estás apagando incendios operativos en vez de hacer crecer tu negocio. Tu equipo pierde hasta el 50% "
        "del día en tareas manuales repetitivas. Los leads se enfrían porque nadie responde a tiempo. "
        "Resultado: pierdes dinero, tiempo y oportunidades cada día. La adopción de IA ya no es opcional: "
        "es la diferencia entre liderar tu mercado o quedarte atrás."
    ))

    section("Quiénes somos", (
        "IDEUSS lleva 15 años optimizando empresas en 10 países de Latinoamérica, con más de 25 años de "
        "experiencia en consultoría estratégica y certificaciones de fabricantes internacionales. No vendemos "
        "software: orquestamos. Ordenamos tu operación, la optimizamos, la automatizamos, y aplicamos IA donde "
        "realmente genera valor. Fácil. Rápido. Rentable. Inteligente y seguro."
    ))

    section("Cómo lo hacemos — Metodología OOIA", (
        "<b>Fase 1 — Descubrimiento y Estrategia:</b> contextualización de estrategia, procesos y "
        "ciberseguridad. Entregable: Road Map estratégico.<br/><br/>"
        "<b>Fase 2 — Organizar y Optimizar:</b> ordenamos tus procesos antes de automatizar.<br/><br/>"
        "<b>Fase 3 — Automatizar:</b> implementación de automatizaciones y agentes IA donde realmente "
        "agregan valor.<br/><br/>"
        "<b>Fase 4 — Acompañamiento:</b> soporte continuo, ajustes y optimización.<br/><br/>"
        "Con el diligenciamiento de la primera etapa de la fase de descubrimiento y estrategia de los "
        "procesos de: mercadeo, ventas, delivery, administración (producción es opcional), hemos terminado "
        "con el levantamiento de la información base. Para terminar la Fase 1 se siguen los siguientes "
        "pasos:<br/><br/>"
        "1. Mapeamos, dibujamos y hacemos Auditoría de tus procesos con el Método BPMN. El cual haremos en "
        "equipo con los responsables de los procesos en la empresa.<br/><br/>"
        "2. Descubrimos tus oportunidades de mejoramiento: cuellos de botella, procesos rotos, procesos "
        "desordenados y puntos de conflicto.<br/><br/>"
        "3. Levantamos los recursos tecnológicos con que disponen: hardware, software y redes. Con esta "
        "información hacemos estudio de vulnerabilidades cibernéticas.<br/><br/>"
        "4. Presentamos el plan estratégico de implementación. Sugerimos el Roadmap técnico de "
        "implementación con fases, alcance, tiempos, recursos y costos estimados."
    ))

    story.append(section_header("Inversión — Fase 1: Descubrimiento y Estrategia"))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "Contextualización de estrategia, procesos y ciberseguridad para identificar mejoras que logren mayor "
        "rendimiento empresarial. Entregable: Road Map estratégico con plan de mejoras, automatizaciones y "
        "agentes IA donde se identifique que agregan valor. Áreas recomendadas: Mercadeo, Ventas, Logística y "
        "Administración.",
        S["body"],
    ))
    story.append(Spacer(1, 10))

    price_rows = [
        ["Alcance", "Inversión"],
        ["Contextualización 1 área crítica (2 semanas)", precio_1_area],
        ["Contextualización completa, hasta 4 áreas (6-8 semanas)", precio_4_areas],
        ["Adicionar Producción", precio_produccion],
    ]
    price_tbl = Table(price_rows, colWidths=[11 * cm, 6 * cm])
    price_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ORANGE), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE), ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LGRAY]),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8), ("ALIGN", (1, 0), (1, -1), "RIGHT"),
    ]))
    story.append(price_tbl)
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "Opción de facturación en COP al TRM del día. Condiciones de pago: 50% al inicio, 30% a 30 días y "
        "saldo a 60 días. Precios en USD, no incluyen IVA, válidos por 30 días.",
        S["body"],
    ))
    story.append(Spacer(1, 12))

    bono = Table([[Paragraph(
        f"<b>Bono: tu inversión se protege.</b> Si decides que IDEUSS sea tu implementador del Road Map, "
        f"el 50% de tu inversión en esta Fase 1 se abona directamente como parte de pago de la propuesta de "
        f"implementación (por ejemplo, {credito_bono} de abono para la Fase 2). Condición: cumplir con los "
        f"tiempos de entrega de información y pagos según el cronograma inicial pactado.",
        S["body"],
    )]], colWidths=[17 * cm])
    bono.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF3DC")),
        ("TOPPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(bono)
    story.append(Spacer(1, 14))

    story.append(section_header("Equipo Consultor"))
    story.append(Spacer(1, 8))
    consultores = [
        (
            "Alejandro Torres Valdivieso — Director, IDEUSS",
            "Consultor y ejecutivo con más de 25 años en gestión gerencial integral para mejorar la "
            "rentabilidad empresarial. Experiencia en artes gráficas, consumo masivo, medios y tecnología. "
            "Lidera proyectos de automatización con agentes de IA en procesos de ventas, mercadeo, finanzas "
            "y manufactura. Ha desarrollado proyectos con clientes en 10 países de Latinoamérica. Asesor de "
            "fabricantes como Ricoh, Kodak, Enfocus y Pipedrive. Ingeniero Industrial — Universidad Javeriana. "
            "Posgrados en Administración (ICESI) y Gerencia Social (Universidad San Buenaventura).",
        ),
        (
            "Samuel Torres Florez — Ingeniería de Datos e IA",
            "Ingeniero de datos con más de 5 años de experiencia en soluciones de IA end-to-end. Consultor "
            "en Roche, liderando proyectos de IA generativa e investigación en inmunología. Especialista en "
            "transformar datos complejos en soluciones prácticas y escalables. Ingeniero Biomédico — "
            "Universidad de los Andes. M.Sc. Bioengineering (IA) — Universidad de McGill, Canadá.",
        ),
        (
            "Juan Pablo Botero Torres — Desarrollo de IA",
            "Ingeniero electrónico especializado en inteligencia artificial de alta demanda. Diseña modelos "
            "de IA energéticamente eficientes. Ofrece asesoría estratégica para transformación digital con "
            "impacto real en la industria. Ingeniero Electrónico — Universidad de los Andes. Doctorado en "
            "curso — Universidad de Utah, Estados Unidos.",
        ),
    ]
    for nombre_cargo, bio in consultores:
        story.append(Paragraph(nombre_cargo, S["h2"]))
        story.append(Paragraph(bio, S["body"]))
        story.append(Spacer(1, 8))
    story.append(Spacer(1, 6))

    section("Próximos pasos", (
        "1. Revisión interna de esta propuesta por parte del cliente.<br/>"
        "2. Para continuar el proceso solicitar reunión en "
        "<link href=\"https://www.ideuss.com/agendar-reuniones/\" color=\"#F5A623\">"
        "https://www.ideuss.com/agendar-reuniones/</link><br/>"
        "3. Aprobación de la propuesta, incluyendo cronograma e hitos específicos.<br/>"
        "4. Firma de la orden de acuerdo de servicio.<br/>"
        "5. Sesión inicial (Kick-off) dentro de 5 días hábiles tras la firma del acuerdo.<br/>"
        "6. Ejecución de la Contextualización con entregas parciales según cronograma.<br/>"
        "7. Entrega del Road Map estratégico y presentación a partes interesadas.<br/>"
        "8. Presentación de Fase 2 (Orquestación y Despliegue) como propuesta independiente."
    ))

    story.append(section_header("Disclaimer"))
    story.append(Spacer(1, 8))
    story.append(Paragraph((
        "Esta propuesta detalla el alcance, los entregables y plazos estimados en función de la información "
        "disponible. Las fechas y resultados podrán variar según disponibilidad de recursos, colaboración "
        "oportuna del cliente y calidad de los datos facilitados. Se espera que el cliente asigne a un líder "
        "del proyecto como punto de contacto para comunicación constante y solicitud de información. "
        "Adicionalmente, requerimos la disposición de por lo menos 2 horas de reuniones a la semana según la "
        "disposición horaria del cliente y del consultor. Cambios significativos en el alcance original "
        "podrían requerir revisiones adicionales del presupuesto y condiciones. Precios en USD, válidos por "
        "30 días. No incluyen IVA."
    ), S["body"]))
    story.append(Spacer(1, 14))

    story.append(Paragraph("IDEUSS | AI Agency &amp; Automation", S["footer"]))
    story.append(Paragraph("info@ideuss.com | +57 315 845 1170 | +1 786 579 0043", S["footer"]))
    story.append(Paragraph(
        "Toda información intercambiada está protegida bajo acuerdo de confidencialidad (NDA).", S["footer"]
    ))

    def add_footer(canvas, doc_):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(GRAY)
        canvas.drawString(2 * cm, 1.2 * cm, f"IDEUSS — Propuesta OOIA  |  {empresa}  |  {fecha}")
        canvas.drawRightString(19 * cm, 1.2 * cm, f"Página {doc_.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)
    return output_path
