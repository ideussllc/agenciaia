const optionStyle = "flex items-center gap-2 text-sm text-slate-700";
const fieldStyle = "mt-2 w-full rounded-xl border border-slate-300 bg-slate-50 px-4 py-3 text-sm text-slate-900 focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-200";

function DeliveryForm({ data, onChange }) {
  return (
    <div className="space-y-8">
      <div className="space-y-4">
        <h2 className="text-2xl font-semibold text-slate-900">Delivery / Fulfillment</h2>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Proceso de entrega</span>
          <textarea
            className={fieldStyle}
            rows="3"
            value={data.d_proc || ''}
            onChange={(e) => onChange('d_proc', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Tiempo promedio de entrega</span>
          <textarea
            className={fieldStyle}
            rows="3"
            value={data.d_tiempo || ''}
            onChange={(e) => onChange('d_tiempo', e.target.value)}
          />
        </label>
        <div className="space-y-3">
          <span className="text-sm font-medium text-slate-700">Documentación del proceso</span>
          {['Manual interno', 'Mapa de procesos', 'Checklist', 'No hay documentación'].map((option) => (
            <label key={option} className={optionStyle}>
              <input
                type="checkbox"
                checked={(data.d_doc || []).includes(option)}
                onChange={() => {
                  const current = Array.isArray(data.d_doc) ? data.d_doc : [];
                  const next = current.includes(option)
                    ? current.filter((item) => item !== option)
                    : [...current, option];
                  onChange('d_doc', next);
                }}
                className="h-4 w-4 rounded border-slate-300 text-slate-600"
              />
              {option}
            </label>
          ))}
          <textarea
            className={fieldStyle}
            rows="3"
            value={Array.isArray(data.d_doc) ? data.d_doc.join(', ') : data.d_doc || ''}
            onChange={(e) => onChange('d_doc', e.target.value)}
            placeholder="Describe o agrega notas de documentación..."
          />
        </div>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Responsable y dependencias</span>
          <textarea
            className={fieldStyle}
            rows="3"
            value={data.d_resp || ''}
            onChange={(e) => onChange('d_resp', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Control de calidad</span>
          <textarea
            className={fieldStyle}
            rows="3"
            value={data.d_cal || ''}
            onChange={(e) => onChange('d_cal', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Errores frecuentes</span>
          <textarea
            className={fieldStyle}
            rows="3"
            value={data.d_err || ''}
            onChange={(e) => onChange('d_err', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Gestión de reclamos</span>
          <textarea
            className={fieldStyle}
            rows="3"
            value={data.d_rec || ''}
            onChange={(e) => onChange('d_rec', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Visibilidad para el cliente</span>
          <textarea
            className={fieldStyle}
            rows="3"
            value={data.d_vis || ''}
            onChange={(e) => onChange('d_vis', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Número de referencias o SKUs que manejan</span>
          <textarea
            className={fieldStyle}
            rows="2"
            value={data.d_skus || ''}
            onChange={(e) => onChange('d_skus', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Número de bodegas</span>
          <textarea
            className={fieldStyle}
            rows="2"
            value={data.d_bodegas || ''}
            onChange={(e) => onChange('d_bodegas', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Tasa de desperdicio, daños u obsolescencia de inventarios</span>
          <textarea
            className={fieldStyle}
            rows="2"
            value={data.d_merma || ''}
            onChange={(e) => onChange('d_merma', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Tasa de pérdida de ventas por falta de inventarios</span>
          <textarea
            className={fieldStyle}
            rows="2"
            value={data.d_quiebre || ''}
            onChange={(e) => onChange('d_quiebre', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">SLA comprometido vs cumplimiento real</span>
          <textarea
            className={fieldStyle}
            rows="2"
            value={data.d_sla || ''}
            onChange={(e) => onChange('d_sla', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Nivel OTIF (% entregas completas y a tiempo)</span>
          <textarea
            className={fieldStyle}
            rows="2"
            value={data.d_otif || ''}
            onChange={(e) => onChange('d_otif', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Tasa de devoluciones o retrabajos</span>
          <textarea
            className={fieldStyle}
            rows="2"
            value={data.d_devol || ''}
            onChange={(e) => onChange('d_devol', e.target.value)}
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
              value={data.d_dolor || ''}
              onChange={(e) => onChange('d_dolor', e.target.value)}
            />
          </label>
          <div className="space-y-2">
            <p className="text-sm font-medium text-slate-700">B — Nivel de automatización actual</p>
            {['Alto', 'Medio', 'Bajo', 'Ninguno'].map((option) => (
              <label key={option} className={optionStyle}>
                <input
                  type="radio"
                  name="d_auto_yn"
                  value={option}
                  checked={data.d_auto_yn === option}
                  onChange={(e) => onChange('d_auto_yn', e.target.value)}
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
              value={data.d_auto_detalle || ''}
              onChange={(e) => onChange('d_auto_detalle', e.target.value)}
            />
          </label>
          <div className="space-y-2">
            <p className="text-sm font-medium text-slate-700">C — Uso de IA en delivery</p>
            {['Sí', 'No'].map((option) => (
              <label key={option} className={optionStyle}>
                <input
                  type="radio"
                  name="d_ia_yn"
                  value={option}
                  checked={data.d_ia_yn === option}
                  onChange={(e) => onChange('d_ia_yn', e.target.value)}
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
              value={data.d_ia_detalle || ''}
              onChange={(e) => onChange('d_ia_detalle', e.target.value)}
            />
          </label>
          <label className="block">
            <span className="text-sm font-medium text-slate-700">D — Criterio de éxito</span>
            <textarea
              className={fieldStyle}
              rows="3"
              value={data.d_exito || ''}
              onChange={(e) => onChange('d_exito', e.target.value)}
            />
          </label>
        </div>
      </div>
    </div>
  )
}

export default DeliveryForm;
