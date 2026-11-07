export const DEMO_MODE = import.meta.env.VITE_DEMO_MODE !== 'false';
export const SESSION_KEY = 'iris-session-v2';
const API_BASE = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api').replace(/\/$/, '');

/**
 * Contrato implementado em api.py (raiz do projeto):
 * POST /auth/login (multipart: image) -> {user, token}   login pelo rosto
 * POST /auth/logout -> 204
 * GET /users -> User[]
 * POST /users -> User
 * PATCH /users/:id -> User
 * DELETE /users/:id -> 204 (apaga biometria e desativa; histórico preservado)
 * POST /recognitions (multipart: image, requested_level) ->
 *   {identified, authorized, user, confidence, reason, timestamp, resource}
 * GET /access-logs -> AccessLog[]
 * POST /face-enrollments (multipart: user_id,image) -> {success:true, message}
 */
export async function apiRequest(path, { method = 'GET', data, token, signal } = {}) {
  const isForm = data instanceof FormData;
  const response = await fetch(`${API_BASE}${path}`, {
    method,
    credentials: 'include',
    headers: { ...(isForm || data === undefined ? {} : { 'Content-Type': 'application/json' }), ...(token ? { Authorization: `Bearer ${token}` } : {}) },
    body: data === undefined ? undefined : isForm ? data : JSON.stringify(data),
    signal,
  });
  if (response.status === 401 && token) {
    // Sessão expirada ou API reiniciada: volta ao login pelo rosto.
    sessionStorage.removeItem(SESSION_KEY);
    window.location.assign('/login');
  }
  if (!response.ok) {
    let detail = `Erro na API (${response.status}).`;
    try { const body = await response.json(); detail = body.detail || body.message || detail; } catch { /* corpo não JSON */ }
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
  }
  if (response.status === 204) return null;
  return response.json();
}
