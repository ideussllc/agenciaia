import { useEffect, useState } from 'react'
import { createUser, listUsers, setUserActive } from '../api.js'

const fieldStyle = 'mt-2 w-full rounded-2xl border border-[#D0D5DD] bg-white px-4 py-3 text-sm text-slate-900 shadow-sm transition focus:border-[#F28C18] focus:outline-none focus:ring-4 focus:ring-[#FDE7D1]'

function AdminUsersScreen() {
  const [users, setUsers] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [listError, setListError] = useState(null)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [isAdminUser, setIsAdminUser] = useState(false)
  const [formError, setFormError] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const refresh = async () => {
    setIsLoading(true)
    const response = await listUsers()
    setIsLoading(false)
    if (response.success) {
      setUsers(response.data)
      setListError(null)
    } else {
      setListError(response.error)
    }
  }

  useEffect(() => {
    refresh()
  }, [])

  const handleCreate = async (event) => {
    event.preventDefault()
    setFormError(null)
    setIsSubmitting(true)

    const response = await createUser(username, password, isAdminUser)
    setIsSubmitting(false)

    if (!response.success) {
      setFormError(response.error)
      return
    }

    setUsername('')
    setPassword('')
    setIsAdminUser(false)
    refresh()
  }

  const handleToggleActive = async (user) => {
    const response = await setUserActive(user.id, !user.is_active)
    if (response.success) {
      refresh()
    } else {
      setListError(response.error)
    }
  }

  return (
    <div className="space-y-6">
      <div className="rounded-[1.75rem] border border-[#E4E7EB] bg-white/90 p-6 shadow-[0_15px_35px_rgba(16,24,40,0.1)] backdrop-blur">
        <h2 className="text-lg font-semibold text-[#101828]">Crear usuario</h2>
        <form className="mt-4 grid gap-4 sm:grid-cols-2" onSubmit={handleCreate}>
          <label className="block text-sm font-medium text-[#344054]">
            Usuario
            <input value={username} onChange={(e) => setUsername(e.target.value)} className={fieldStyle} required />
          </label>
          <label className="block text-sm font-medium text-[#344054]">
            Contraseña
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} className={fieldStyle} required />
          </label>
          <label className="flex items-center gap-2 text-sm font-medium text-[#344054] sm:col-span-2">
            <input type="checkbox" checked={isAdminUser} onChange={(e) => setIsAdminUser(e.target.checked)} className="h-4 w-4 border-slate-300 text-[#F28C18]" />
            Es administrador
          </label>
          {formError ? <p className="text-sm font-medium text-red-600 sm:col-span-2">{formError}</p> : null}
          <button
            type="submit"
            disabled={isSubmitting}
            className="rounded-2xl bg-[#F28C18] px-4 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-[#d97a0f] disabled:cursor-not-allowed disabled:opacity-60 sm:col-span-2 sm:w-fit"
          >
            {isSubmitting ? 'Creando...' : 'Crear usuario'}
          </button>
        </form>
      </div>

      <div className="rounded-[1.75rem] border border-[#E4E7EB] bg-white/90 p-6 shadow-[0_15px_35px_rgba(16,24,40,0.1)] backdrop-blur">
        <h2 className="text-lg font-semibold text-[#101828]">Usuarios</h2>
        {listError ? <p className="mt-2 text-sm font-medium text-red-600">{listError}</p> : null}
        {isLoading ? (
          <p className="mt-4 text-sm text-[#667085]">Cargando...</p>
        ) : (
          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="text-xs font-semibold uppercase tracking-wide text-[#667085]">
                  <th className="pb-2">Usuario</th>
                  <th className="pb-2">Admin</th>
                  <th className="pb-2">Estado</th>
                  <th className="pb-2"></th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id} className="border-t border-[#E4E7EB]">
                    <td className="py-2 text-slate-900">{user.username}</td>
                    <td className="py-2 text-slate-700">{user.is_admin ? 'Sí' : 'No'}</td>
                    <td className="py-2 text-slate-700">{user.is_active ? 'Activo' : 'Desactivado'}</td>
                    <td className="py-2 text-right">
                      <button
                        type="button"
                        onClick={() => handleToggleActive(user)}
                        className="rounded-xl border border-[#D0D5DD] px-3 py-1.5 text-xs font-semibold text-[#344054] transition hover:border-[#F28C18] hover:text-[#F28C18]"
                      >
                        {user.is_active ? 'Desactivar' : 'Activar'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

export default AdminUsersScreen
