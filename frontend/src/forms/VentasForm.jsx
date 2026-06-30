const optionStyle = "flex items-center gap-2 text-sm text-slate-700";
const fieldStyle = "mt-2 w-full rounded-xl border border-slate-300 bg-slate-50 px-4 py-3 text-sm text-slate-900 focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-200";

function VentasForm({ data, onChange }) {
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
        <h2 className="text-2xl font-semibold text-slate-900">Ventas</h2>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Volumen de ventas anual</span>
          <textarea
            className={fieldStyle}
            rows="3"
            value={data.v_volumen || ''}
            onChange={(e) => onChange('v_volumen', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Facturas al mes</span>
          <textarea
            className={fieldStyle}
            rows="3"
            value={data.v_facturas || ''}
            onChange={(e) => onChange('v_facturas', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Prospectos atendidos al mes</span>
          <textarea
            className={fieldStyle}
            rows="3"
            value={data.v_pro || ''}
            onChange={(e) => onChange('v_pro', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Llamadas entrantes al mes</span>
          <textarea
            className={fieldStyle}
            rows="3"
            value={data.v_ll || ''}
            onChange={(e) => onChange('v_ll', e.target.value)}
          />
        </label>
        <div className="space-y-3">
          <span className="text-sm font-medium text-slate-700">¿Qué parte del proceso está estandarizado?</span>
          {['CRM', 'Pipeline', 'Scripts de venta', 'No está estandarizado'].map((option) => (
            <label key={option} className={optionStyle}>
              <input
                type="checkbox"
                checked={(data.v_proc || []).includes(option)}
                onChange={() => toggleCheckbox('v_proc', option)}
                className="h-4 w-4 rounded border-slate-300 text-slate-600"
              />
              {option}
            </label>
          ))}
        </div>
        <fieldset className="space-y-3">
          <legend className="text-sm font-medium text-slate-700">Ciclo de venta</legend>
          {['Menos de 30 días', '30-90 días', 'Más de 90 días'].map((option) => (
            <label key={option} className={optionStyle}>
              <input
                type="radio"
                name="v_ciclo"
                value={option}
                checked={data.v_ciclo === option}
                onChange={(e) => onChange('v_ciclo', e.target.value)}
                className="h-4 w-4 rounded border-slate-300 text-slate-600"
              />
              {option}
            </label>
          ))}
        </fieldset>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Proceso de cotización</span>
          <textarea
            className={fieldStyle}
            rows="3"
            value={data.v_cotiz || ''}
            onChange={(e) => onChange('v_cotiz', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Frecuencia de pérdida de prospectos</span>
          <textarea
            className={fieldStyle}
            rows="3"
            value={data.v_perd || ''}
            onChange={(e) => onChange('v_perd', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Tasa de conversión lead → cliente (%)</span>
          <textarea
            className={fieldStyle}
            rows="2"
            value={data.v_conv || ''}
            onChange={(e) => onChange('v_conv', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Ticket promedio por venta</span>
          <textarea
            className={fieldStyle}
            rows="2"
            value={data.v_ticket || ''}
            onChange={(e) => onChange('v_ticket', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Seguimiento post-cotización (SLA y frecuencia)</span>
          <textarea
            className={fieldStyle}
            rows="3"
            value={data.v_seg || ''}
            onChange={(e) => onChange('v_seg', e.target.value)}
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
              value={data.v_dolor || ''}
              onChange={(e) => onChange('v_dolor', e.target.value)}
            />
          </label>
          <div className="space-y-2">
            <p className="text-sm font-medium text-slate-700">B — Nivel de automatización actual</p>
            {['Alto', 'Medio', 'Bajo', 'Ninguno'].map((option) => (
              <label key={option} className={optionStyle}>
                <input
                  type="radio"
                  name="v_auto_yn"
                  value={option}
                  checked={data.v_auto_yn === option}
                  onChange={(e) => onChange('v_auto_yn', e.target.value)}
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
              value={data.v_auto_detalle || ''}
              onChange={(e) => onChange('v_auto_detalle', e.target.value)}
            />
          </label>
          <div className="space-y-2">
            <p className="text-sm font-medium text-slate-700">C — Uso de IA en ventas</p>
            {['Sí', 'No'].map((option) => (
              <label key={option} className={optionStyle}>
                <input
                  type="radio"
                  name="v_ia_yn"
                  value={option}
                  checked={data.v_ia_yn === option}
                  onChange={(e) => onChange('v_ia_yn', e.target.value)}
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
              value={data.v_ia_detalle || ''}
              onChange={(e) => onChange('v_ia_detalle', e.target.value)}
            />
          </label>
          <label className="block">
            <span className="text-sm font-medium text-slate-700">D — Criterio de éxito</span>
            <textarea
              className={fieldStyle}
              rows="3"
              value={data.v_exito || ''}
              onChange={(e) => onChange('v_exito', e.target.value)}
            />
          </label>
        </div>
      </div>
    </div>
  )
}

export default VentasForm;
