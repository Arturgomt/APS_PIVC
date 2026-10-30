import React, { useEffect, useState } from 'react';
import { Users, Search, Plus, Pencil, Trash2, ShieldCheck, UserRound, AlertCircle, UserPlus } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { userService } from '../services/users';
import { Avatar, EmptyState, Modal, PageIntro, StatusPill } from '../components/UI';

const blank = { name: '', email: '', job: '', department: '', level: 1, role: 'user', status: 'Ativo' };
function UserForm({ initial, onSubmit, busy, onCancel, error }) {
  const [form, setForm] = useState(initial || blank);
  const change = (key, value) => setForm((prev) => ({ ...prev, [key]: value }));
  return <form onSubmit={(event) => { event.preventDefault(); onSubmit(form); }} className="user-form">
    <div className="form-grid"><label className="field-label">Nome completo<input className="text-input" required minLength={3} maxLength={100} value={form.name} onChange={(e) => change('name', e.target.value)} placeholder="Nome do colaborador"/></label><label className="field-label">E-mail<input className="text-input" type="email" required maxLength={120} value={form.email} onChange={(e) => change('email', e.target.value)} placeholder="usuario@exemplo.com"/></label><label className="field-label">Cargo<input className="text-input" required maxLength={80} value={form.job} onChange={(e) => change('job', e.target.value)} placeholder="Analista"/></label><label className="field-label">Departamento<input className="text-input" required maxLength={80} value={form.department} onChange={(e) => change('department', e.target.value)} placeholder="Operações"/></label><label className="field-label">Nível de permissão<select className="text-input" value={form.level} onChange={(e) => change('level', Number(e.target.value))}><option value={1}>Nível 1 — Geral</option><option value={2}>Nível 2 — Diretores</option><option value={3}>Nível 3 — Ministro(a)</option></select></label><label className="field-label">Perfil de sistema<select className="text-input" value={form.role} onChange={(e) => change('role', e.target.value)}><option value="user">Usuário</option><option value="admin">Administrador</option></select></label><label className="field-label">Situação<select className="text-input" value={form.status} onChange={(e) => change('status', e.target.value)}><option>Ativo</option><option>Inativo</option></select></label></div>
    <p className="help-text">O perfil define quais telas aparecem no React. O nível define a permissão de acesso ao cofre. A validação real caberá à API.</p>{error && <div className="inline-error"><AlertCircle size={17}/>{error}</div>}<div className="form-footer"><button type="button" className="btn secondary" onClick={onCancel}>Cancelar</button><button type="submit" className="btn primary" disabled={busy}>{busy ? 'Salvando...' : initial ? 'Salvar alterações' : 'Criar usuário'}</button></div>
  </form>;
}
export default function UsersPage() {
  const { token, user: sessionUser } = useAuth();
  const [users, setUsers] = useState([]);
  const [query, setQuery] = useState('');
  const [filter, setFilter] = useState('todos');
  const [editing, setEditing] = useState(null);
  const [modal, setModal] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [pageError, setPageError] = useState('');
  async function refresh() { try { setUsers(await userService.list(token)); setPageError(''); } catch (err) { setPageError(err.message); } }
  useEffect(() => { refresh(); }, [token]);
  async function save(data) {
    setBusy(true); setError('');
    try {
      const clean = { ...data, name: data.name.trim(), email: data.email.toLowerCase().trim(), job: data.job.trim(), department: data.department.trim(), level: Number(data.level) };
      if (editing) await userService.update(editing.id, clean, token); else await userService.create(clean, token);
      setModal(false); setEditing(null); await refresh();
    } catch (err) { setError(err.message); } finally { setBusy(false); }
  }
  async function remove(u) {
    if (u.id === sessionUser.id) { setPageError('Não é permitido excluir a própria conta durante a sessão.'); return; }
    if (!window.confirm(`Excluir o usuário ${u.name}?`)) return;
    try { await userService.remove(u.id, token); await refresh(); } catch (err) { setPageError(err.message); }
  }
  const visible = users.filter((u) => {
    const s = `${u.name} ${u.email} ${u.department}`.toLowerCase();
    return s.includes(query.toLowerCase()) && (filter === 'todos' || u.status === filter || u.role === filter);
  });
  return <div className="page-fade"><PageIntro eyebrow="ADMINISTRAÇÃO · USUÁRIOS" title="Gestão de usuários" description="Cadastre colaboradores, defina funções e gerencie as permissões do cofre."><button className="btn primary" onClick={() => { setEditing(null); setError(''); setModal(true); }}><Plus size={18}/> Novo usuário</button></PageIntro>
    <section className="card management-card"><div className="management-head"><div><h2><Users size={21}/> Usuários cadastrados <span className="count-chip">{users.length}</span></h2><p>Gerencie os perfis associados ao ambiente.</p></div></div><div className="filters-row"><div className="search-field"><Search size={18}/><input aria-label="Pesquisar usuários" placeholder="Pesquisar por nome, e-mail ou departamento" value={query} onChange={(e) => setQuery(e.target.value)}/></div><select className="text-input filter-select" aria-label="Filtrar usuários" value={filter} onChange={(e) => setFilter(e.target.value)}><option value="todos">Todos os usuários</option><option value="Ativo">Ativos</option><option value="Inativo">Inativos</option><option value="admin">Administradores</option><option value="user">Usuários comuns</option></select></div>
    {pageError && <div className="inline-error"><AlertCircle size={16}/>{pageError}</div>}
    {visible.length ? <div className="table-scroll"><table className="data-table users-table"><thead><tr><th>Usuário</th><th>Cargo / Departamento</th><th>Perfil</th><th>Nível</th><th>Situação</th><th>Ações</th></tr></thead><tbody>{visible.map((u) => <tr key={u.id}><td><div className="table-person"><Avatar name={u.name}/><span><strong>{u.name}</strong><small>{u.email}</small></span></div></td><td><div className="two-line"><strong>{u.job}</strong><small>{u.department}</small></div></td><td><span className="tiny-tag">{u.role === 'admin' ? <ShieldCheck size={13}/> : <UserRound size={13}/>} {u.role === 'admin' ? 'Administrador' : 'Usuário'}</span></td><td><span className="level-number">Nível {u.level}</span></td><td><StatusPill allowed={u.status === 'Ativo'} text={u.status}/></td><td><div className="row-actions"><button className="icon-btn" title="Editar" onClick={() => { setEditing(u); setError(''); setModal(true); }}><Pencil size={17}/></button><button className="icon-btn danger" title="Excluir" disabled={u.id === sessionUser.id} onClick={() => remove(u)}><Trash2 size={17}/></button></div></td></tr>)}</tbody></table></div> : <EmptyState icon={UserPlus} title="Nenhum usuário encontrado" description="Altere os filtros ou adicione um novo usuário."/>}</section>
    {modal && <Modal title={editing ? 'Editar usuário' : 'Cadastrar usuário'} onClose={() => { setModal(false); setEditing(null); }}><UserForm initial={editing} busy={busy} error={error} onCancel={() => { setModal(false); setEditing(null); }} onSubmit={save}/></Modal>}
  </div>;
}
