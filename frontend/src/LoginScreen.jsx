import { useState } from 'react'
import { login } from './api.js'
import { setToken } from './auth.js'
import ideussLogo from './assets/ideuss-logo.jpg'

function LoginScreen({ onLogin }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError(null)
    setIsSubmitting(true)

    const response = await login(username, password)
    setIsSubmitting(false)

    if (!response.success) {
      setError(response.error)
      return
    }

    setToken(response.data.token)
    onLogin({ username: response.data.username, isAdmin: response.data.is_admin })
  }

  return (
    <div className="ideuss-bg flex min-h-screen items-center justify-center px-4 text-slate-900">
      <div className="w-full max-w-md rounded-[2rem] border border-[#E4E7EB] bg-white/90 p-8 shadow-[0_20px_50px_rgba(16,24,40,0.12)] backdrop-blur">
        <div className="flex flex-col items-center text-center">
          <img src={ideussLogo} alt="IDEUSS" className="h-14 w-auto object-contain" />
          <p className="mt-4 text-xs font-semibold uppercase tracking-[0.28em] text-[#F28C18]">Descubrimiento OOIA</p>
          <h1 className="mt-2 text-2xl font-bold tracking-tight text-[#101828]">Acceso restringido</h1>
          <p className="mt-2 text-sm text-[#667085]">Ingresa con las credenciales que te compartió IDEUSS.</p>
        </div>

        <form className="mt-8 space-y-4" onSubmit={handleSubmit}>
          <label className="block text-sm font-medium text-[#344054]">
            Usuario
            <input
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              className="mt-2 w-full rounded-2xl border border-[#D0D5DD] bg-white px-4 py-3 text-sm text-slate-900 shadow-sm transition focus:border-[#F28C18] focus:outline-none focus:ring-4 focus:ring-[#FDE7D1]"
              placeholder="usuario"
              autoComplete="username"
              required
            />
          </label>
          <label className="block text-sm font-medium text-[#344054]">
            Contraseña
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="mt-2 w-full rounded-2xl border border-[#D0D5DD] bg-white px-4 py-3 text-sm text-slate-900 shadow-sm transition focus:border-[#F28C18] focus:outline-none focus:ring-4 focus:ring-[#FDE7D1]"
              placeholder="••••••••"
              autoComplete="current-password"
              required
            />
          </label>

          {error ? <p className="text-sm font-medium text-red-600">{error}</p> : null}

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full rounded-2xl bg-[#F28C18] px-4 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-[#d97a0f] disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isSubmitting ? 'Ingresando...' : 'Ingresar'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default LoginScreen
