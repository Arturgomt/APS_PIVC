import { apiRequest } from './api';

// Rotas genéricas de api.py: /produtos, /formulas, /processos, /documentos, /instalacoes, /setores.
export const cadastroService = {
  list: (rota, token) => apiRequest(`/${rota}`, { token }),
  get: (rota, id, token) => apiRequest(`/${rota}/${id}`, { token }),
  save: (rota, data, id, token) => apiRequest(id ? `/${rota}/${id}` : `/${rota}`, { method: id ? 'PUT' : 'POST', data, token }),
  approve: (rota, id, token) => apiRequest(`/${rota}/${id}/aprovar`, { method: 'POST', token }),
  remove: (rota, id, token) => apiRequest(`/${rota}/${id}`, { method: 'DELETE', token }),
  permissions: (token) => apiRequest('/permissoes', { token }),
};
