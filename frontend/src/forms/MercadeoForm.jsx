const optionStyle = "flex items-center gap-2 text-sm text-slate-700";
const fieldStyle = "mt-2 w-full rounded-xl border border-slate-300 bg-slate-50 px-4 py-3 text-sm text-slate-900 focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-200";

function MercadeoForm({ data, onChange }) {
  const toggleCheckbox = (field, value) => {
    const current = Array.isArray(data[field]) ? data[field] : [];
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
          <span className="text-sm font-medium text-slate-700">Cliente ideal / buyer persona</span>
          <textarea
            className={fieldStyle}
            rows="3"
            value={data.m_buyer || ''}
            onChange={(e) => onChange('m_buyer', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Propuesta de valor</span>
          <textarea
            className={fieldStyle}
            rows="3"
            value={data.m_prop || ''}
            onChange={(e) => onChange('m_prop', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Plan de marketing</span>
          <textarea
            className={fieldStyle}
            rows="3"
            value={data.m_plan || ''}
            onChange={(e) => onChange('m_plan', e.target.value)}
          />
        </label>
        <div className="space-y-3">
          <span className="text-sm font-medium text-slate-700">Canales con mayor generación de leads</span>
          {['Email', 'Redes sociales', 'Contenido', 'Publicidad paga', 'Referidos'].map((option) => (
            <label key={option} className={optionStyle}>
              <input
                type="checkbox"
                checked={(data.m_leads || []).includes(option)}
                onChange={() => toggleCheckbox('m_leads', option)}
                className="h-4 w-4 rounded border-slate-300 text-slate-600"
              />
              {option}
            </label>
          ))}
          <textarea
            className={fieldStyle}
            rows="3"
            value={Array.isArray(data.m_leads) ? data.m_leads.join(', ') : data.m_leads || ''}
            onChange={(e) => onChange('m_leads', e.target.value)}
            placeholder="O describe tus canales principales..."
          />
        </div>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Canal de mayor calidad</span>
          <textarea
            className={fieldStyle}
            rows="2"
            value={data.m_best || ''}
            onChange={(e) => onChange('m_best', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Gestión de contenido</span>
          <textarea
            className={fieldStyle}
            rows="3"
            value={data.m_cont || ''}
            onChange={(e) => onChange('m_cont', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Flujo lead → ventas</span>
          <textarea
            className={fieldStyle}
            rows="3"
            value={data.m_flujo || ''}
            onChange={(e) => onChange('m_flujo', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">CAC estimado por canal</span>
          <textarea
            className={fieldStyle}
            rows="2"
            value={data.m_cac || ''}
            onChange={(e) => onChange('m_cac', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Tasa de conversión MQL/Lead → venta</span>
          <textarea
            className={fieldStyle}
            rows="2"
            value={data.m_conv || ''}
            onChange={(e) => onChange('m_conv', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Atribución y medición de campañas</span>
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
            <span className="text-sm font-medium text-slate-700">A — Dolor principal</span>
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
