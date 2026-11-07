import React, { useEffect, useState } from 'react';
import { Users, Search, Plus, Pencil, Trash2, ShieldCheck, UserRound, AlertCircle, UserPlus, ScanFace } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { userService } from '../services/users';
import { recognitionService } from '../services/recognition';
import { cadastroService } from '../services/cadastros';
import { PERFIS } from '../data/cadastros';
import { DEMO_MODE } from '../services/api';
import { dateTime } from '../utils/format';
import { Avatar, EmptyState, Modal, PageIntro, StatusPill } from '../components/UI';
const blank = { name: '', cpf: '', email: '', job: '', department: '', level: 1, role: 'user', status: 'Ativo' };
const faceLabel = (samples) => samples == null ? '—' : samples ? `${samples} amostra(s)` : 'Pendente';
function UserForm({ initial, onSubmit, busy, onCancel, error }) {
  const { token } = useAuth();
  const [form, setForm] = useState(initial || blank);
  const [setores, setSetores] = useState([]);
  useEffect(() => { if (!DEMO_MODE) cadastroService.list('setores', token).then(setSetores).catch(() => {}); }, [token]);
  const change = (key, value) => setForm((prev) => ({ ...prev, [key]: value }));
  return <form onSubmit={(event) => { event.preventDefault(); onSubmit(form); }} className="user-form">
    <div className="form-grid"><label className="field-label">Nome completo<input className="text-input" required minLength={3} maxLength={100} value={form.name} onChange={(e) => change('name', e.target.value)} /></label><label className="field-label">CPF<input className="text-input" required={!DEMO_MODE} inputMode="numeric" maxLength={14} value={form.cpf || ''} onChange={(e) => change('cpf', e.target.value)} placeholder="000.000.000-00"/></label><label className="field-label">E-mail<input className="text-input" type="email" required maxLength={120} value={form.email} onChange={(e) => change('email', e.target.value)} placeholder="usuario@exemplo.com"/></label><label className="field-label">Cargo<input className="text-input" required maxLength={80} value={form.job} onChange={(e) => change('job', e.target.value)} placeholder="Analista"/></label><label className="field-label">Setor<input className="text-input" required maxLength={80} list="lista-setores" value={form.department} onChange={(e) => change('department', e.target.value)} placeholder="Produção"/><datalist id="lista-setores">{setores.map((s) => <option key={s.id} value={s.nome}/>)}</datalist></label><label className="field-label">Perfil<select className="text-input" value={form.level} onChange={(e) => change('level', Number(e.target.value))}>{[1, 2, 3].map((n) => <option key={n} value={n}>{PERFIS[n]} (nível {n})</option>)}</select></label><label className="field-label">Administrador<select className="text-input" value={form.role} onChange={(e) => change('role', e.target.value)}><option value="user">Não</option><option value="admin">Sim</option></select></label><label className="field-label">Situação<select className="text-input" value={form.status} onChange={(e) => change('status', e.target.value)}><option>Ativo</option><option>Inativo</option></select></label></div>
    {error && <div className="inline-error"><AlertCircle size={17}/>{error}</div>}<div className="form-footer"><button type="button" className="btn secondary" onClick={onCancel}>Cancelar</button><button type="submit" className="btn primary" disabled={busy}>{busy ? 'Salvando...' : initial ? 'Salvar alterações' : 'Criar usuário'}</button></div>
  </form>;
}
function FaceSamples({ person, token, own, onChanged }) {
  const [samples, setSamples] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  async function load() { try { setSamples(await recognitionService.samples(person.id, token)); } catch (err) { setError(err.message); } }
  useEffect(() => { load(); }, [person.id]);
  async function remove(sampleId) {
    const all = !sampleId;
    const warning = `${all ? `Apagar todas as amostras de ${person.name}` : 'Apagar esta amostra'}?${own && all ? ' Você não conseguirá entrar com o rosto.' : ''}`;
    if (!window.confirm(warning)) return;
    setBusy(true); setError('');
    try { await recognitionService.removeSamples(person.id, sampleId, token); await load(); onChanged(); }
    catch (err) { setError(err.message); } finally { setBusy(false); }
  }
  return <div className="user-form">
    {error && <div className="inline-error"><AlertCircle size={16}/>{error}</div>}
    {samples === null ? <p className="help-text">Carregando...</p> : samples.length === 0
      ? <EmptyState icon={ScanFace} title="Nenhuma amostra"/>
      : <div className="table-scroll"><table className="data-table"><thead><tr><th>#</th><th>Capturada em</th><th>Brilho</th><th>Nitidez</th><th>Confiança</th><th></th></tr></thead><tbody>{samples.map((s) => <tr key={s.id}><td>{s.order}</td><td className="muted-td">{dateTime(s.capturedAt)}</td><td>{s.brightness?.toFixed(0) ?? '—'}</td><td>{s.sharpness?.toFixed(0) ?? '—'}</td><td>{s.confidence?.toFixed(2) ?? '—'}</td><td><button className="icon-btn danger" title="Apagar amostra" disabled={busy} onClick={() => remove(s.id)}><Trash2 size={16}/></button></td></tr>)}</tbody></table></div>}
    <div className="form-footer">{samples?.length > 0 && <button type="button" className="btn secondary" disabled={busy} onClick={() => remove(null)}><Trash2 size={16}/> Apagar todas</button>}</div>
  </div>;
}
export default function UsersPage() {
  const { token, user: sessionUser } = useAuth();
  const [users, setUsers] = useState([]);
  const [query, setQuery] = useState('');
  const [filter, setFilter] = useState('todos');
  const [editing, setEditing] = useState(null);
  const [modal, setModal] = useState(false);
  const [faces, setFaces] = useState(null);
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
    if (!window.confirm(`Excluir ${u.name}?`)) return;
    try { await userService.remove(u.id, token); await refresh(); } catch (err) { setPageError(err.message); }
  }
  const visible = users.filter((u) => {
    const s = `${u.name} ${u.email} ${u.department}`.toLowerCase();
    return s.includes(query.toLowerCase()) && (filter === 'todos' || u.status === filter || u.role === filter);
  });
  return <div className="page-fade"><PageIntro title="Usuários"><button className="btn primary" onClick={() => { setEditing(null); setError(''); setModal(true); }}><Plus size={18}/> Novo usuário</button></PageIntro>
    <section className="card management-card"><div className="management-head"><div><h2><Users size={21}/> Usuários <span className="count-chip">{users.length}</span></h2></div></div><div className="filters-row"><div className="search-field"><Search size={18}/><input aria-label="Pesquisar usuários" placeholder="Pesquisar" value={query} onChange={(e) => setQuery(e.target.value)}/></div><select className="text-input filter-select" aria-label="Filtrar usuários" value={filter} onChange={(e) => setFilter(e.target.value)}><option value="todos">Todos os usuários</option><option value="Ativo">Ativos</option><option value="Inativo">Inativos</option><option value="admin">Administradores</option><option value="user">Usuários comuns</option></select></div>
    {pageError && <div className="inline-error"><AlertCircle size={16}/>{pageError}</div>}
    {visible.length ? <div className="table-scroll"><table className="data-table users-table"><thead><tr><th>Usuário</th><th>Cargo / Setor</th><th>Função</th><th>Perfil</th><th>Biometria</th><th>Situação</th><th>Ações</th></tr></thead><tbody>{visible.map((u) => <tr key={u.id}><td><div className="table-person"><Avatar name={u.name}/><span><strong>{u.name}</strong><small>{u.email}</small></span></div></td><td><div className="two-line"><strong>{u.job}</strong><small>{u.department}</small></div></td><td><span className="tiny-tag">{u.role === 'admin' ? <ShieldCheck size={13}/> : <UserRound size={13}/>} {u.role === 'admin' ? 'Administrador' : 'Usuário'}</span></td><td><span className="level-number">{PERFIS[u.level]} · nível {u.level}</span></td><td>{faceLabel(u.faceSamples)}</td><td><StatusPill allowed={u.status === 'Ativo'} text={u.status}/></td><td><div className="row-actions">{!DEMO_MODE && <button className="icon-btn" title="Cadastros faciais" onClick={() => setFaces(u)}><ScanFace size={17}/></button>}<button className="icon-btn" title="Editar" onClick={() => { setEditing(u); setError(''); setModal(true); }}><Pencil size={17}/></button><button className="icon-btn danger" title="Excluir" disabled={u.id === sessionUser.id} onClick={() => remove(u)}><Trash2 size={17}/></button></div></td></tr>)}</tbody></table></div> : <EmptyState icon={UserPlus} title="Nenhum usuário encontrado"/>}</section>
    {modal && <Modal title={editing ? 'Editar usuário' : 'Cadastrar usuário'} onClose={() => { setModal(false); setEditing(null); }}><UserForm initial={editing} busy={busy} error={error} onCancel={() => { setModal(false); setEditing(null); }} onSubmit={save}/></Modal>}
    {faces && <Modal title={`Cadastros faciais · ${faces.name}`} onClose={() => setFaces(null)}><FaceSamples person={faces} token={token} own={faces.id === sessionUser.id} onChanged={refresh}/></Modal>}
  </div>;
}
