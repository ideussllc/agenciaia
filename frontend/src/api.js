import { authHeaders, clearToken } from './auth.js'

const API_BASE = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '')

function buildPayload(data, analysisReport = null, pipedriveLeadId = null, diagId = null) {
  const payload = {
    data,
    empresa_nombre: data.empresa_nombre || '',
    empresa_contacto: data.empresa_contacto || '',
    roadmap: data.roadmap || {},
  }
  if (analysisReport) {
    payload.analysis_report = analysisReport
  }
  if (pipedriveLeadId) {
    payload.pipedrive_lead_id = pipedriveLeadId
  }
  if (diagId) {
    payload.diag_id = diagId
  }
  return payload
}

function checkUnauthorized(response) {
  if (response.status === 401) {
    clearToken()
  }
}

async function login(username, password) {
  try {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    })
    const result = await response.json()
    if (!response.ok) throw new Error(result.detail || 'Usuario o contraseña incorrectos')
    return { success: true, data: result, error: null }
  } catch (error) {
    return { success: false, data: null, error: error.message || String(error) }
  }
}

async function saveDiagnostico(data) {
  try {
    const payload = buildPayload(data)
    const response = await fetch(`${API_BASE}/save`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify(payload),
    })
    checkUnauthorized(response)
    const result = await response.json()
    if (!response.ok) throw new Error(result.detail || 'Error saving diagnostico')
    return { success: true, data: result, error: null }
  } catch (error) {
    return { success: false, data: null, error: error.message || String(error) }
  }
}

async function listDiagnosticos() {
  try {
    const response = await fetch(`${API_BASE}/list`, { headers: { ...authHeaders() } })
    checkUnauthorized(response)
    const result = await response.json()
    if (!response.ok) throw new Error(result.detail || 'Error listing diagnosticos')
    return { success: true, data: result, error: null }
  } catch (error) {
    return { success: false, data: null, error: error.message || String(error) }
  }
}

async function loadDiagnostico(id) {
  try {
    const response = await fetch(`${API_BASE}/load/${encodeURIComponent(id)}`, { headers: { ...authHeaders() } })
    checkUnauthorized(response)
    const result = await response.json()
    if (!response.ok) throw new Error(result.detail || 'Error loading diagnostico')
    return { success: true, data: result, error: null }
  } catch (error) {
    return { success: false, data: null, error: error.message || String(error) }
  }
}

async function sendReportPDF(data, analysisReport = null, pipedriveLeadId = null, diagId = null) {
  try {
    const payload = buildPayload(data, analysisReport, pipedriveLeadId, diagId)
    const response = await fetch(`${API_BASE}/generate-pdf`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify(payload),
    })
    checkUnauthorized(response)
    const result = await response.json()
    if (!response.ok) throw new Error(result.detail || 'Error enviando el informe')
    return { success: true, data: result, error: null }
  } catch (error) {
    return { success: false, data: null, error: error.message || String(error) }
  }
}

async function exportNotion(data, token, pageId) {
  try {
    const payload = { ...buildPayload(data), notion_token: token, notion_page_id: pageId }
    const response = await fetch(`${API_BASE}/export-notion`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify(payload),
    })
    checkUnauthorized(response)
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
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify(payload),
    })
    checkUnauthorized(response)
    const result = await response.json()
    if (!response.ok) throw new Error(result.detail || 'Error analyzing diagnostico')
    return { success: true, data: result, error: null }
  } catch (error) {
    return { success: false, data: null, error: error.message || String(error) }
  }
}

async function fetchCurrentUser() {
  try {
    const response = await fetch(`${API_BASE}/auth/me`, { headers: { ...authHeaders() } })
    checkUnauthorized(response)
    if (!response.ok) throw new Error('No autenticado')
    return { success: true, data: await response.json(), error: null }
  } catch (error) {
    return { success: false, data: null, error: error.message || String(error) }
  }
}

async function listUsers() {
  try {
    const response = await fetch(`${API_BASE}/admin/users`, { headers: { ...authHeaders() } })
    checkUnauthorized(response)
    const result = await response.json()
    if (!response.ok) throw new Error(result.detail || 'Error listing users')
    return { success: true, data: result.users, error: null }
  } catch (error) {
    return { success: false, data: null, error: error.message || String(error) }
  }
}

async function createUser(username, password, isAdmin = false) {
  try {
    const response = await fetch(`${API_BASE}/admin/users`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify({ username, password, is_admin: isAdmin }),
    })
    checkUnauthorized(response)
    const result = await response.json()
    if (!response.ok) throw new Error(result.detail || 'Error creating user')
    return { success: true, data: result, error: null }
  } catch (error) {
    return { success: false, data: null, error: error.message || String(error) }
  }
}

async function setUserActive(userId, isActive) {
  try {
    const response = await fetch(`${API_BASE}/admin/users/${encodeURIComponent(userId)}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify({ is_active: isActive }),
    })
    checkUnauthorized(response)
    const result = await response.json()
    if (!response.ok) throw new Error(result.detail || 'Error updating user')
    return { success: true, data: result, error: null }
  } catch (error) {
    return { success: false, data: null, error: error.message || String(error) }
  }
}

export {
  login,
  fetchCurrentUser,
  listUsers,
  createUser,
  setUserActive,
  saveDiagnostico,
  listDiagnosticos,
  loadDiagnostico,
  sendReportPDF,
  exportNotion,
  analyzeDiagnostico,
}
