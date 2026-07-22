const API_BASE = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '')

function buildPayload(data, analysisReport = null) {
  const payload = {
    data,
    empresa_nombre: data.empresa_nombre || '',
    empresa_contacto: data.empresa_contacto || '',
    roadmap: data.roadmap || {},
  }
  if (analysisReport) {
    payload.analysis_report = analysisReport
  }
  return payload
}

async function saveDiagnostico(data) {
  try {
    const payload = buildPayload(data)
    const response = await fetch(`${API_BASE}/save`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    const result = await response.json()
    if (!response.ok) throw new Error(result.detail || 'Error saving diagnostico')
    return { success: true, data: result, error: null }
  } catch (error) {
    return { success: false, data: null, error: error.message || String(error) }
  }
}

async function listDiagnosticos() {
  try {
    const response = await fetch(`${API_BASE}/list`)
    const result = await response.json()
    if (!response.ok) throw new Error(result.detail || 'Error listing diagnosticos')
    return { success: true, data: result, error: null }
  } catch (error) {
    return { success: false, data: null, error: error.message || String(error) }
  }
}

async function loadDiagnostico(id) {
  try {
    const response = await fetch(`${API_BASE}/load/${encodeURIComponent(id)}`)
    const result = await response.json()
    if (!response.ok) throw new Error(result.detail || 'Error loading diagnostico')
    return { success: true, data: result, error: null }
  } catch (error) {
    return { success: false, data: null, error: error.message || String(error) }
  }
}

async function generatePDF(data, analysisReport = null) {
  try {
    const payload = buildPayload(data, analysisReport)
    const response = await fetch(`${API_BASE}/generate-pdf`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!response.ok) {
      const errorResult = await response.json().catch(() => null)
      throw new Error(errorResult?.detail || 'Error generating PDF')
    }

    const blob = await response.blob()
    const filename = response.headers.get('Content-Disposition')?.match(/filename="?([^";]+)"?/)?.[1] || 'diagnostico.pdf'
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)

    return { success: true, data: null, error: null }
  } catch (error) {
    return { success: false, data: null, error: error.message || String(error) }
  }
}

async function exportNotion(data, token, pageId) {
  try {
    const payload = { ...buildPayload(data), notion_token: token, notion_page_id: pageId }
    const response = await fetch(`${API_BASE}/export-notion`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    const result = await response.json()
    if (!response.ok) throw new Error(result.detail || 'Error exporting to Notion')
    return { success: true, data: result, error: null }
  } catch (error) {
    return { success: false, data: null, error: error.message || String(error) }
  }
}

async function analyzeDiagnostico(data) {
  try {
    const payload = buildPayload(data)
    const response = await fetch(`${API_BASE}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    const result = await response.json()
    if (!response.ok) throw new Error(result.detail || 'Error analyzing diagnostico')
    return { success: true, data: result, error: null }
  } catch (error) {
    return { success: false, data: null, error: error.message || String(error) }
  }
}

export { saveDiagnostico, listDiagnosticos, loadDiagnostico, generatePDF, exportNotion, analyzeDiagnostico }
