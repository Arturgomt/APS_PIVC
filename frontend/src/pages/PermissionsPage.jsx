import React, { useEffect, useState } from 'react';
import { AlertCircle, Building2, KeyRound, ShieldCheck, UserRound, Layers } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { cadastroService } from '../services/cadastros';
import { NIVEIS } from '../data/cadastros';
import { PageIntro, SectionHeading } from '../components/UI';
const COLUNAS = [['verProprioSetor', 'Ver no seu setor'], ['verOutrosSetores', 'Ver em outros setores'], ['criar', 'Criar rascunho'],
  ['editarAprovado', 'Editar aprovado'], ['aprovar', 'Aprovar'], ['excluir', 'Excluir']];
const HIERARQUIA = [
  ['Analista', 'Nível 1', 'Itens internos'],
  ['Diretor', 'Nível 2', 'Itens internos e restritos do próprio setor'],
  ['Ministro', 'Nível 3', 'Todos os itens'],
  ['Administrador', '—', 'Usuários, setores, instalações e rostos'],
];
const marca = (sim) => sim ? <span className="check-yes" aria-label="sim">✓</span> : <span className="check-no" aria-label="não">—</span>;

export default function PermissionsPage() {
  const { token } = useAuth();
  const [dados, setDados] = useState(null);
  const [erro, setErro] = useState('');
  useEffect(() => { cadastroService.permissions(token).then(setDados).catch((e) => setErro(e.message)); }, [token]);
  const cartoes = dados && [
    ['Perfil', dados.perfil, UserRound, 'blue'], ['Nível de acesso', `${dados.nivel} · ${NIVEIS[dados.nivel]}`, Layers, 'cyan'],
    ['Setor', dados.setor || 'Sem setor', Building2, 'green'], ['Administrador', dados.administrador ? 'Sim' : 'Não', ShieldCheck, 'red'],
  ];
  return <div className="page-fade"><PageIntro title="Minhas permissões"/>
    {erro && <div className="inline-error big"><AlertCircle size={18}/>{erro}</div>}
    {dados && <>
      <div className="stats-grid">{cartoes.map(([rotulo, valor, Icone, cor]) => <div key={rotulo} className="stat-card"><div className="stat-top"><span className={`stat-icon ${cor}`}><Icone size={21}/></span></div><div className="stat-value" style={{ fontSize: 20 }}>{valor}</div><div className="stat-label">{rotulo}</div></div>)}</div>
      <section className="card"><SectionHeading title="Permissões" icon={KeyRound}/>
        <div className="table-scroll"><table className="data-table"><thead><tr><th>Cadastro</th>{COLUNAS.map(([k, rotulo]) => <th key={k}>{rotulo}</th>)}</tr></thead>
          <tbody>{dados.regras.map((r) => <tr key={`${r.rota}-${r.nivel}`}><td><strong>{r.cadastro}</strong>{r.nivel && <small className="help-text"> · nível {r.nivel}</small>}</td>{COLUNAS.map(([k]) => <td key={k}>{marca(r[k])}</td>)}</tr>)}</tbody></table></div>
      </section>
      <section className="card" style={{ marginTop: 20 }}><SectionHeading title="Hierarquia" icon={Layers}/>
        <div className="table-scroll"><table className="data-table"><thead><tr><th>Perfil</th><th>Nível</th><th>Acesso</th></tr></thead>
          <tbody>{HIERARQUIA.map(([perfil, nivel, texto]) => <tr key={perfil} style={perfil === dados.perfil ? { background: '#17304d' } : undefined}><td><strong>{perfil}</strong></td><td>{nivel}</td><td style={{ whiteSpace: 'normal' }}>{texto}</td></tr>)}</tbody></table></div>
      </section>
    </>}
  </div>;
}
