const optionStyle = "flex items-center gap-2 text-sm text-slate-700";
const fieldStyle = "mt-2 w-full rounded-xl border border-slate-300 bg-slate-50 px-4 py-3 text-sm text-slate-900 focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-200";

function ProduccionForm({ data, onChange }) {
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
        <h2 className="text-2xl font-semibold text-slate-900">Producción</h2>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Etapas del proceso</span>
          <textarea
            className={fieldStyle}
            rows="3"
            value={data.p_et || ''}
            onChange={(e) => onChange('p_et', e.target.value)}
          />
        </label>
        <div className="space-y-3">
          <span className="text-sm font-medium text-slate-700">Capacidad productiva</span>
          {['Baja', 'Media', 'Alta', 'Variable'].map((option) => (
            <label key={option} className={optionStyle}>
              <input
                type="checkbox"
                checked={(data.p_cap || []).includes(option)}
                onChange={() => toggleCheckbox('p_cap', option)}
                className="h-4 w-4 rounded border-slate-300 text-slate-600"
              />
              {option}
            </label>
          ))}
          <textarea
            className={fieldStyle}
            rows="2"
            value={Array.isArray(data.p_cap) ? data.p_cap.join(', ') : data.p_cap || ''}
            onChange={(e) => onChange('p_cap', e.target.value)}
            placeholder="Describe la capacidad productiva..."
          />
        </div>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Documentación</span>
          <textarea
            className={fieldStyle}
            rows="3"
            value={data.p_doc || ''}
            onChange={(e) => onChange('p_doc', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Cuellos de botella</span>
          <textarea
            className={fieldStyle}
            rows="3"
            value={data.p_bot || ''}
            onChange={(e) => onChange('p_bot', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Control de calidad</span>
          <textarea
            className={fieldStyle}
            rows="3"
            value={data.p_cal || ''}
            onChange={(e) => onChange('p_cal', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Gestión de inventario</span>
          <textarea
            className={fieldStyle}
            rows="3"
            value={data.p_inv || ''}
            onChange={(e) => onChange('p_inv', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Paros por materiales</span>
          <textarea
            className={fieldStyle}
            rows="3"
            value={data.p_par || ''}
            onChange={(e) => onChange('p_par', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Planeación</span>
          <textarea
            className={fieldStyle}
            rows="3"
            value={data.p_plan || ''}
            onChange={(e) => onChange('p_plan', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">OEE / eficiencia global del equipo</span>
          <textarea
            className={fieldStyle}
            rows="2"
            value={data.p_oee || ''}
            onChange={(e) => onChange('p_oee', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Nivel de merma / scrap</span>
          <textarea
            className={fieldStyle}
            rows="2"
            value={data.p_scrap || ''}
            onChange={(e) => onChange('p_scrap', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Mantenimiento preventivo vs correctivo</span>
          <textarea
            className={fieldStyle}
            rows="3"
            value={data.p_mant || ''}
            onChange={(e) => onChange('p_mant', e.target.value)}
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
              value={data.p_dolor || ''}
              onChange={(e) => onChange('p_dolor', e.target.value)}
            />
          </label>
          <div className="space-y-2">
            <p className="text-sm font-medium text-slate-700">B — Nivel de automatización actual</p>
            {['Alto', 'Medio', 'Bajo', 'Ninguno'].map((option) => (
              <label key={option} className={optionStyle}>
                <input
                  type="radio"
                  name="p_auto_yn"
                  value={option}
                  checked={data.p_auto_yn === option}
                  onChange={(e) => onChange('p_auto_yn', e.target.value)}
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
              value={data.p_auto_detalle || ''}
              onChange={(e) => onChange('p_auto_detalle', e.target.value)}
            />
          </label>
          <div className="space-y-2">
            <p className="text-sm font-medium text-slate-700">C — Uso de IA en producción</p>
            {['Sí', 'No'].map((option) => (
              <label key={option} className={optionStyle}>
                <input
                  type="radio"
                  name="p_ia_yn"
                  value={option}
                  checked={data.p_ia_yn === option}
                  onChange={(e) => onChange('p_ia_yn', e.target.value)}
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
              value={data.p_ia_detalle || ''}
              onChange={(e) => onChange('p_ia_detalle', e.target.value)}
            />
          </label>
          <label className="block">
            <span className="text-sm font-medium text-slate-700">D — Criterio de éxito</span>
            <textarea
              className={fieldStyle}
              rows="3"
              value={data.p_exito || ''}
              onChange={(e) => onChange('p_exito', e.target.value)}
            />
          </label>
        </div>
      </div>
    </div>
  )
}

export default ProduccionForm;
