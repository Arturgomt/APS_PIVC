import React, { useState } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import { ArrowRight, Lock, Mail, ShieldCheck, ScanFace, Fingerprint, Eye, EyeOff, AlertCircle, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { DEMO_MODE } from '../services/api';

export default function Login() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [show, setShow] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  if (user) return <Navigate to={user.role === 'admin' ? '/admin' : '/usuario'} replace/>;
  async function submit(event) {
    event.preventDefault(); setError(''); setBusy(true);
    try { const logged = await login(email, password); navigate(logged.role === 'admin' ? '/admin' : '/usuario', { replace: true }); }
    catch (err) { setError(err.message || 'Falha ao entrar.'); }
    finally { setBusy(false); }
  }
  const fill = (admin) => { setEmail(admin ? 'admin@iris.demo' : 'usuario@iris.demo'); setPassword(admin ? 'Admin@123' : 'User@123'); setError(''); };
  return <div className="login-page"><div className="login-visual">
    <div className="login-brand"><span className="brand-mark"><ShieldCheck size={28}/></span><strong>IRIS<span>.</span></strong></div>
    <div className="login-art"><div className="orb orb-one"/><div className="orb orb-two"/><div className="orb orb-three"/><div className="face-scan"><div className="face-scan-inner"><ScanFace size={120} strokeWidth={0.75}/></div><i className="scanner-line"/></div><span className="floating-chip top"><Fingerprint size={16}/> Identidade protegida</span><span className="floating-chip bottom"><CheckCircle2 size={16}/> Controle de acesso</span></div>
    <div className="login-visual-copy"><div className="eyebrow bright">PROTEÇÃO INTELIGENTE</div><h2>Segurança que<br/><span>reconhece você.</span></h2><p>Identificação biométrica, permissões por nível e uma experiência de acesso simples e segura.</p></div>
    <div className="login-visual-footer">APS Ciência da Computação • UNIP • 2026</div>
  </div><div className="login-form-side"><div className="login-card"><div className="login-mobile-logo"><ShieldCheck size={24}/> IRIS</div><div className="eyebrow">BEM-VINDO AO IRIS</div><h1>Acesse sua conta</h1><p className="login-sub">Entre para acessar o sistema de reconhecimento facial.</p>
  <form onSubmit={submit} className="form-stack"><label className="field-label">E-mail institucional<div className="input-wrap"><Mail size={18}/><input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="nome@instituicao.gov.br" required autoComplete="username"/></div></label><label className="field-label">Senha<div className="input-wrap"><Lock size={18}/><input type={show ? 'text' : 'password'} value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Digite sua senha" required autoComplete="current-password"/><button type="button" className="input-action" aria-label={show ? 'Ocultar senha' : 'Mostrar senha'} onClick={() => setShow(!show)}>{show ? <EyeOff size={18}/> : <Eye size={18}/>}</button></div></label>
  {error && <div className="inline-error"><AlertCircle size={16}/>{error}</div>}
  <button type="submit" className="btn primary login-submit" disabled={busy}>{busy ? 'Autenticando...' : 'Entrar no sistema'}<ArrowRight size={18}/></button></form>
  {DEMO_MODE && <div className="demo-login"><div className="demo-login-head"><span className="demo-dot"/> MODO DE DEMONSTRAÇÃO</div><p>Selecione um perfil para preencher as credenciais de teste:</p><div className="demo-profiles"><button onClick={() => fill(false)}><span>👤</span><strong>Usuário</strong><small>Acesso ao cofre</small></button><button onClick={() => fill(true)}><span>🛡️</span><strong>Administrador</strong><small>Gestão e controle</small></button></div><small>Autenticação apenas demonstrativa. Nenhuma validação de segurança real é feita no navegador.</small></div>}
  <div className="login-right-footer"><ShieldCheck size={15}/> IRIS — Projeto acadêmico</div></div></div></div>;
}
