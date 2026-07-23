import { useEffect, useState } from 'react'
import VentasForm from './forms/VentasForm.jsx'
import MercadeoForm from './forms/MercadeoForm.jsx'
import DeliveryForm from './forms/DeliveryForm.jsx'
import AdminForm from './forms/AdminForm.jsx'
import ProduccionForm from './forms/ProduccionForm.jsx'
import AdminUsersScreen from './forms/AdminUsersScreen.jsx'
import LoginScreen from './LoginScreen.jsx'
import { analyzeDiagnostico, saveDiagnostico, sendReportPDF, fetchCurrentUser } from './api.js'
import { getToken, clearToken } from './auth.js'
import ideussLogo from './assets/ideuss-logo.jpg'
import economicActivities from './data/economicActivities.js'

const tabs = ['Mercadeo', 'Ventas', 'Delivery', 'Administracion', 'Produccion', 'Informe']
const components = {
  Ventas: VentasForm,
  Mercadeo: MercadeoForm,
  Delivery: DeliveryForm,
  Administracion: AdminForm,
  Produccion: ProduccionForm,
}

const employeeRangeOptions = [
  'Menos de 10',
  'Entre 11 y 50',
  'Entre 51 y 100',
  'Mas de 100',
]

const decisionLevelOptions = [
  'Toma la decisión',
  'Participa en la decisión',
  'Propone la decisión',
]

const salesRangeCopOptions = [
  'Menos de 1.000',
  'Entre 1.001 y 5.000',
  'Entre 5.001 y 10.000',
  'Entre 10.001 y 90.000',
  'Mas de 90.000',
]

const salesRangeUsdOptions = [
  'Menos de 0,3',
  'Entre 0,3 y 1,5',
  'Entre 1,5 y 5,0',
  'Entre 5,0 y 25,0',
  'Mas de 25,0',
]

const OTRA_ACTIVIDAD = 'Otra actividad (no está en la lista)'

const requiredMetadataFields = [
  { key: 'empresa_contacto_cargo', label: 'Cargo que desempeña el contacto' },
  { key: 'empresa_contacto_nivel_decision', label: 'Nivel de decisión del contacto' },
  { key: 'empresa_actividad_economica', label: 'Actividad economica principal' },
  { key: 'empresa_rango_empleados', label: 'Rango de empleados' },
  { key: 'empresa_rango_ventas_cop', label: 'Rango de ventas' },
]

function SectionTitle({ children }) {
  return <h1 className="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">{children}</h1>
}

function ReportPane({ data }) {
  const trackedKeys = [
    'v_dolor', 'm_dolor', 'd_dolor', 'a_dolor', 'p_dolor',
    'v_exito', 'm_exito', 'd_exito', 'a_exito', 'p_exito',
    'v_auto_yn', 'm_auto_yn', 'd_auto_yn', 'a_auto_yn', 'p_auto_yn',
    'v_ia_yn', 'm_ia_yn', 'd_ia_yn', 'a_ia_yn', 'p_ia_yn',
  ]

  const answeredCount = trackedKeys.filter((key) => {
    const value = data[key]
    if (Array.isArray(value)) {
      return value.length > 0
    }
    return Boolean(value)
  }).length
  const completionPct = Math.round((answeredCount / trackedKeys.length) * 100)

  const isFilled = (value) => {
    if (Array.isArray(value)) {
      return value.length > 0
    }
    return Boolean(value)
  }

  const areaConfig = [
    {
      name: 'Ventas',
      prefix: 'v',
      keys: ['v_canales', 'v_ciudades', 'v_num_vendedores', 'v_facturas', 'v_pro', 'v_ll', 'v_proc', 'v_herramientas', 'v_ciclo', 'v_registro_prospectos', 'v_cotiz', 'v_perd', 'v_conv', 'v_ticket', 'v_seg', 'v_dolor', 'v_auto_yn', 'v_ia_yn', 'v_exito'],
    },
    {
      name: 'Mercadeo',
      prefix: 'm',
      keys: ['m_buyer', 'm_prop', 'm_plan', 'm_leads', 'm_best', 'm_cont', 'm_flujo', 'm_cac', 'm_conv', 'm_attr', 'm_dolor', 'm_auto_yn', 'm_ia_yn', 'm_exito'],
    },
    {
      name: 'Delivery',
      prefix: 'd',
      keys: ['d_proc', 'd_tiempo', 'd_proveedores', 'd_doc', 'd_resp', 'd_cal', 'd_err', 'd_rec', 'd_vis', 'd_sla', 'd_otif', 'd_devol', 'd_dolor', 'd_auto_yn', 'd_ia_yn', 'd_exito'],
    },
    {
      name: 'Administracion',
      prefix: 'a',
      keys: ['a_fact', 'a_soft', 'a_cobrar', 'a_cierre', 'a_nomina', 'a_estr', 'a_man', 'a_dep', 'a_rep', 'a_dso', 'a_aprob', 'a_concil', 'a_dolor', 'a_auto_yn', 'a_ia_yn', 'a_exito'],
    },
    {
      name: 'Produccion',
      prefix: 'p',
      keys: ['p_et', 'p_cap', 'p_doc', 'p_bot', 'p_cal', 'p_inv', 'p_par', 'p_plan', 'p_oee', 'p_scrap', 'p_mant', 'p_dolor', 'p_auto_yn', 'p_ia_yn', 'p_exito'],
    },
  ]

  const getStatus = (score) => {
    if (score >= 75) {
      return {
        label: 'Verde',
        classes: 'border-emerald-200 bg-emerald-50 text-emerald-800',
        dot: 'bg-emerald-500',
        recommendation: 'Mantener estandar y capturar quick wins de automatizacion.',
      }
    }
    if (score >= 45) {
      return {
        label: 'Ambar',
        classes: 'border-amber-200 bg-amber-50 text-amber-800',
        dot: 'bg-amber-500',
        recommendation: 'Priorizar brechas de proceso en los proximos 30-60 dias.',
      }
    }
    return {
      label: 'Rojo',
      classes: 'border-rose-200 bg-rose-50 text-rose-800',
      dot: 'bg-rose-500',
      recommendation: 'Intervencion inmediata: documentar proceso y definir control operativo.',
    }
  }

  const areaScores = areaConfig.map((area) => {
    const answered = area.keys.filter((key) => isFilled(data[key])).length
    const score = Math.round((answered / area.keys.length) * 100)
    const status = getStatus(score)
    const pain = data[`${area.prefix}_dolor`] || 'Sin dolor principal registrado.'
    return {
      ...area,
      answered,
      score,
      status,
      pain,
    }
  })

  const prioritizedAreas = [...areaScores].sort((a, b) => a.score - b.score)

  const section = (title, items) => (
    <div className="rounded-3xl border border-[#E4E7EB] bg-white/90 p-6 shadow-[0_12px_35px_rgba(16,24,40,0.08)] backdrop-blur">
      <h2 className="text-xl font-semibold text-slate-900">{title}</h2>
      <div className="mt-4 space-y-3">
        {items.map(({ label, value }) => (
          <div key={label} className="rounded-2xl border border-[#E4E7EB] bg-[#F9FAFB] p-4">
            <p className="text-sm font-semibold uppercase tracking-wide text-[#667085]">{label}</p>
            <p className="mt-2 text-sm text-slate-800">{value || 'Sin respuesta'}</p>
          </div>
        ))}
      </div>
    </div>
  )

  const summarize = (keys) =>
    keys.map((key) => ({ label: key.replace(/_/g, ' '), value: Array.isArray(data[key]) ? data[key].join(', ') : data[key] }))

  return (
    <div className="space-y-6">
      <SectionTitle>Informe de descubrimiento</SectionTitle>

      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-3xl border border-[#E4E7EB] bg-white p-5 shadow-sm">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#667085]">Empresa</p>
          <p className="mt-2 text-xl font-bold text-[#101828]">{data.empresa_nombre || 'Sin definir'}</p>
        </div>
        <div className="rounded-3xl border border-[#E4E7EB] bg-white p-5 shadow-sm">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#667085]">Avance de descubrimiento</p>
          <p className="mt-2 text-xl font-bold text-[#101828]">{completionPct}%</p>
        </div>
        <div className="rounded-3xl border border-[#E4E7EB] bg-white p-5 shadow-sm">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#667085]">Respuestas clave</p>
          <p className="mt-2 text-xl font-bold text-[#101828]">{answeredCount}/{trackedKeys.length}</p>
        </div>
      </div>

      <div className="rounded-3xl border border-[#E4E7EB] bg-white/90 p-6 shadow-[0_12px_35px_rgba(16,24,40,0.08)] backdrop-blur">
        <h2 className="text-xl font-semibold text-slate-900">Semaforo por area</h2>
        <p className="mt-1 text-sm text-[#667085]">Priorizacion automatica segun completitud de datos y claridad operativa.</p>
        <div className="mt-4 grid gap-4 lg:grid-cols-2">
          {prioritizedAreas.map((area) => (
            <div key={area.name} className="rounded-2xl border border-[#E4E7EB] bg-[#F9FAFB] p-4">
              <div className="flex items-center justify-between gap-3">
                <p className="text-sm font-bold text-[#101828]">{area.name}</p>
                <span className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-semibold ${area.status.classes}`}>
                  <span className={`h-2.5 w-2.5 rounded-full ${area.status.dot}`} />
                  {area.status.label}
                </span>
              </div>
              <p className="mt-2 text-xs font-semibold uppercase tracking-wide text-[#667085]">Cobertura descubrimiento</p>
              <p className="mt-1 text-sm text-[#344054]">{area.answered}/{area.keys.length} respuestas clave ({area.score}%)</p>
              <p className="mt-3 text-xs font-semibold uppercase tracking-wide text-[#667085]">Dolor principal</p>
              <p className="mt-1 text-sm text-[#344054]">{area.pain}</p>
              <p className="mt-3 text-xs font-semibold uppercase tracking-wide text-[#667085]">Sugerencia de gestion</p>
              <p className="mt-1 text-sm text-[#344054]">{area.status.recommendation}</p>
            </div>
          ))}
        </div>
      </div>

      {section('Resumen rápido', summarize(['v_dolor', 'm_dolor', 'd_dolor', 'a_dolor', 'p_dolor']))}
      {section('Criterios de éxito', summarize(['v_exito', 'm_exito', 'd_exito', 'a_exito', 'p_exito']))}
      {section('Automatización e IA', summarize(['v_auto_yn', 'v_ia_yn', 'm_auto_yn', 'm_ia_yn', 'd_auto_yn', 'd_ia_yn', 'a_auto_yn', 'a_ia_yn', 'p_auto_yn', 'p_ia_yn']))}
      {section('Roadmap y prioridad', summarize(['roadmap', 'empresa_nombre', 'empresa_contacto', 'empresa_actividad_economica', 'empresa_rango_empleados', 'empresa_rango_ventas_cop']))}
    </div>
  )
}

function App() {
  const [currentUser, setCurrentUser] = useState(null)
  const [authChecked, setAuthChecked] = useState(false)
  const [activeTab, setActiveTab] = useState('Mercadeo')
  const [data, setData] = useState({})
  const [analysisResult, setAnalysisResult] = useState(null)
  const [analysisError, setAnalysisError] = useState(null)
  const [saveMessage, setSaveMessage] = useState(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [isSending, setIsSending] = useState(false)
  const [sendError, setSendError] = useState(null)
  const [sendMessage, setSendMessage] = useState(null)
  const [pipedriveLeadId, setPipedriveLeadId] = useState(null)
  const [diagId, setDiagId] = useState(null)
  const FormComponent = components[activeTab]
  const missingMetadataFields = requiredMetadataFields.filter(({ key }) => {
    const value = data[key]
    return typeof value !== 'string' || !value.trim()
  })
  const hasMissingMetadata = missingMetadataFields.length > 0
  const visibleTabs = currentUser?.isAdmin ? [...tabs, 'Usuarios'] : tabs

  useEffect(() => {
    if (!getToken()) {
      setAuthChecked(true)
      return
    }
    fetchCurrentUser().then((response) => {
      if (response.success) {
        setCurrentUser({ username: response.data.sub, isAdmin: response.data.is_admin })
      }
      setAuthChecked(true)
    })
  }, [])

  const handleLogout = () => {
    clearToken()
    setCurrentUser(null)
  }

  const handleChange = (key, value) => {
    setData((prev) => ({ ...prev, [key]: value }))
  }

  const handleMetadataChange = (key, value) => {
    setData((prev) => ({ ...prev, [key]: value }))
  }

  const handleMonedaChange = (moneda) => {
    setData((prev) => ({ ...prev, empresa_moneda: moneda, empresa_rango_ventas_cop: '' }))
  }

  const actividadOptions = economicActivities.map(({ code, label }) => `${code} - ${label}`)
  const actividadValue = data.empresa_actividad_economica || ''
  const actividadSelectValue = actividadOptions.includes(actividadValue)
    ? actividadValue
    : (actividadValue ? OTRA_ACTIVIDAD : '')
  const showActividadOtraInput = actividadSelectValue === OTRA_ACTIVIDAD
  const currentSalesRangeOptions = data.empresa_moneda === 'USD' ? salesRangeUsdOptions : salesRangeCopOptions
  const salesRangeLabel = data.empresa_moneda === 'USD'
    ? 'Rango de ventas anuales (millones de USD)'
    : 'Rango de ventas anuales (miles de COP)'

  const runAnalysis = async () => {
    if (hasMissingMetadata) {
      const labels = missingMetadataFields.map(({ label }) => label).join(', ')
      setAnalysisError(`Completa los datos iniciales requeridos: ${labels}.`)
      return
    }

    setIsAnalyzing(true)
    setAnalysisError(null)
    setAnalysisResult(null)
    setSaveMessage(null)

    const response = await analyzeDiagnostico(data)

    setIsAnalyzing(false)
    if (response.success) {
      setAnalysisResult(response.data)
    } else {
      setAnalysisError(response.error)
    }
  }

  const sendReportEmail = async () => {
    setIsSending(true)
    setSendError(null)
    setSendMessage(null)

    let leadId = pipedriveLeadId
    let currentDiagId = diagId

    if (!currentDiagId) {
      const saveResponse = await saveDiagnostico(data)
      if (!saveResponse.success) {
        setIsSending(false)
        setSendError(saveResponse.error)
        return
      }
      currentDiagId = saveResponse.data.id
      setDiagId(currentDiagId)
      if (saveResponse.data.pipedrive_lead_id) {
        leadId = saveResponse.data.pipedrive_lead_id
        setPipedriveLeadId(leadId)
      }
    }

    const response = await sendReportPDF(data, analysisResult, leadId, currentDiagId)
    setIsSending(false)
    if (response.success) {
      setSendMessage('Informe enviado. Revisa el borrador en el correo de ventas.')
    } else {
      setSendError(response.error)
    }
  }

  const saveCurrentDiagnostico = async () => {
    if (hasMissingMetadata) {
      const labels = missingMetadataFields.map(({ label }) => label).join(', ')
      setSaveMessage(`Completa los datos iniciales requeridos: ${labels}.`)
      return
    }

    setIsSaving(true)
    setSaveMessage(null)
    setAnalysisError(null)

    const response = await saveDiagnostico(data)
    setIsSaving(false)
    if (response.success) {
      setSaveMessage(`Guardado con ID: ${response.data.id}`)
      setDiagId(response.data.id)
      if (response.data.pipedrive_lead_id) {
        setPipedriveLeadId(response.data.pipedrive_lead_id)
      }
    } else {
      setSaveMessage(`Error guardando: ${response.error}`)
    }
  }

  if (!authChecked) {
    return (
      <div className="ideuss-bg flex min-h-screen items-center justify-center text-slate-900">
        <p className="text-sm text-[#667085]">Cargando...</p>
      </div>
    )
  }

  if (!currentUser) {
    return <LoginScreen onLogin={setCurrentUser} />
  }

  return (
    <div className="ideuss-bg min-h-screen text-slate-900">
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="ideuss-orb ideuss-orb-1" />
        <div className="ideuss-orb ideuss-orb-2" />
      </div>

      <div className="relative mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="mb-4 flex items-center justify-end gap-3 text-sm text-[#475467]">
          <span>Sesión: <strong className="text-[#101828]">{currentUser.username}</strong>{currentUser.isAdmin ? ' (admin)' : ''}</span>
          <button
            type="button"
            onClick={handleLogout}
            className="rounded-full border border-[#D0D5DD] px-3 py-1.5 text-xs font-semibold text-[#344054] transition hover:border-[#F28C18] hover:text-[#F28C18]"
          >
            Cerrar sesión
          </button>
        </div>
        <div className="mb-7 grid gap-6 rounded-[2rem] border border-[#E4E7EB] bg-white/90 p-6 shadow-[0_20px_50px_rgba(16,24,40,0.12)] backdrop-blur reveal sm:grid-cols-[1.5fr_1fr] sm:p-8">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.28em] text-[#F28C18]">Descubrimiento OOIA</p>
            <h1 className="mt-3 text-4xl font-bold tracking-tight text-[#101828] sm:text-5xl">Arquitectura de procesos y agentes IA</h1>
            <p className="mt-4 max-w-2xl text-sm leading-7 text-[#475467] sm:text-base">
              Completa cada área para convertir el descubrimiento en un plan accionable, con recomendaciones automáticas y exportación profesional.
            </p>
            <p className="mt-3 max-w-2xl text-xs leading-5 text-[#667085]">
              Los datos aquí registrados están protegidos por la política de privacidad de IDEUSS disponible en{' '}
              <a
                href="https://www.ideuss.com/politicas-de-privacidad-de-ideuss/"
                target="_blank"
                rel="noreferrer"
                className="font-semibold text-[#F28C18] underline"
              >
                www.ideuss.com/politicas-de-privacidad-de-ideuss
              </a>
              .
            </p>
          </div>
          <div className="brand-card">
            <img src={ideussLogo} alt="IDEUSS" className="h-14 w-auto object-contain sm:h-16" />
            <p className="mt-3 text-sm font-semibold text-[#101828]">Consultoría estratégica en automatización</p>
            <p className="mt-1 text-sm text-[#475467]">Diseño de operaciones inteligentes, IA aplicada y crecimiento escalable.</p>
          </div>
        </div>

        <div className="mb-6 grid gap-4 rounded-[1.75rem] border border-[#E4E7EB] bg-white/90 p-6 shadow-[0_15px_35px_rgba(16,24,40,0.1)] backdrop-blur sm:grid-cols-[1fr_auto]">
          <div className="space-y-4">
            <label className="block text-sm font-medium text-[#344054]">
              Nombre de la empresa
              <input
                value={data.empresa_nombre || ''}
                onChange={(event) => handleMetadataChange('empresa_nombre', event.target.value)}
                className="mt-2 w-full rounded-2xl border border-[#D0D5DD] bg-white px-4 py-3 text-sm text-slate-900 shadow-sm transition focus:border-[#F28C18] focus:outline-none focus:ring-4 focus:ring-[#FDE7D1]"
                placeholder="Ej. Acme S.A."
              />
            </label>
            <label className="block text-sm font-medium text-[#344054]">
              Contacto principal
              <input
                value={data.empresa_contacto || ''}
                onChange={(event) => handleMetadataChange('empresa_contacto', event.target.value)}
                className="mt-2 w-full rounded-2xl border border-[#D0D5DD] bg-white px-4 py-3 text-sm text-slate-900 shadow-sm transition focus:border-[#F28C18] focus:outline-none focus:ring-4 focus:ring-[#FDE7D1]"
                placeholder="Ej. Maria Pérez"
              />
            </label>
            <label className="block text-sm font-medium text-[#344054]">
              Cargo que desempeña
              <input
                value={data.empresa_contacto_cargo || ''}
                onChange={(event) => handleMetadataChange('empresa_contacto_cargo', event.target.value)}
                className="mt-2 w-full rounded-2xl border border-[#D0D5DD] bg-white px-4 py-3 text-sm text-slate-900 shadow-sm transition focus:border-[#F28C18] focus:outline-none focus:ring-4 focus:ring-[#FDE7D1]"
                placeholder="Ej. Gerente de Operaciones"
              />
            </label>
            <label className="block text-sm font-medium text-[#344054]">
              Nivel de decisión
              <select
                value={data.empresa_contacto_nivel_decision || ''}
                onChange={(event) => handleMetadataChange('empresa_contacto_nivel_decision', event.target.value)}
                className="mt-2 w-full rounded-2xl border border-[#D0D5DD] bg-white px-4 py-3 text-sm text-slate-900 shadow-sm transition focus:border-[#F28C18] focus:outline-none focus:ring-4 focus:ring-[#FDE7D1]"
              >
                <option value="">Selecciona una opcion</option>
                {decisionLevelOptions.map((option) => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
            </label>
            <label className="block text-sm font-medium text-[#344054]">
              Correo electrónico del contacto
              <input
                type="email"
                value={data.empresa_contacto_email || ''}
                onChange={(event) => handleMetadataChange('empresa_contacto_email', event.target.value)}
                className="mt-2 w-full rounded-2xl border border-[#D0D5DD] bg-white px-4 py-3 text-sm text-slate-900 shadow-sm transition focus:border-[#F28C18] focus:outline-none focus:ring-4 focus:ring-[#FDE7D1]"
                placeholder="Ej. maria@empresa.com"
              />
            </label>
            <label className="block text-sm font-medium text-[#344054]">
              Número de WhatsApp del contacto
              <input
                value={data.empresa_contacto_whatsapp || ''}
                onChange={(event) => handleMetadataChange('empresa_contacto_whatsapp', event.target.value)}
                className="mt-2 w-full rounded-2xl border border-[#D0D5DD] bg-white px-4 py-3 text-sm text-slate-900 shadow-sm transition focus:border-[#F28C18] focus:outline-none focus:ring-4 focus:ring-[#FDE7D1]"
                placeholder="Ej. +57 300 123 4567"
              />
            </label>
            <label className="block text-sm font-medium text-[#344054]">
              Actividad economica principal
              <select
                value={actividadSelectValue}
                onChange={(event) => handleMetadataChange('empresa_actividad_economica', event.target.value === OTRA_ACTIVIDAD ? '' : event.target.value)}
                className="mt-2 w-full rounded-2xl border border-[#D0D5DD] bg-white px-4 py-3 text-sm text-slate-900 shadow-sm transition focus:border-[#F28C18] focus:outline-none focus:ring-4 focus:ring-[#FDE7D1]"
              >
                <option value="">Selecciona una opcion</option>
                {economicActivities.map(({ code, label }) => (
                  <option key={code} value={`${code} - ${label}`}>{code} - {label}</option>
                ))}
                <option value={OTRA_ACTIVIDAD}>{OTRA_ACTIVIDAD}</option>
              </select>
            </label>
            {showActividadOtraInput ? (
              <label className="block text-sm font-medium text-[#344054]">
                Especifica tu actividad económica
                <input
                  value={data.empresa_actividad_economica || ''}
                  onChange={(event) => handleMetadataChange('empresa_actividad_economica', event.target.value)}
                  className="mt-2 w-full rounded-2xl border border-[#D0D5DD] bg-white px-4 py-3 text-sm text-slate-900 shadow-sm transition focus:border-[#F28C18] focus:outline-none focus:ring-4 focus:ring-[#FDE7D1]"
                  placeholder="Ej. Fabricación de calzado"
                />
              </label>
            ) : null}
            <label className="block text-sm font-medium text-[#344054]">
              URL del sitio web
              <input
                value={data.empresa_sitio_web || ''}
                onChange={(event) => handleMetadataChange('empresa_sitio_web', event.target.value)}
                className="mt-2 w-full rounded-2xl border border-[#D0D5DD] bg-white px-4 py-3 text-sm text-slate-900 shadow-sm transition focus:border-[#F28C18] focus:outline-none focus:ring-4 focus:ring-[#FDE7D1]"
                placeholder="https://... o escribe NA si no tienen"
              />
            </label>
            <label className="block text-sm font-medium text-[#344054]">
              Rango de empleados
              <select
                value={data.empresa_rango_empleados || ''}
                onChange={(event) => handleMetadataChange('empresa_rango_empleados', event.target.value)}
                className="mt-2 w-full rounded-2xl border border-[#D0D5DD] bg-white px-4 py-3 text-sm text-slate-900 shadow-sm transition focus:border-[#F28C18] focus:outline-none focus:ring-4 focus:ring-[#FDE7D1]"
              >
                <option value="">Selecciona una opcion</option>
                {employeeRangeOptions.map((option) => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
            </label>
            <div className="block text-sm font-medium text-[#344054]">
              Moneda de reporte
              <div className="mt-2 flex gap-4">
                {['COP', 'USD'].map((moneda) => (
                  <label key={moneda} className="flex items-center gap-2 text-sm font-normal text-slate-700">
                    <input
                      type="radio"
                      name="empresa_moneda"
                      value={moneda}
                      checked={(data.empresa_moneda || 'COP') === moneda}
                      onChange={() => handleMonedaChange(moneda)}
                      className="h-4 w-4 border-slate-300 text-[#F28C18]"
                    />
                    {moneda}
                  </label>
                ))}
              </div>
            </div>
            <label className="block text-sm font-medium text-[#344054]">
              {salesRangeLabel}
              <select
                value={data.empresa_rango_ventas_cop || ''}
                onChange={(event) => handleMetadataChange('empresa_rango_ventas_cop', event.target.value)}
                className="mt-2 w-full rounded-2xl border border-[#D0D5DD] bg-white px-4 py-3 text-sm text-slate-900 shadow-sm transition focus:border-[#F28C18] focus:outline-none focus:ring-4 focus:ring-[#FDE7D1]"
              >
                <option value="">Selecciona una opcion</option>
                {currentSalesRangeOptions.map((option) => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
            </label>
          </div>
          <div className="flex flex-col gap-3 sm:items-end">
            <button
              type="button"
              onClick={saveCurrentDiagnostico}
              disabled={isSaving || hasMissingMetadata}
              className="inline-flex items-center justify-center rounded-full bg-[#F28C18] px-5 py-3 text-sm font-semibold text-white shadow-[0_8px_20px_rgba(242,140,24,0.35)] transition hover:bg-[#E17D0C] disabled:cursor-not-allowed disabled:bg-slate-400"
            >
              {isSaving ? 'Guardando...' : 'Guardar descubrimiento'}
            </button>
            {hasMissingMetadata ? (
              <p className="max-w-sm text-right text-xs text-rose-600">
                Requerido para guardar: {missingMetadataFields.map(({ label }) => label).join(', ')}.
              </p>
            ) : null}
            {saveMessage ? (
              <p className="text-sm text-[#475467]">{saveMessage}</p>
            ) : null}
          </div>
        </div>

        <div className="mb-6 flex flex-wrap gap-2 rounded-2xl border border-[#E4E7EB] bg-white/90 p-2 shadow-[0_10px_26px_rgba(16,24,40,0.08)] backdrop-blur">
          {visibleTabs.map((tab) => {
            const active = tab === activeTab
            return (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`rounded-full border px-4 py-2 text-sm font-semibold transition ${
                  active
                    ? 'border-[#F28C18] bg-[#F28C18] text-white shadow-[0_8px_18px_rgba(242,140,24,0.35)]'
                    : 'border-transparent bg-transparent text-[#475467] hover:border-[#F6D1A8] hover:bg-[#FFF7ED]'
                }`}
              >
                {tab}
              </button>
            )
          })}
        </div>

        <div className="rounded-[1.9rem] border border-[#E4E7EB] bg-white/95 p-6 shadow-[0_20px_46px_rgba(16,24,40,0.12)] backdrop-blur form-surface">
          {activeTab === 'Informe' ? (
            <div className="space-y-6">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm font-semibold uppercase tracking-[0.3em] text-[#F28C18]">Análisis AI</p>
                  <h2 className="text-2xl font-semibold text-[#101828]">Generar recomendaciones automáticas</h2>
                </div>
                <div className="flex flex-wrap gap-3">
                  <button
                    type="button"
                    onClick={runAnalysis}
                    disabled={isAnalyzing || hasMissingMetadata}
                    className="inline-flex items-center justify-center rounded-full bg-[#0E7A86] px-5 py-3 text-sm font-semibold text-white transition hover:bg-[#0A6470] disabled:cursor-not-allowed disabled:bg-slate-400"
                  >
                    {isAnalyzing ? 'Analizando...' : 'Analizar descubrimiento'}
                  </button>
                  <button
                    type="button"
                    onClick={sendReportEmail}
                    disabled={!analysisResult || isSending}
                    className="inline-flex items-center justify-center rounded-full bg-[#1D2939] px-5 py-3 text-sm font-semibold text-white transition hover:bg-black disabled:cursor-not-allowed disabled:bg-slate-400"
                  >
                    {isSending ? 'Enviando...' : 'Enviar informe en PDF'}
                  </button>
                </div>
              </div>

              {analysisError ? (
                <div className="rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
                  Error al analizar: {analysisError}
                </div>
              ) : null}
              {sendError ? (
                <div className="rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
                  Error al enviar el informe: {sendError}
                </div>
              ) : null}
              {sendMessage ? (
                <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-700">
                  {sendMessage}
                </div>
              ) : null}

              {analysisResult ? (
                <div className="space-y-4">
                  <div className="rounded-3xl border border-[#E4E7EB] bg-gradient-to-r from-[#FFF7ED] to-[#FFF1E6] p-6 shadow-sm">
                    <h3 className="text-xl font-semibold text-[#101828]">Resumen ejecutivo</h3>
                    <p className="mt-3 text-sm leading-6 text-[#344054]">{analysisResult.resumen_ejecutivo}</p>
                  </div>

                  <div className="grid gap-4 lg:grid-cols-2">
                    <div className="rounded-3xl border border-[#E4E7EB] bg-white p-6 shadow-sm">
                      <h3 className="text-lg font-semibold text-[#101828]">Estado actual</h3>
                      <p className="mt-3 text-sm leading-6 text-[#344054]">{analysisResult.estado_actual}</p>
                    </div>
                    <div className="rounded-3xl border border-[#E4E7EB] bg-white p-6 shadow-sm">
                      <h3 className="text-lg font-semibold text-[#101828]">Comparación con la industria</h3>
                      <p className="mt-3 text-sm leading-6 text-[#344054]">{analysisResult.comparacion_industria}</p>
                    </div>
                  </div>

                  <div className="rounded-3xl border border-[#E4E7EB] bg-white p-6 shadow-sm">
                    <h3 className="text-lg font-semibold text-[#101828]">Oportunidades de mejora</h3>
                    <div className="mt-4 space-y-4">
                      {analysisResult.oportunidades_mejora?.map((item, index) => (
                        <div key={index} className="rounded-2xl border border-[#E4E7EB] bg-[#F9FAFB] p-4">
                          <p className="text-sm font-semibold text-[#1D2939]">{item.titulo}</p>
                          <p className="text-sm text-[#475467]">Área: {item.area}</p>
                          <p className="text-sm text-[#475467]">Prioridad: {item.prioridad}</p>
                          <p className="text-sm text-[#475467]">Beneficio: {item.beneficio}</p>
                          <p className="mt-2 text-sm text-[#344054]">{item.descripcion}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="rounded-3xl border border-[#E4E7EB] bg-white p-6 shadow-sm">
                    <h3 className="text-lg font-semibold text-[#101828]">Automatizaciones sugeridas</h3>
                    <div className="mt-4 space-y-4">
                      {analysisResult.automatizaciones_sugeridas?.map((item, index) => (
                        <div key={index} className="rounded-2xl border border-[#E4E7EB] bg-[#F9FAFB] p-4">
                          <p className="text-sm font-semibold text-[#1D2939]">{item.solucion}</p>
                          <p className="text-sm text-[#475467]">Área: {item.area}</p>
                          <p className="text-sm text-[#475467]">Impacto: {item.impacto}</p>
                          <p className="text-sm text-[#475467]">Prioridad: {item.prioridad}</p>
                          <p className="mt-2 text-sm text-[#344054]">Requisitos: {item.requisitos}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="rounded-3xl border border-[#E4E7EB] bg-white p-6 shadow-sm">
                    <h3 className="text-lg font-semibold text-[#101828]">Agentes IA sugeridos</h3>
                    <div className="mt-4 space-y-4">
                      {analysisResult.agentes_ia_sugeridos?.map((item, index) => (
                        <div key={index} className="rounded-2xl border border-[#E4E7EB] bg-[#F9FAFB] p-4">
                          <p className="text-sm font-semibold text-[#1D2939]">{item.nombre}</p>
                          <p className="text-sm text-[#475467]">Función: {item.funcion}</p>
                          <p className="text-sm text-[#475467]">Beneficio: {item.beneficio}</p>
                          <p className="mt-2 text-sm text-[#344054]">Implementación: {item.implementacion}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="rounded-3xl border border-[#E4E7EB] bg-white p-6 shadow-sm">
                    <h3 className="text-lg font-semibold text-[#101828]">Casos de uso aplicados</h3>
                    <div className="mt-4 space-y-4">
                      {analysisResult.casos_uso_aplicados?.map((item, index) => (
                        <div key={index} className="rounded-2xl border border-[#E4E7EB] bg-[#F9FAFB] p-4">
                          <p className="text-sm font-semibold text-[#1D2939]">{item.caso}</p>
                          <p className="text-sm text-[#475467]">Proceso relacionado: {item.proceso_relacionado}</p>
                          <p className="text-sm text-[#475467]">Sector de referencia: {item.sector_referencia}</p>
                          <p className="text-sm text-[#475467]">Impacto esperado: {item.impacto_esperado}</p>
                          <p className="mt-2 text-sm text-[#344054]">{item.descripcion}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="grid gap-4 lg:grid-cols-2">
                    <div className="rounded-3xl border border-[#E4E7EB] bg-white p-6 shadow-sm">
                      <h3 className="text-lg font-semibold text-[#101828]">Oportunidades estratégicas</h3>
                      <div className="mt-4 space-y-4">
                        {analysisResult.oportunidades?.map((item, index) => (
                          <div key={index} className="rounded-2xl border border-[#E4E7EB] bg-[#F9FAFB] p-4">
                            <p className="text-sm font-semibold text-[#1D2939]">{item.opp}</p>
                            <p className="mt-1 text-sm text-[#475467]">Área: {item.area}</p>
                            <p className="text-sm text-[#475467]">Herramienta: {item.tool}</p>
                            <p className="text-sm text-[#475467]">Fase: {item.phase}</p>
                            <p className="text-sm text-[#475467]">Impacto: {item.impacto}</p>
                            <p className="text-sm text-[#475467]">Complejidad: {item.complejidad}</p>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="rounded-3xl border border-[#E4E7EB] bg-white p-6 shadow-sm">
                      <h3 className="text-lg font-semibold text-[#101828]">Alertas de ciberseguridad</h3>
                      <div className="mt-4 space-y-4">
                        {analysisResult.alertas_ciberseguridad?.map((item, index) => (
                          <div key={index} className="rounded-2xl border border-[#E4E7EB] bg-[#F9FAFB] p-4">
                            <p className="text-sm font-semibold text-[#1D2939]">Área: {item.area}</p>
                            <p className="text-sm text-[#475467]">Riesgo: {item.riesgo}</p>
                            <p className="text-sm text-[#475467]">Nivel: {item.nivel}</p>
                            <p className="text-sm text-[#475467]">Recomendación: {item.recomendacion}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="rounded-3xl border border-[#E4E7EB] bg-white p-6 shadow-sm">
                    <h3 className="text-lg font-semibold text-[#101828]">Quick wins</h3>
                    <ul className="mt-4 list-disc space-y-2 pl-5 text-sm text-[#344054]">
                      {analysisResult.quick_wins?.map((item, index) => (
                        <li key={index}>{item}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              ) : (
                <ReportPane data={data} />
              )}
            </div>
          ) : activeTab === 'Usuarios' ? (
            <AdminUsersScreen />
          ) : (
            <FormComponent data={data} onChange={handleChange} />
          )}
        </div>
      </div>
    </div>
  )
}

export default App
