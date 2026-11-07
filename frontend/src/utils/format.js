export const dateTime = (value) => value ? new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short', timeStyle: 'short' }).format(new Date(value)) : '—';
export const initials = (name = '') => name.split(/\s+/).filter(Boolean).slice(0, 2).map((part) => part[0]).join('').toUpperCase();
export const levelLabel = (level, source) => level ? `Nível ${level}` : source === 'login' ? 'Login' : '—';
export const sourceLabel = (source) => ({ demo: 'Simulação', login: 'Login', legado: 'Legado' })[source] || 'API';
export const dateOnly = (value) => value ? new Date(`${value}T00:00`).toLocaleDateString('pt-BR') : '—';
export const daysUntil = (value) => Math.ceil((new Date(`${value}T00:00`) - new Date()) / 86_400_000);
