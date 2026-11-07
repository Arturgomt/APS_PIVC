import React, { useEffect, useState } from 'react';
import { ArrowRight, ArrowUpRight, Users, ScanFace, CheckCircle2, XCircle, Shield, Sparkles, Fingerprint, History } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { userService } from '../services/users';
import { recognitionService } from '../services/recognition';
import { PageIntro, SectionHeading, Avatar, StatusPill } from '../components/UI';
import AccessTable from '../components/AccessTable';
import Recognize from './Recognize';

export default function Dashboard({ admin = false }) {
  const { user, token } = useAuth();
  const [users, setUsers] = useState([]);
  const [logs, setLogs] = useState([]);
  const [error, setError] = useState('');
  useEffect(() => {
    if (!admin) return;
    let active = true;
    Promise.all([userService.list(token), recognitionService.history(token)]).then(([u, l]) => { if (active) { setUsers(u); setLogs(l); } }).catch((e) => { if (active) setError(e.message); });
    return () => { active = false; };
  }, [admin, token]);
  if (!admin) return <><PageIntro eyebrow="ÁREA DO USUÁRIO" title={`Olá, ${user?.name?.split(' ')[0]}! 👋`} description="Utilize o reconhecimento facial para solicitar acesso ao cofre."/><div className="user-hero"><span className="user-hero-icon"><Shield size={28}/></span><div><strong>Seu perfil possui permissão de Nível {user?.level}</strong><p>Solicitações a níveis superiores serão negadas pelo servidor quando integrado.</p></div><Link to="/usuario/perfil" className="btn secondary">Meu perfil <ArrowRight size={16}/></Link></div><Recognize embedded/></>;
  const totals = { users: users.length, attempts: logs.length, allowed: logs.filter((x) => x.allowed).length, denied: logs.filter((x) => !x.allowed).length };
  const stats = [{ label: 'Usuários cadastrados', value: totals.users, icon: Users, color: 'blue', detail: 'Base de usuários' }, { label: 'Tentativas registradas', value: totals.attempts, icon: ScanFace, color: 'cyan', detail: 'Total carregado' }, { label: 'Acessos autorizados', value: totals.allowed, icon: CheckCircle2, color: 'green', detail: 'Solicitações permitidas' }, { label: 'Acessos negados', value: totals.denied, icon: XCircle, color: 'red', detail: 'Solicitações bloqueadas' }];
  return <div className="page-fade"><PageIntro eyebrow="VISÃO GERAL · ADMINISTRADOR" title={`Bem-vindo, ${user?.name?.split(' ')[0]}!`} description="Acompanhe os usuários, permissões e solicitações de acesso ao sistema."><Link className="btn primary" to="/admin/cadastro"><Fingerprint size={17}/> Novo cadastro facial</Link></PageIntro>
    {error && <div className="inline-error big">{error}</div>}
    <div className="stats-grid">{stats.map(({ label, value, icon: Icon, color, detail }) => <div key={label} className="stat-card"><div className="stat-top"><span className={`stat-icon ${color}`}><Icon size={21}/></span><ArrowUpRight className="stat-arrow" size={17}/></div><div className="stat-value">{value}</div><div className="stat-label">{label}</div><div className="stat-detail">{detail}</div></div>)}</div>
    <div className="dashboard-section-heading"><div><div className="eyebrow">AUTENTICAÇÃO</div><h2>Central de reconhecimento</h2><p>Captura facial, seleção de nível de segurança e retorno da autenticação.</p></div><span className="tiny-tag">Módulo de acesso</span></div>
    <Recognize embedded/>
    <AccessTable items={logs} preview/>
  </div>;
}
