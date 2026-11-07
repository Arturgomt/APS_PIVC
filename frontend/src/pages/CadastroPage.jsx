import React, { useEffect, useState } from 'react';
import { AlertCircle, BadgeCheck, Lock, Pencil, Plus, Search, Trash2 } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { cadastroService } from '../services/cadastros';
import { NIVEIS } from '../data/cadastros';
import { dateOnly, dateTime } from '../utils/format';
import { EmptyState, Modal, PageIntro } from '../components/UI';
// Só o Ministro escolhe o setor de um item; os demais gravam no próprio setor (regra da API).
const CAMPO_SETOR = { k: 'setor_id', l: 'Setor', tipo: 'ref', ref: 'setores', nome: 'setor', req: true };
const camposDoFormulario = (config, user) => !config.estrutural && user.level === 3 ? [...config.campos, CAMPO_SETOR] : config.campos;

const componentesParaTexto = (lista = []) => lista.map((c) => `${c.nome}; ${c.cas || ''}; ${c.percentual}`).join('\n');
const textoParaComponentes = (texto) => texto.split('\n').map((linha) => linha.trim()).filter(Boolean).map((linha) => {
  const [nome, cas = '', percentual = ''] = linha.split(';').map((parte) => parte.trim());
  return { nome, cas, percentual: Number(percentual.replace('%', '').replace(',', '.')) };
});

function Situacao({ item }) {
  const aprovado = item.status === 'aprovado';
  return <span className={`status-pill ${aprovado ? 'allowed' : 'draft'}`}><span className="status-dot"/>{aprovado ? 'Aprovado' : 'Rascunho'}</span>;
}

function Valor({ campo, item }) {
  const valor = item[campo.k];
  if (campo.tipo === 'ref') return item[campo.nome] || '—';
  if (campo.tipo === 'date') return dateOnly(valor);
  if (campo.tipo === 'nivel') return `Nível ${valor} · ${NIVEIS[valor]}`;
  if (campo.tipo === 'componentes') {
    const total = (valor || []).reduce((soma, c) => soma + c.percentual, 0);
    return <table className="data-table"><thead><tr><th>Componente</th><th>Nº CAS</th><th>%</th></tr></thead><tbody>
      {(valor || []).map((c) => <tr key={c.nome}><td>{c.nome}</td><td>{c.cas || '—'}</td><td>{c.percentual.toLocaleString('pt-BR')}</td></tr>)}
      <tr><td><strong>Total</strong></td><td/><td><strong>{total.toLocaleString('pt-BR')}</strong></td></tr></tbody></table>;
  }
  return valor === null || valor === undefined || valor === '' ? '—' : <span className="pre-text">{String(valor)}</span>;
}

function Campo({ campo, value, onChange, opcoes, user }) {
  const props = { className: 'text-input', value, required: campo.req, onChange: (e) => onChange(e.target.value) };
  if (campo.tipo === 'textarea' || campo.tipo === 'componentes') return <textarea {...props} rows={campo.tipo === 'componentes' ? 7 : 5} placeholder={campo.tipo === 'componentes' ? 'Água deionizada; 7732-18-5; 62' : campo.ph}/>;
  if (campo.tipo === 'select') return <select {...props}>{campo.opcoes.map((o) => <option key={o}>{o}</option>)}</select>;
  if (campo.tipo === 'nivel') return <select {...props}>{[1, 2, 3].filter((n) => n <= user.level).map((n) => <option key={n} value={n}>Nível {n} · {NIVEIS[n]}</option>)}</select>;
  if (campo.tipo === 'ref') return <select {...props}><option value="">{campo.req ? 'Selecione' : 'Nenhum'}</option>{(opcoes || []).map((o) => <option key={o.id} value={o.id}>{o.codigo ? `${o.codigo} · ${o.nome}` : o.nome}</option>)}</select>;
  return <input {...props} placeholder={campo.ph} type={campo.tipo || 'text'} min={campo.tipo === 'number' ? 0 : undefined} step={campo.tipo === 'number' ? 'any' : undefined}/>;
}

function Formulario({ config, inicial, onSaved, onCancel }) {
  const { token, user } = useAuth();
  const campos = camposDoFormulario(config, user);
  const inicialDe = (c) => {
    const v = inicial?.[c.k];
    if (c.tipo === 'componentes') return componentesParaTexto(v);
    if (c.tipo === 'select') return v ?? c.opcoes[0];
    if (c.tipo === 'nivel') return v ?? 1;
    if (c.tipo === 'number') return v ?? 0;
    return v ?? '';
  };
  const [form, setForm] = useState(() => Object.fromEntries(campos.map((c) => [c.k, inicialDe(c)])));
  const [opcoes, setOpcoes] = useState({});
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  useEffect(() => {
    [...new Set(campos.filter((c) => c.tipo === 'ref').map((c) => c.ref))].forEach((ref) =>
      cadastroService.list(ref, token).then((lista) => setOpcoes((atual) => ({ ...atual, [ref]: lista }))).catch(() => {}));
  }, []);
  const converter = (c, v) => {
    if (c.tipo === 'componentes') return textoParaComponentes(v);
    if (c.tipo === 'number' || c.tipo === 'nivel') return Number(v);
    if (c.tipo === 'ref') return v === '' ? null : Number(v);
    if (c.tipo === 'date') return v || null;
    return v;
  };
  async function submit(event) {
    event.preventDefault(); setBusy(true); setError('');
    try { onSaved(await cadastroService.save(config.rota, Object.fromEntries(campos.map((c) => [c.k, converter(c, form[c.k])])), inicial?.id, token)); }
    catch (err) { setError(err.message); setBusy(false); }
  }
  return <form onSubmit={submit} className="user-form">
    <div className="form-grid">{campos.map((c) => <label key={c.k} className={`field-label ${c.largo ? 'wide' : ''}`}>{c.l}
      <Campo campo={c} value={form[c.k]} opcoes={opcoes[c.ref]} user={user} onChange={(v) => setForm((atual) => ({ ...atual, [c.k]: v }))}/>
      {c.tipo === 'componentes' && <small className="help-text">Um por linha: nome; CAS; %. Total: {textoParaComponentes(form[c.k]).reduce((s, x) => s + (x.percentual || 0), 0).toLocaleString('pt-BR')}%</small>}
    </label>)}</div>
    {error && <div className="inline-error"><AlertCircle size={17}/>{error}</div>}
    <div className="form-footer"><button type="button" className="btn secondary" onClick={onCancel}>Cancelar</button><button type="submit" className="btn primary" disabled={busy}>{busy ? 'Salvando...' : 'Salvar'}</button></div>
  </form>;
}

function Detalhe({ config, item, busy, error, onEdit, onApprove, onDelete }) {
  const metadados = config.estrutural ? [] : [
    ['Setor', item.setor], ['Sigilo', `Nível ${item.nivel_sigilo} · ${NIVEIS[item.nivel_sigilo]}`], ['Situação', <Situacao item={item}/>],
    ['Criado por', item.autor || 'Dados de exemplo'], ['Aprovado por', item.aprovador ? `${item.aprovador} · ${dateTime(item.aprovado_em)}` : '—'],
  ];
  const linhas = [...config.campos.filter((c) => c.tipo !== 'nivel').map((c) => [c.l, <Valor campo={c} item={item}/>, c.largo]), ...metadados];
  return <div className="user-form">
    {item.nivel_sigilo === 3 && <div className="info-box compact"><Lock size={17}/><p>Confidencial. Este acesso foi registrado.</p></div>}
    <div className="profile-grid">{linhas.map(([rotulo, valor, largo]) => <div key={rotulo} className={largo ? 'wide' : ''}><span>{rotulo}</span><strong>{valor}</strong></div>)}</div>
    {error && <div className="inline-error"><AlertCircle size={17}/>{error}</div>}
    <div className="form-footer">
      {item.podeExcluir && <button className="btn secondary" disabled={busy} onClick={onDelete}><Trash2 size={16}/> Excluir</button>}
      {item.podeEditar && <button className="btn secondary" disabled={busy} onClick={onEdit}><Pencil size={16}/> Editar</button>}
      {item.podeAprovar && <button className="btn primary" disabled={busy} onClick={onApprove}><BadgeCheck size={16}/> Aprovar</button>}
    </div>
  </div>;
}

export default function CadastroPage({ config }) {
  const { token } = useAuth();
  const [itens, setItens] = useState(null);
  const [erro, setErro] = useState('');
  const [busca, setBusca] = useState('');
  const [podeCriar, setPodeCriar] = useState(false);
  const [aberto, setAberto] = useState(null);
  const [editando, setEditando] = useState(null); // null, 'novo' ou o item
  const [acao, setAcao] = useState({ busy: false, erro: '' });
  const Icone = config.icone;

  async function carregar() {
    try { setItens(await cadastroService.list(config.rota, token)); setErro(''); } catch (err) { setErro(err.message); }
  }
  useEffect(() => {
    carregar();
    cadastroService.permissions(token).then((p) => setPodeCriar(p.regras.some((r) => r.rota === config.rota && r.criar))).catch(() => {});
  }, [token]);
  async function abrir(item) {
    setAcao({ busy: false, erro: '' });
    try { setAberto(await cadastroService.get(config.rota, item.id, token)); } catch (err) { setErro(err.message); }
  }
  async function executar(operacao, fechar = false) {
    setAcao({ busy: true, erro: '' });
    try { const item = await operacao(); await carregar(); setAberto(fechar ? null : item); setAcao({ busy: false, erro: '' }); }
    catch (err) { setAcao({ busy: false, erro: err.message }); }
  }
  function salvo(item) { setEditando(null); setAberto(item); carregar(); }

  const termo = busca.toLowerCase();
  const visiveis = (itens || []).filter((i) => !termo || config.colunas.some(([k]) => String(i[k] ?? '').toLowerCase().includes(termo)));
  const pendentes = (itens || []).filter((i) => i.podeAprovar).length;

  return <div className="page-fade"><PageIntro title={config.titulo}>
    {podeCriar && <button className="btn primary" onClick={() => setEditando('novo')}><Plus size={18}/> {config.feminino ? "Nova" : "Novo"} {config.singular}</button>}</PageIntro>
    <section className="card management-card">
      <div className="management-head"><div><h2><Icone size={21}/> {config.titulo} <span className="count-chip">{visiveis.length}</span>{pendentes > 0 && <span className="status-pill draft">{pendentes} para aprovar</span>}</h2></div></div>
      <div className="filters-row"><div className="search-field"><Search size={18}/><input aria-label={`Pesquisar ${config.titulo}`} placeholder="Pesquisar" value={busca} onChange={(e) => setBusca(e.target.value)}/></div></div>
      {erro && <div className="inline-error"><AlertCircle size={16}/>{erro}</div>}
      {itens === null ? <p className="help-text">Carregando...</p> : visiveis.length === 0
        ? <EmptyState icon={Icone} title="Nenhum registro"/>
        : <div className="table-scroll"><table className="data-table"><thead><tr>{config.colunas.map(([k, rotulo]) => <th key={k}>{rotulo}</th>)}{!config.estrutural && <><th>Setor</th><th>Sigilo</th><th>Situação</th></>}</tr></thead>
          <tbody>{visiveis.map((i) => <tr key={i.id} className="clickable-row" onClick={() => abrir(i)}>
            {config.colunas.map(([k, , formatar]) => <td key={k}>{formatar ? formatar(i[k], i) : (i[k] ?? '—')}</td>)}
            {!config.estrutural && <><td>{i.setor}</td><td><span className="tiny-tag">Nível {i.nivel_sigilo}</span></td><td><Situacao item={i}/></td></>}
          </tr>)}</tbody></table></div>}
    </section>
    {aberto && !editando && <Modal title={aberto.nome || aberto.titulo || `${aberto.produto} · versão ${aberto.versao}`} onClose={() => setAberto(null)}>
      <Detalhe config={config} item={aberto} busy={acao.busy} error={acao.erro} onEdit={() => setEditando(aberto)}
        onApprove={() => executar(() => cadastroService.approve(config.rota, aberto.id, token))}
        onDelete={() => window.confirm(`Excluir ${config.singular} definitivamente?`) && executar(() => cadastroService.remove(config.rota, aberto.id, token), true)}/>
    </Modal>}
    {editando && <Modal title={editando === 'novo' ? `${config.feminino ? 'Nova' : 'Novo'} ${config.singular}` : `Editar ${config.singular}`} onClose={() => setEditando(null)}>
      <Formulario config={config} inicial={editando === 'novo' ? null : editando} onSaved={salvo} onCancel={() => setEditando(null)}/>
    </Modal>}
  </div>;
}
