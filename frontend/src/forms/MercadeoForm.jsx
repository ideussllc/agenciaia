const optionStyle = "flex items-center gap-2 text-sm text-slate-700";
const fieldStyle = "mt-2 w-full rounded-xl border border-slate-300 bg-slate-50 px-4 py-3 text-sm text-slate-900 focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-200";

function MercadeoForm({ data, onChange }) {
  const toggleCheckbox = (field, value, maxSelected) => {
    const current = Array.isArray(data[field]) ? data[field] : [];
    if (!current.includes(value) && maxSelected && current.length >= maxSelected) {
      return;
    }
    const next = current.includes(value)
      ? current.filter((item) => item !== value)
      : [...current, value];
    onChange(field, next);
  };

  return (
    <div className="space-y-8">
      <div className="space-y-4">
        <h2 className="text-2xl font-semibold text-slate-900">Mercadeo</h2>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">¿Quién es tu cliente ideal?</span>
          <p className="mt-1 text-xs text-slate-500">Quién compra, qué rol tiene, qué necesidad busca satisfacer</p>
          <textarea
            className={fieldStyle}
            rows="3"
            value={data.m_buyer || ''}
            onChange={(e) => onChange('m_buyer', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">¿Qué problema resuelves?</span>
          <textarea
            className={fieldStyle}
            rows="3"
            value={data.m_prop || ''}
            onChange={(e) => onChange('m_prop', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Describa si tiene su plan de mercadeo escrito: Estrategias de precios, producto, publicidad y canales de distribución con presupuesto asignado.</span>
          <textarea
            className={fieldStyle}
            rows="3"
            value={data.m_plan || ''}
            onChange={(e) => onChange('m_plan', e.target.value)}
          />
        </label>
        <div className="space-y-3">
          <span className="text-sm font-medium text-slate-700">Canales con mayor generación de prospectos de clientes (Marcar máximo 3)</span>
          {['Sitio Web', 'Redes sociales', 'Google Ads', 'email marketing', 'WhatsApp', 'Medios tradicionales', 'Networking', 'Eventos y ferias'].map((option) => (
            <label key={option} className={optionStyle}>
              <input
                type="checkbox"
                checked={(data.m_leads || []).includes(option)}
                onChange={() => toggleCheckbox('m_leads', option, 3)}
                className="h-4 w-4 rounded border-slate-300 text-slate-600"
              />
              {option}
            </label>
          ))}
        </div>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Describa cuáles son canales con mayor calidad y por que.</span>
          <textarea
            className={fieldStyle}
            rows="2"
            value={data.m_best || ''}
            onChange={(e) => onChange('m_best', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Describa las acciones y con qué frecuencia realiza para hacer generación de contenido y publicación para sus clientes objetivos</span>
          <textarea
            className={fieldStyle}
            rows="3"
            value={data.m_cont || ''}
            onChange={(e) => onChange('m_cont', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Describa como es el flujo de prospectos generados por mercadeo hacia ventas</span>
          <textarea
            className={fieldStyle}
            rows="3"
            value={data.m_flujo || ''}
            onChange={(e) => onChange('m_flujo', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Tiene el cálculo del costo de adquisición de nuevos clientes por cada canal o estrategia de mercadeo?</span>
          <textarea
            className={fieldStyle}
            rows="2"
            value={data.m_cac || ''}
            onChange={(e) => onChange('m_cac', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Tasa de conversión entendida como Numero de llamados a la accion obtenidos sobre el número de impactos publicitarios</span>
          <textarea
            className={fieldStyle}
            rows="2"
            value={data.m_conv || ''}
            onChange={(e) => onChange('m_conv', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Describa el proceso de creación, atribución y medicion de campañas publicitarias. Si dispone de un equipo propio, contrata con un tercero o si no las realiza actualmente.</span>
          <textarea
            className={fieldStyle}
            rows="3"
            value={data.m_attr || ''}
            onChange={(e) => onChange('m_attr', e.target.value)}
          />
        </label>
      </div>

      <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6">
        <h3 className="text-xl font-semibold text-slate-900">Diagnóstico estratégico</h3>
        <div className="mt-4 space-y-5">
          <label className="block">
            <span className="text-sm font-medium text-slate-700">A — Dolor principal en el proceso de mercadeo</span>
            <textarea
              className={fieldStyle}
              rows="3"
              value={data.m_dolor || ''}
              onChange={(e) => onChange('m_dolor', e.target.value)}
            />
          </label>
          <div className="space-y-2">
            <p className="text-sm font-medium text-slate-700">B — Nivel de automatización actual</p>
            {['Alto', 'Medio', 'Bajo', 'Ninguno'].map((option) => (
              <label key={option} className={optionStyle}>
                <input
                  type="radio"
                  name="m_auto_yn"
                  value={option}
                  checked={data.m_auto_yn === option}
                  onChange={(e) => onChange('m_auto_yn', e.target.value)}
                  className="h-4 w-4 rounded border-slate-300 text-slate-600"
                />
                {option}
              </label>
            ))}
          </div>
          <label className="block">
            <span className="text-sm font-medium text-slate-700">Detalle de automatizaciones existentes</span>
            <textarea
              className={fieldStyle}
              rows="3"
              value={data.m_auto_detalle || ''}
              onChange={(e) => onChange('m_auto_detalle', e.target.value)}
            />
          </label>
          <div className="space-y-2">
            <p className="text-sm font-medium text-slate-700">C — Uso de IA en mercadeo</p>
            {['Sí', 'No'].map((option) => (
              <label key={option} className={optionStyle}>
                <input
                  type="radio"
                  name="m_ia_yn"
                  value={option}
                  checked={data.m_ia_yn === option}
                  onChange={(e) => onChange('m_ia_yn', e.target.value)}
                  className="h-4 w-4 rounded border-slate-300 text-slate-600"
                />
                {option}
              </label>
            ))}
          </div>
          <label className="block">
            <span className="text-sm font-medium text-slate-700">Detalle de IA</span>
            <textarea
              className={fieldStyle}
              rows="3"
              value={data.m_ia_detalle || ''}
              onChange={(e) => onChange('m_ia_detalle', e.target.value)}
            />
          </label>
          <label className="block">
            <span className="text-sm font-medium text-slate-700">D — Criterio de éxito</span>
            <textarea
              className={fieldStyle}
              rows="3"
              value={data.m_exito || ''}
              onChange={(e) => onChange('m_exito', e.target.value)}
            />
          </label>
        </div>
      </div>
    </div>
  )
}

export default MercadeoForm;
