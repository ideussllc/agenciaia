import sys, json, os, tempfile
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, PageBreak, Image
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from datetime import datetime

ORANGE = colors.HexColor("#F5A623")
DARK   = colors.HexColor("#1A1A1A")
GRAY   = colors.HexColor("#6B6B6B")
LGRAY  = colors.HexColor("#F5F5F3")
BORDER = colors.HexColor("#E0DED8")
WHITE  = colors.white
GREEN  = colors.HexColor("#3B6D11")
BLUE   = colors.HexColor("#185FA5")
RED    = colors.HexColor("#993C1D")

def sty(name, **kw):
    return ParagraphStyle(name, **kw)

S = {
    "cover_title": sty("ct", fontName="Helvetica-Bold", fontSize=28, textColor=DARK, leading=34, spaceAfter=8),
    "cover_sub":   sty("cs", fontName="Helvetica", fontSize=14, textColor=GRAY, leading=18, spaceAfter=4),
    "logo_title":  sty("lt", fontName="Helvetica-Bold", fontSize=26, textColor=ORANGE, leading=30, spaceAfter=2),
    "logo_tag":    sty("lg", fontName="Helvetica", fontSize=10, textColor=GRAY, leading=12, spaceAfter=4),
    "sec_title":   sty("st", fontName="Helvetica-Bold", fontSize=16, textColor=WHITE, leading=20),
    "h2":          sty("h2", fontName="Helvetica-Bold", fontSize=13, textColor=DARK, leading=17, spaceBefore=14, spaceAfter=6),
    "label":       sty("lb", fontName="Helvetica-Bold", fontSize=9, textColor=GRAY, leading=12, spaceBefore=4, spaceAfter=2),
    "body":        sty("bd", fontName="Helvetica", fontSize=9.5, textColor=DARK, leading=14, spaceAfter=4),
    "answer":      sty("an", fontName="Helvetica", fontSize=9.5, textColor=DARK, leading=14, spaceAfter=2, leftIndent=6),
    "empty":       sty("em", fontName="Helvetica-Oblique", fontSize=9.5, textColor=GRAY, leading=14, spaceAfter=2, leftIndent=6),
    "footer":      sty("ft", fontName="Helvetica", fontSize=8, textColor=GRAY, leading=10),
}

def safe(val):
    if not val: return ""
    return str(val).replace("||", ", ").replace("<", "&lt;").replace(">", "&gt;")

def section_header(title):
    tbl = Table([[Paragraph(title, S["sec_title"])]], colWidths=[17*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), ORANGE),
        ("TOPPADDING", (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("LEFTPADDING", (0,0), (-1,-1), 14),
    ]))
    return tbl

def qa_block(label, value, highlight=False):
    bg = colors.HexColor("#FFFBF2") if highlight else LGRAY
    content = safe(value) if value else "Sin respuesta registrada."
    style = S["answer"] if value else S["empty"]
    rows = [[Paragraph(label, S["label"])], [Paragraph(content, style)]]
    t = Table(rows, colWidths=[16.5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), bg),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("RIGHTPADDING", (0,0), (-1,-1), 8),
        ("LINEBELOW", (0,1), (-1,1), 0.5, BORDER),
    ]))
    return t

def strategic_block(prefix, area_label, _data=None):
    if _data is None: _data = {}
    items = [Spacer(1, 6)]
    qs = [
        (f"{prefix}_dolor",        "A — Dolor o cuello de botella principal", True),
        (f"{prefix}_auto_yn",      "B — Nivel de automatizacion actual", False),
        (f"{prefix}_auto_detalle", "   Automatizaciones existentes", False),
        (f"{prefix}_ia_yn",        "C — Uso de herramientas de IA", False),
        (f"{prefix}_ia_detalle",   "   Detalle del uso de IA", False),
        (f"{prefix}_exito",        "D — Criterio de exito de la consultoria", True),
    ]
    for key, lbl, hi in qs:
        items.append(qa_block(lbl, _data.get(key), highlight=hi))
        items.append(Spacer(1, 4))
    return items

def generate(data: dict, output_path: str):
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title="Descubrimiento OOIA — IDEUSS"
    )

    story = []
    empresa = data.get("empresa_nombre", "[Empresa]")
    contacto = data.get("empresa_contacto", "")
    actividad_economica = data.get("empresa_actividad_economica", "")
    rango_empleados = data.get("empresa_rango_empleados", "")
    rango_ventas_cop = data.get("empresa_rango_ventas_cop", "")
    fecha = datetime.now().strftime("%d de %B de %Y")

    size_map = {
        "Menos de USD $50.000 / año": "Microempresa",
        "Entre USD $50.000 y $500.000 / año": "Pequeña empresa",
        "Entre USD $500.000 y $5.000.000 / año": "Mediana empresa",
        "Más de USD $5.000.000 / año": "Gran empresa",
    }
    employee_size_map = {
        "Menos de 10": "Microempresa",
        "Entre 11 y 50": "Pequeña empresa",
        "Entre 51 y 100": "Mediana empresa",
        "Mas de 100": "Gran empresa",
    }
    size_label = employee_size_map.get(rango_empleados, size_map.get(data.get("v_volumen", ""), ""))

    # Cover
    story.append(Spacer(1, 1.5*cm))
    logo_path = os.path.join(os.path.dirname(__file__), 'assets', 'ideuss-logo.jpg')
    logo_img = None
    if os.path.exists(logo_path):
        logo_img = Image(logo_path, width=5*cm, height=2.2*cm)

    if logo_img:
        logo_row = [logo_img, Paragraph("Soluciones de automatización e inteligencia artificial", S["logo_tag"])]
    else:
        logo_row = [Paragraph("IDEUSS", S["logo_title"]), Paragraph("Soluciones de automatización e inteligencia artificial", S["logo_tag"])]

    logo_grid = Table([logo_row], colWidths=[5*cm, 11.5*cm])
    logo_grid.setStyle(TableStyle([
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("LEFTPADDING",(0,0),(-1,-1),0),
        ("RIGHTPADDING",(0,0),(-1,-1),0),
    ]))
    story.append(logo_grid)
    story.append(Spacer(1, 0.6*cm))
    story.append(HRFlowable(width="100%", thickness=2, color=ORANGE, spaceAfter=18))
    story.append(Paragraph("Informe de Descubrimiento Estrategico", S["cover_title"]))
    story.append(Paragraph("Ecosistema de orquestación de procesos y agentes IA", S["cover_sub"]))
    story.append(Spacer(1, 0.6*cm))

    meta_rows = [
        ["Empresa:", empresa], ["Contacto:", contacto or "—"],
        ["Actividad economica:", actividad_economica or "—"], ["Rango empleados:", rango_empleados or "—"],
        ["Rango ventas (miles COP):", rango_ventas_cop or "—"],
        ["Fecha:", fecha], ["Elaborado por:", "IDEUSS — AI Agency & Automation"],
    ]
    meta_tbl = Table(meta_rows, colWidths=[4*cm, 13*cm])
    meta_tbl.setStyle(TableStyle([
        ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"), ("FONTNAME",(1,0),(1,-1),"Helvetica"),
        ("FONTSIZE",(0,0),(-1,-1),10), ("TEXTCOLOR",(0,0),(0,-1),GRAY),
        ("TEXTCOLOR",(1,0),(1,-1),DARK), ("TOPPADDING",(0,0),(-1,-1),5),
        ("BOTTOMPADDING",(0,0),(-1,-1),5), ("LINEBELOW",(0,-1),(-1,-1),0.5,BORDER),
    ]))
    story.append(meta_tbl)
    story.append(Spacer(1, 0.5*cm))

    if size_label:
        badge = Table([[Paragraph(f"Clasificacion: {size_label}", sty("sz", fontName="Helvetica-Bold", fontSize=10, textColor=ORANGE))]],
                      colWidths=[8*cm])
        badge.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1), colors.HexColor("#FFF3DC")),
            ("TOPPADDING",(0,0),(-1,-1),5), ("BOTTOMPADDING",(0,0),(-1,-1),5),
            ("LEFTPADDING",(0,0),(-1,-1),8),
        ]))
        story.append(badge)

    def render_analysis_report(report):
        if not report:
            return []

        blocks = [PageBreak(), KeepTogether([section_header("7. Informe de consultoria AI"), Spacer(1, 10)])]

        def add_block(title, text):
            blocks.append(Paragraph(title, S["h2"]))
            blocks.append(qa_block(title, text))
            blocks.append(Spacer(1, 8))

        def render_list(title, items, fields):
            blocks.append(Paragraph(title, S["h2"]))
            if not items:
                blocks.append(qa_block("Sin resultados", "No se han generado recomendaciones para esta sección."))
                blocks.append(Spacer(1, 8))
                return
            for item in items:
                for label, key in fields:
                    blocks.append(qa_block(label, item.get(key)))
                blocks.append(Spacer(1, 6))
            blocks.append(Spacer(1, 8))

        add_block("Resumen ejecutivo", report.get("resumen_ejecutivo"))
        add_block("Estado actual", report.get("estado_actual"))
        add_block("Comparacion con la industria", report.get("comparacion_industria"))

        render_list(
            "Oportunidades de mejora",
            report.get("oportunidades_mejora", []),
            [
                ("Titulo", "titulo"),
                ("Area", "area"),
                ("Descripcion", "descripcion"),
                ("Prioridad", "prioridad"),
                ("Beneficio", "beneficio"),
            ],
        )
        render_list(
            "Automatizaciones sugeridas",
            report.get("automatizaciones_sugeridas", []),
            [
                ("Solucion", "solucion"),
                ("Area", "area"),
                ("Impacto", "impacto"),
                ("Prioridad", "prioridad"),
                ("Requisitos", "requisitos"),
            ],
        )
        render_list(
            "Agentes IA sugeridos",
            report.get("agentes_ia_sugeridos", []),
            [
                ("Nombre", "nombre"),
                ("Funcion", "funcion"),
                ("Beneficio", "beneficio"),
                ("Implementacion", "implementacion"),
            ],
        )
        render_list(
            "Casos de uso aplicados",
            report.get("casos_uso_aplicados", []),
            [
                ("Caso", "caso"),
                ("Proceso relacionado", "proceso_relacionado"),
                ("Descripcion", "descripcion"),
                ("Sector de referencia", "sector_referencia"),
                ("Impacto esperado", "impacto_esperado"),
            ],
        )
        render_list(
            "Oportunidades estrategicas",
            report.get("oportunidades", []),
            [
                ("Oportunidad", "opp"),
                ("Area", "area"),
                ("Herramienta", "tool"),
                ("Fase", "phase"),
                ("Impacto", "impacto"),
                ("Complejidad", "complejidad"),
                ("Justificacion", "justificacion"),
            ],
        )
        render_list(
            "Alertas de ciberseguridad",
            report.get("alertas_ciberseguridad", []),
            [
                ("Area", "area"),
                ("Riesgo", "riesgo"),
                ("Nivel", "nivel"),
                ("Recomendacion", "recomendacion"),
            ],
        )
        add_block("Quick wins", "\n".join(report.get("quick_wins", [])) if report.get("quick_wins") else "")
        return blocks

    story.append(PageBreak())

    # Sections
    sections = [
        ("1. Ventas", "v", [
            ("v_volumen","Volumen de ventas anual"), ("v_facturas","Facturas al mes"),
            ("v_pro","Prospectos atendidos al mes"), ("v_ll","Llamadas entrantes al mes"),
            ("v_proc","Proceso estandarizado"), ("v_ciclo","Ciclo de venta"),
            ("v_cotiz","Proceso de cotizacion"), ("v_perd","Frecuencia perdida de prospectos"),
            ("v_conv","Tasa de conversion lead a cliente (%)"), ("v_ticket","Ticket promedio por venta"),
            ("v_seg","Seguimiento post-cotizacion (SLA y frecuencia)"),
        ]),
        ("2. Mercadeo", "m", [
            ("m_buyer","Cliente ideal / buyer persona"), ("m_prop","Propuesta de valor"),
            ("m_plan","Plan de marketing"), ("m_leads","Leads al mes por canal"),
            ("m_best","Canal de mayor calidad"), ("m_cont","Gestion de contenido"),
            ("m_flujo","Flujo lead → ventas"),
            ("m_cac","CAC estimado por canal"), ("m_conv","Tasa de conversion lead a venta"),
            ("m_attr","Atribucion y medicion de campanas"),
        ]),
        ("3. Delivery / Fulfillment", "d", [
            ("d_proc","Proceso de entrega"), ("d_tiempo","Tiempo promedio"),
            ("d_doc","Documentacion del proceso"), ("d_resp","Responsable y dependencias"),
            ("d_cal","Control de calidad"), ("d_err","Errores frecuentes"),
            ("d_rec","Gestion de reclamos"), ("d_vis","Visibilidad del cliente"),
            ("d_skus","Numero de referencias o SKUs"), ("d_bodegas","Numero de bodegas"),
            ("d_merma","Tasa de desperdicio, danos u obsolescencia"),
            ("d_quiebre","Tasa de perdida de ventas por falta de inventarios"),
            ("d_sla","SLA comprometido vs cumplimiento real"), ("d_otif","Nivel OTIF"),
            ("d_devol","Tasa de devoluciones o retrabajos"),
        ]),
        ("4. Administracion", "a", [
            ("a_fact","Proceso de facturacion"), ("a_soft","Software contable"),
            ("a_cobrar","Cuentas por cobrar"), ("a_cierre","Cierre contable mensual"),
            ("a_estr","Estructura documental"), ("a_man","Procesos manuales"),
            ("a_dep","Dependencia de personas clave"), ("a_rep","Reportes de gestion"),
            ("a_dso","DSO promedio (dias de cobro)"), ("a_aprob","Flujo de aprobaciones y tiempos"),
            ("a_concil","Conciliacion bancaria y frecuencia"),
        ]),
        ("5. Produccion", "p", [
            ("p_et","Etapas del proceso"), ("p_cap","Capacidad productiva"),
            ("p_doc","Documentacion"), ("p_bot","Cuellos de botella"),
            ("p_cal","Control de calidad"), ("p_inv","Gestion de inventario"),
            ("p_par","Paros por materiales"), ("p_plan","Planeacion"),
            ("p_oee","OEE / eficiencia global"), ("p_scrap","Nivel de merma / scrap"),
            ("p_mant","Mantenimiento preventivo vs correctivo"),
        ]),
    ]

    for sec_title, prefix, fields in sections:
        story.append(KeepTogether([section_header(sec_title), Spacer(1, 10)]))
        for key, lbl in fields:
            story.append(qa_block(lbl, data.get(key)))
            story.append(Spacer(1, 4))
        story.append(Paragraph(f"Descubrimiento estrategico — {sec_title.split('. ')[1]}", S["h2"]))
        story.extend(strategic_block(prefix, sec_title, data))
        story.append(PageBreak())

    story.extend(render_analysis_report(data.get("analysis_report")))

    # Roadmap
    story.append(KeepTogether([section_header("6. Roadmap de Implementacion"), Spacer(1, 10)]))
    roadmap = data.get("roadmap", {})
    phases = [("Fase 0 — Quick wins", "p0", ORANGE, colors.HexColor("#FFF3DC")),
              ("Fase 1 — Proyectos estructurales", "p1", BLUE, colors.HexColor("#E6F1FB")),
              ("Fase 2 — Proyectos estrategicos", "p2", GREEN, colors.HexColor("#EAF3DE"))]

    for phase_title, phase_key, color_h, color_bg in phases:
        ph = Table([[Paragraph(phase_title, sty("pt", fontName="Helvetica-Bold", fontSize=12, textColor=color_h))]],
                   colWidths=[17*cm])
        ph.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),color_bg),
            ("TOPPADDING",(0,0),(-1,-1),10),("BOTTOMPADDING",(0,0),(-1,-1),10),
            ("LEFTPADDING",(0,0),(-1,-1),12),("LINEBELOW",(0,0),(-1,-1),1,color_h)]))
        story.append(ph)
        items = roadmap.get(phase_key, [])
        if items:
            rows = [["Oportunidad","Area","Herramienta","Tiempo","Costo USD"]]
            for r in items:
                if r.get("opp"):
                    rows.append([r.get("opp",""), r.get("area",""), r.get("tool",""), r.get("time",""), r.get("cost","")])
            if len(rows) > 1:
                dt = Table(rows, colWidths=[5*cm, 2.5*cm, 3.5*cm, 2.5*cm, 3.5*cm])
                dt.setStyle(TableStyle([
                    ("BACKGROUND",(0,0),(-1,0),LGRAY), ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
                    ("FONTSIZE",(0,0),(-1,-1),8.5), ("GRID",(0,0),(-1,-1),0.5,BORDER),
                    ("TOPPADDING",(0,0),(-1,-1),4), ("BOTTOMPADDING",(0,0),(-1,-1),4),
                    ("LEFTPADDING",(0,0),(-1,-1),5),
                ]))
                story.append(dt)
        story.append(Spacer(1, 12))

    # KPIs
    story.append(Paragraph("Criterios de exito por area", S["h2"]))
    kpi_rows = [["Area","Criterio de exito definido por el cliente"]]
    for area, key in [("Ventas","v_exito"),("Mercadeo","m_exito"),("Delivery","d_exito"),("Admin","a_exito"),("Produccion","p_exito")]:
        kpi_rows.append([area, data.get(key) or "Sin respuesta."])
    kt = Table(kpi_rows, colWidths=[4.5*cm, 12.5*cm])
    kt.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),ORANGE), ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("TEXTCOLOR",(0,0),(-1,0),WHITE), ("FONTSIZE",(0,0),(-1,-1),8.5),
        ("GRID",(0,0),(-1,-1),0.5,BORDER), ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE,LGRAY]),
        ("TOPPADDING",(0,0),(-1,-1),4), ("BOTTOMPADDING",(0,0),(-1,-1),4),
        ("LEFTPADDING",(0,0),(-1,-1),6), ("VALIGN",(0,0),(-1,-1),"TOP"),
    ]))
    story.append(kt)

    def add_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(GRAY)
        canvas.drawString(2*cm, 1.2*cm, f"IDEUSS — Diagnostico OOIA  |  {empresa}  |  {fecha}")
        canvas.drawRightString(19*cm, 1.2*cm, f"Pagina {doc.page}")
        canvas.setStrokeColor(BORDER)
        canvas.setLineWidth(0.5)
        canvas.line(2*cm, 1.6*cm, 19*cm, 1.6*cm)
        canvas.restoreState()

    doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)
    return output_path


# CLI mode (for testing)
if __name__ == "__main__":
    data = json.loads(sys.argv[1])
    out = data.get("_output", "/tmp/diagnostico.pdf")
    generate(data, out)
    print(f"PDF generado: {out}")
