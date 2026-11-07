import React, { useState } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import { ArrowRight, Lock, Mail, ShieldCheck, ScanFace, Eye, EyeOff, AlertCircle } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { DEMO_MODE } from '../services/api';
import CameraPanel from '../components/CameraPanel';
export default function Login() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [face, setFace] = useState(null);
  const [show, setShow] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  if (user) return <Navigate to={user.role === 'admin' ? '/admin' : '/usuario'} replace/>;
  async function enter(credentials) {
    setError(''); setBusy(true);
    try { const logged = await login(credentials); navigate(logged.role === 'admin' ? '/admin' : '/usuario', { replace: true }); }
    catch (err) { setError(err.message || 'Falha ao entrar.'); }
    finally { setBusy(false); }
  }
  function submit(event) { event.preventDefault(); enter({ email, password }); }
  const fill = (admin) => { setEmail(admin ? 'admin@iris.demo' : 'usuario@iris.demo'); setPassword(admin ? 'Admin@123' : 'User@123'); setError(''); };
  return <div className="login-page"><div className="login-visual">
    <div className="login-brand"><span className="brand-mark"><ShieldCheck size={28}/></span><strong>IRIS<span>.</span></strong></div>
    <div className="login-art"><div className="orb orb-one"/><div className="orb orb-two"/><div className="orb orb-three"/><div className="face-scan"><div className="face-scan-inner"><ScanFace size={120} strokeWidth={0.75}/></div><i className="scanner-line"/></div></div>
    <div className="login-visual-footer">APS Ciência da Computação · UNIP · 2026</div>
  </div><div className="login-form-side"><div className="login-card"><div className="login-mobile-logo"><ShieldCheck size={24}/> IRIS</div><h1>Entrar</h1>{!DEMO_MODE && <p className="login-sub">Ative a câmera, capture seu rosto e clique em entrar.</p>}
  {!DEMO_MODE && <div className="form-stack"><CameraPanel small onCapture={setFace}/>
  {error && <div className="inline-error"><AlertCircle size={16}/>{error}</div>}
  <button type="button" className="btn primary login-submit" disabled={busy || !face} onClick={() => enter({ image: face })}><ScanFace size={18}/>{busy ? 'Reconhecendo...' : 'Entrar com o rosto'}<ArrowRight size={18}/></button></div>}
  {DEMO_MODE && <form onSubmit={submit} className="form-stack"><label className="field-label">E-mail institucional<div className="input-wrap"><Mail size={18}/><input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="nome@instituicao.gov.br" required autoComplete="username"/></div></label><label className="field-label">Senha<div className="input-wrap"><Lock size={18}/><input type={show ? 'text' : 'password'} value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Digite sua senha" required autoComplete="current-password"/><button type="button" className="input-action" aria-label={show ? 'Ocultar senha' : 'Mostrar senha'} onClick={() => setShow(!show)}>{show ? <EyeOff size={18}/> : <Eye size={18}/>}</button></div></label>
  {error && <div className="inline-error"><AlertCircle size={16}/>{error}</div>}
  <button type="submit" className="btn primary login-submit" disabled={busy}>{busy ? 'Autenticando...' : 'Entrar no sistema'}<ArrowRight size={18}/></button></form>}
  {DEMO_MODE && <div className="demo-login"><div className="demo-login-head"><span className="demo-dot"/> Modo demonstração</div><div className="demo-profiles"><button onClick={() => fill(false)}><strong>Usuário</strong></button><button onClick={() => fill(true)}><strong>Administrador</strong></button></div></div>}
  </div></div></div>;
}
