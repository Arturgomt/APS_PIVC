export const DEMO_MODE = import.meta.env.VITE_DEMO_MODE !== 'false';
const API_BASE = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api').replace(/\/$/, '');

/**
 * Contrato PROPOSTO, a validar com a equipe Python:
 * POST /auth/login {email,password} -> {user, token?}
 * GET /users -> User[]
 * POST /users -> User
 * PATCH /users/:id -> User
 * DELETE /users/:id -> 204
 * POST /recognitions (multipart: image, requested_level) ->
 *   {identified, authorized, user?, confidence?, reason?, timestamp?}
 * GET /access-logs -> AccessLog[]
 * POST /face-enrollments (multipart: user_id,image) -> {success:true}
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
  if (!response.ok) {
    let detail = `Erro na API (${response.status}).`;
    try { const body = await response.json(); detail = body.detail || body.message || detail; } catch { /* corpo não JSON */ }
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
  }
  if (response.status === 204) return null;
  return response.json();
}
