const optionStyle = "flex items-center gap-2 text-sm text-slate-700";
const fieldStyle = "mt-2 w-full rounded-xl border border-slate-300 bg-slate-50 px-4 py-3 text-sm text-slate-900 focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-200";

function AdminForm({ data, onChange }) {
  return (
    <div className="space-y-8">
      <div className="space-y-4">
        <h2 className="text-2xl font-semibold text-slate-900">Administración</h2>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Proceso de facturación</span>
          <textarea
            className={fieldStyle}
            rows="3"
            value={data.a_fact || ''}
            onChange={(e) => onChange('a_fact', e.target.value)}
          />
        </label>
        <div className="space-y-3">
          <span className="text-sm font-medium text-slate-700">Software contable</span>
          {['ERP', 'Excel', 'Herramienta contable', 'Sin sistema'].map((option) => (
            <label key={option} className={optionStyle}>
              <input
                type="checkbox"
                checked={(data.a_soft || []).includes(option)}
                onChange={() => {
                  const current = Array.isArray(data.a_soft) ? data.a_soft : [];
                  const next = current.includes(option)
                    ? current.filter((item) => item !== option)
                    : [...current, option];
                  onChange('a_soft', next);
                }}
                className="h-4 w-4 rounded border-slate-300 text-slate-600"
              />
              {option}
            </label>
          ))}
          <textarea
            className={fieldStyle}
            rows="2"
            value={Array.isArray(data.a_soft) ? data.a_soft.join(', ') : data.a_soft || ''}
            onChange={(e) => onChange('a_soft', e.target.value)}
            placeholder="Describe tu software o herramientas actuales..."
          />
        </div>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Cuentas por cobrar</span>
          <textarea
            className={fieldStyle}
            rows="3"
            value={data.a_cobrar || ''}
            onChange={(e) => onChange('a_cobrar', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Cierre contable mensual</span>
          <textarea
            className={fieldStyle}
            rows="3"
            value={data.a_cierre || ''}
            onChange={(e) => onChange('a_cierre', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Estructura documental</span>
          <textarea
            className={fieldStyle}
            rows="3"
            value={data.a_estr || ''}
            onChange={(e) => onChange('a_estr', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Procesos manuales</span>
          <textarea
            className={fieldStyle}
            rows="3"
            value={data.a_man || ''}
            onChange={(e) => onChange('a_man', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Dependencia de personas clave</span>
          <textarea
            className={fieldStyle}
            rows="3"
            value={data.a_dep || ''}
            onChange={(e) => onChange('a_dep', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Reportes de gestión</span>
          <textarea
            className={fieldStyle}
            rows="3"
            value={data.a_rep || ''}
            onChange={(e) => onChange('a_rep', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">DSO promedio (días de cobro)</span>
          <textarea
            className={fieldStyle}
            rows="2"
            value={data.a_dso || ''}
            onChange={(e) => onChange('a_dso', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Flujo de aprobaciones y tiempos</span>
          <textarea
            className={fieldStyle}
            rows="3"
            value={data.a_aprob || ''}
            onChange={(e) => onChange('a_aprob', e.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Conciliación bancaria y frecuencia</span>
          <textarea
            className={fieldStyle}
            rows="2"
            value={data.a_concil || ''}
            onChange={(e) => onChange('a_concil', e.target.value)}
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
              value={data.a_dolor || ''}
              onChange={(e) => onChange('a_dolor', e.target.value)}
            />
          </label>
          <div className="space-y-2">
            <p className="text-sm font-medium text-slate-700">B — Nivel de automatización actual</p>
            {['Alto', 'Medio', 'Bajo', 'Ninguno'].map((option) => (
              <label key={option} className={optionStyle}>
                <input
                  type="radio"
                  name="a_auto_yn"
                  value={option}
                  checked={data.a_auto_yn === option}
                  onChange={(e) => onChange('a_auto_yn', e.target.value)}
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
              value={data.a_auto_detalle || ''}
              onChange={(e) => onChange('a_auto_detalle', e.target.value)}
            />
          </label>
          <div className="space-y-2">
            <p className="text-sm font-medium text-slate-700">C — Uso de IA en administración</p>
            {['Sí', 'No'].map((option) => (
              <label key={option} className={optionStyle}>
                <input
                  type="radio"
                  name="a_ia_yn"
                  value={option}
                  checked={data.a_ia_yn === option}
                  onChange={(e) => onChange('a_ia_yn', e.target.value)}
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
              value={data.a_ia_detalle || ''}
              onChange={(e) => onChange('a_ia_detalle', e.target.value)}
            />
          </label>
          <label className="block">
            <span className="text-sm font-medium text-slate-700">D — Criterio de éxito</span>
            <textarea
              className={fieldStyle}
              rows="3"
              value={data.a_exito || ''}
              onChange={(e) => onChange('a_exito', e.target.value)}
            />
          </label>
        </div>
      </div>
    </div>
  )
}

export default AdminForm;
