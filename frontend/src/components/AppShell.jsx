import React, { useState } from 'react';
import { NavLink, useLocation, useNavigate } from 'react-router-dom';
import { ScanFace, LayoutDashboard, Users, UserRound, UserPlus, History, Settings, ShieldCheck, LogOut, Menu, X, KeyRound } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { DEMO_MODE } from '../services/api';
import { CADASTROS } from '../data/cadastros';
import { Avatar, DemoNotice } from './UI';
const routeLabels = { '/admin': 'Visão geral', '/admin/usuarios': 'Usuários', '/admin/cadastro': 'Cadastro facial', '/admin/historico': 'Histórico', '/admin/configuracoes': 'Configurações', '/usuario': 'Início', '/usuario/reconhecimento': 'Reconhecimento facial', '/usuario/perfil': 'Meu perfil', '/permissoes': 'Minhas permissões',
  ...Object.fromEntries(CADASTROS.map((c) => [`/${c.rota}`, c.titulo])) };
const itemDoCadastro = (c) => ({ path: `/${c.rota}`, icon: c.icone, name: c.titulo });
export default function AppShell({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);
  const admin = user?.role === 'admin';
  const menu = admin ? [
    { path: '/admin', icon: LayoutDashboard, name: 'Visão geral', end: true },
    { path: '/admin/usuarios', icon: Users, name: 'Usuários' },
    { path: '/admin/cadastro', icon: UserPlus, name: 'Cadastro facial' },
    { path: '/admin/historico', icon: History, name: 'Histórico de acessos' },
    ...(DEMO_MODE ? [] : CADASTROS.filter((c) => c.apenasAdmin).map(itemDoCadastro)),
    { path: '/admin/configuracoes', icon: Settings, name: 'Configurações' },
  ] : [
    { path: '/usuario', icon: LayoutDashboard, name: 'Início', end: true },
    { path: '/usuario/reconhecimento', icon: ScanFace, name: 'Reconhecimento facial' },
    { path: '/usuario/perfil', icon: UserRound, name: 'Meu perfil' },
  ];
  // Itens que o perfil não alcança somem do menu; a API bloqueia de qualquer forma.
  const empresa = DEMO_MODE ? [] : [
    ...CADASTROS.filter((c) => !c.apenasAdmin && (user?.level ?? 1) >= c.nivelMinimo).map(itemDoCadastro),
    { path: '/permissoes', icon: KeyRound, name: 'Minhas permissões' },
  ];
  const grupos = [[admin ? 'ADMINISTRAÇÃO' : 'MENU PRINCIPAL', menu], ['EMPRESA', empresa]].filter(([, itens]) => itens.length);
  function leave() { logout(); navigate('/login', { replace: true }); }
  return <div className="app-shell">
    {menuOpen && <button className="mobile-scrim" onClick={() => setMenuOpen(false)} aria-label="Fechar navegação"/>}
    <aside className={`sidebar ${menuOpen ? 'open' : ''}`}>
      <div className="brand"><span className="brand-mark"><ShieldCheck size={29} strokeWidth={2}/></span><div><strong>IRIS<span className="brand-dot">.</span></strong></div><button className="icon-btn mobile-close" onClick={() => setMenuOpen(false)} aria-label="Fechar menu"><X size={18}/></button></div>
      <div className="sidebar-body">
        {grupos.map(([rotulo, itens]) => <React.Fragment key={rotulo}><div className="nav-group-label">{rotulo}</div>
          <nav className="nav-list" aria-label={rotulo}>
            {itens.map(({ path, icon: Icon, name, end }) => <NavLink key={path} end={end} to={path} onClick={() => setMenuOpen(false)} className={({ isActive }) => `nav-item ${isActive ? 'selected' : ''}`}><Icon size={20}/><span>{name}</span></NavLink>)}
          </nav></React.Fragment>)}
        <div className="sidebar-bottom">
          <button className="logout-btn" onClick={leave}><LogOut size={19}/> Sair da conta</button>
        </div>
      </div>
    </aside>
    <div className="shell-right">
      <header className="topbar">
        <div className="topbar-title"><button className="icon-btn menu-trigger" onClick={() => setMenuOpen(true)} aria-label="Abrir menu"><Menu size={22}/></button><span className="breadcrumb">IRIS / <strong>{routeLabels[location.pathname] || 'Painel'}</strong></span></div>
        <div className="topbar-actions"><span className="topbar-role">{admin ? 'Administrador' : 'Usuário'}</span><Avatar name={user?.name}/></div>
      </header>
      <main className="main-content"><DemoNotice/>{children}</main>
    </div>
  </div>;
}
