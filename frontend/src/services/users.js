import { apiRequest, DEMO_MODE } from './api';
import { demoStore } from '../data/demo';

export const userService = {
  async list(token) { return DEMO_MODE ? demoStore.getUsers() : apiRequest('/users', { token }); },
  async create(user, token) {
    if (!DEMO_MODE) return apiRequest('/users', { method: 'POST', data: user, token });
    const users = demoStore.getUsers();
    if (users.some((u) => u.email.toLowerCase() === user.email.toLowerCase())) throw new Error('E-mail já cadastrado.');
    const entry = { ...user, id: `USR-${Date.now()}`, createdAt: new Date().toISOString().slice(0, 10) };
    demoStore.setUsers([entry, ...users]);
    return entry;
  },
  async update(id, changes, token) {
    if (!DEMO_MODE) return apiRequest(`/users/${encodeURIComponent(id)}`, { method: 'PATCH', data: changes, token });
    const list = demoStore.getUsers();
    if (list.some((u) => u.id !== id && u.email.toLowerCase() === changes.email?.toLowerCase())) throw new Error('E-mail já cadastrado.');
    const updated = list.map((u) => u.id === id ? { ...u, ...changes } : u);
    demoStore.setUsers(updated);
    return updated.find((u) => u.id === id);
  },
  async remove(id, token) {
    if (!DEMO_MODE) return apiRequest(`/users/${encodeURIComponent(id)}`, { method: 'DELETE', token });
    demoStore.setUsers(demoStore.getUsers().filter((u) => u.id !== id));
  },
};
