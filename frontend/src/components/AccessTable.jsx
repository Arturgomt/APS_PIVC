import React from 'react';
import { History, ArrowUpRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { dateTime, levelLabel, sourceLabel } from '../utils/format';
import { Avatar, EmptyState, SectionHeading, StatusPill } from './UI';
export default function AccessTable({ items = [], preview = false }) {
  const shown = preview ? items.slice(0, 5) : items;
  return <section className="card access-history"><SectionHeading title="Histórico de acessos" icon={History}>{preview && <Link to="/admin/historico" className="text-link">Ver todos <ArrowUpRight size={16}/></Link>}</SectionHeading>
    {shown.length === 0 ? <EmptyState icon={History} title="Sem registros"/> : <div className="table-scroll"><table className="data-table"><thead><tr><th>Data e hora</th><th>Usuário</th><th>Nível solicitado</th><th>Resultado</th><th>Origem</th></tr></thead><tbody>{shown.map((item) => <tr key={item.id}><td className="muted-td">{dateTime(item.date)}</td><td><div className="table-person"><Avatar name={item.user} size="tiny"/><span>{item.user}</span></div></td><td>{levelLabel(item.level, item.source)}</td><td><StatusPill allowed={item.allowed}/></td><td><span className="tiny-tag" title={item.reason}>{sourceLabel(item.source)}</span></td></tr>)}</tbody></table></div>}</section>;
}
