import { apiRequest, DEMO_MODE } from './api';
import { demoStore } from '../data/demo';

export async function signIn({ email = '', password = '', image } = {}) {
  if (!DEMO_MODE) {
    if (!image) throw new Error('Capture uma imagem do rosto para entrar.');
    const form = new FormData();
    form.append('image', image, 'login.jpg');
    return apiRequest('/auth/login', { method: 'POST', data: form });
  }
  await new Promise((resolve) => setTimeout(resolve, 450));
  const account = email.toLowerCase().trim();
  const valid = (account === 'admin@iris.demo' && password === 'Admin@123') ||
    (account === 'usuario@iris.demo' && password === 'User@123');
  if (!valid) throw new Error('Credenciais de demonstração inválidas.');
  const user = demoStore.getUsers().find((item) => item.email === account && item.status === 'Ativo');
  if (!user) throw new Error('Conta de demonstração indisponível.');
  return { user, token: null };
}

export function signOut(token) {
  if (!DEMO_MODE && token) apiRequest('/auth/logout', { method: 'POST', token }).catch(() => {});
}
