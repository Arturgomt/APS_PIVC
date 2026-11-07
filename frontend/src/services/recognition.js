import { apiRequest, DEMO_MODE } from './api';
import { demoStore } from '../data/demo';

export const recognitionService = {
  async recognize({ image, level, token, demoUser }) {
    if (!DEMO_MODE) {
      if (!image) throw new Error('Ative a câmera e capture uma imagem antes de reconhecer.');
      const form = new FormData();
      form.append('image', image, 'captura.jpg');
      form.append('requested_level', String(level));
      return apiRequest('/recognitions', { method: 'POST', data: form, token });
    }
    await new Promise((resolve) => setTimeout(resolve, 800));
    // Somente simulação da regra de permissões. NÃO identifica rostos.
    const current = demoStore.getUsers().find((u) => u.id === demoUser?.id) || demoUser;
    const allowed = Boolean(current && current.status === 'Ativo' && Number(current.level) >= Number(level));
    const result = {
      identified: false, // deliberadamente false: biometria não foi executada
      authorized: allowed,
      user: current,
      confidence: null,
      reason: 'SIMULAÇÃO: nível verificado com o usuário da sessão, sem análise facial.',
      timestamp: new Date().toISOString(),
      simulated: true,
    };
    demoStore.setLogs([{
      id: `LOG-${Date.now()}`, date: result.timestamp, user: current?.name || 'Usuário demo',
      level: Number(level), allowed, source: 'demo',
    }, ...demoStore.getLogs()].slice(0, 100));
    return result;
  },
  async enroll({ image, userId, token }) {
    if (!image) throw new Error('Capture uma imagem antes de continuar.');
    if (DEMO_MODE) return { success: false, simulated: true, message: 'Prévia da foto capturada. Nenhum dado biométrico foi armazenado.' };
    const form = new FormData(); form.append('image', image, 'cadastro.jpg'); form.append('user_id', userId);
    return apiRequest('/face-enrollments', { method: 'POST', data: form, token });
  },
  async history(token) { return DEMO_MODE ? demoStore.getLogs() : apiRequest('/access-logs', { token }); },
};
