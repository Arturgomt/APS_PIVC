import React, { useEffect, useState } from 'react';
import { ArrowRight, Users, ScanFace, CheckCircle2, XCircle, Shield, Fingerprint } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { userService } from '../services/users';
import { recognitionService } from '../services/recognition';
import { PageIntro } from '../components/UI';
import { PERFIS } from '../data/cadastros';
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
  if (!admin) return <><PageIntro title={`Olá, ${user?.name?.split(' ')[0]}`}/><div className="user-hero"><span className="user-hero-icon"><Shield size={28}/></span><div><strong>{PERFIS[user?.level]} · nível {user?.level}</strong></div><Link to="/usuario/perfil" className="btn secondary">Meu perfil <ArrowRight size={16}/></Link></div><Recognize embedded/></>;
  const totals = { users: users.length, attempts: logs.length, allowed: logs.filter((x) => x.allowed).length, denied: logs.filter((x) => !x.allowed).length };
  const stats = [{ label: 'Usuários', value: totals.users, icon: Users, color: 'blue' }, { label: 'Tentativas', value: totals.attempts, icon: ScanFace, color: 'cyan' }, { label: 'Autorizados', value: totals.allowed, icon: CheckCircle2, color: 'green' }, { label: 'Negados', value: totals.denied, icon: XCircle, color: 'red' }];
  return <div className="page-fade"><PageIntro title={`Olá, ${user?.name?.split(' ')[0]}`}><Link className="btn primary" to="/admin/cadastro"><Fingerprint size={17}/> Novo cadastro facial</Link></PageIntro>
    {error && <div className="inline-error big">{error}</div>}
    <div className="stats-grid">{stats.map(({ label, value, icon: Icon, color }) => <div key={label} className="stat-card"><div className="stat-top"><span className={`stat-icon ${color}`}><Icon size={21}/></span></div><div className="stat-value">{value}</div><div className="stat-label">{label}</div></div>)}</div>
    <div className="dashboard-section-heading"><div><h2>Reconhecimento</h2></div></div>
    <Recognize embedded/>
    <AccessTable items={logs} preview/>
  </div>;
}
