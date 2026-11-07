export const INITIAL_USERS = [
  { id: 'USR-001', name: 'João Silva', email: 'admin@iris.demo', job: 'Diretor de Segurança', department: 'Segurança', role: 'admin', level: 2, status: 'Ativo', createdAt: '2026-10-19' },
  { id: 'USR-002', name: 'Maria Santos', email: 'usuario@iris.demo', job: 'Analista Ambiental', department: 'Operações', role: 'user', level: 1, status: 'Ativo', createdAt: '2026-10-20' },
  { id: 'USR-003', name: 'Carlos Lima', email: 'carlos@iris.demo', job: 'Diretor de Divisão', department: 'Pesquisa', role: 'user', level: 2, status: 'Ativo', createdAt: '2026-10-20' },
  { id: 'USR-004', name: 'Helena Costa', email: 'helena@iris.demo', job: 'Ministra', department: 'Gabinete', role: 'user', level: 3, status: 'Ativo', createdAt: '2026-10-21' },
];

export const INITIAL_LOGS = [
  { id: 'LOG-001', date: '2026-10-25T11:42:18', user: 'João Silva', level: 2, allowed: true, source: 'demo' },
  { id: 'LOG-002', date: '2026-10-25T11:28:05', user: 'Maria Santos', level: 1, allowed: true, source: 'demo' },
  { id: 'LOG-003', date: '2026-10-25T11:15:32', user: 'Usuário desconhecido', level: 2, allowed: false, source: 'demo' },
  { id: 'LOG-004', date: '2026-10-24T14:10:11', user: 'Carlos Lima', level: 2, allowed: true, source: 'demo' },
  { id: 'LOG-005', date: '2026-10-24T13:55:47', user: 'Usuário desconhecido', level: 1, allowed: false, source: 'demo' },
];

export const ACCESS_LEVELS = [
  { value: 1, title: 'Nível 1', description: 'Permissão geral' },
  { value: 2, title: 'Nível 2', description: 'Acesso restrito · Diretores' },
  { value: 3, title: 'Nível 3', description: 'Acesso exclusivo · Ministro(a)' },
];

const USERS_KEY = 'iris-demo-users-v2';
const LOGS_KEY = 'iris-demo-logs-v2';
const parse = (key, fallback) => {
  try { const value = JSON.parse(localStorage.getItem(key)); return Array.isArray(value) ? value : fallback; }
  catch { return fallback; }
};
export const demoStore = {
  getUsers: () => parse(USERS_KEY, INITIAL_USERS),
  getLogs: () => parse(LOGS_KEY, INITIAL_LOGS),
  setUsers: (list) => localStorage.setItem(USERS_KEY, JSON.stringify(list)),
  setLogs: (list) => localStorage.setItem(LOGS_KEY, JSON.stringify(list)),
  reset: () => { localStorage.removeItem(USERS_KEY); localStorage.removeItem(LOGS_KEY); },
};
