import React, { useEffect, useState } from 'react';
import { History, Download, Search, AlertCircle } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { recognitionService } from '../services/recognition';
import AccessTable from '../components/AccessTable';
import { PageIntro } from '../components/UI';
import { DEMO_MODE } from '../services/api';
import { dateTime } from '../utils/format';
function safeCsv(value) {
  const plain = String(value ?? '');
  const escaped = /^[=+\-@\t\r]/.test(plain) ? `'${plain}` : plain;
  return `"${escaped.replaceAll('"', '""')}"`;
}
export default function HistoryPage() {
  const { token } = useAuth();
  const [records, setRecords] = useState([]);
  const [query, setQuery] = useState('');
  const [filter, setFilter] = useState('todos');
  const [error, setError] = useState('');
  useEffect(() => { recognitionService.history(token).then(setRecords).catch((e) => setError(e.message)); }, [token]);
  const visible = records.filter((r) => r.user.toLowerCase().includes(query.toLowerCase()) && (filter === 'todos' || (filter === 'permitidos' ? r.allowed : !r.allowed)));
  function exportCsv() {
    const lines = [['Data e hora', 'Usuário', 'Nível solicitado', 'Resultado', 'Origem'], ...visible.map((r) => [dateTime(r.date), r.user, `Nível ${r.level}`, r.allowed ? 'Permitido' : 'Negado', r.source === 'demo' ? 'Simulação' : 'API'])];
    const csv = '\ufeff' + lines.map((line) => line.map(safeCsv).join(';')).join('\r\n');
    const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
    const a = document.createElement('a'); a.href = url; a.download = 'iris-historico.csv'; a.click(); URL.revokeObjectURL(url);
  }
  return <div className="page-fade"><PageIntro eyebrow="ADMINISTRAÇÃO · AUDITORIA" title="Histórico de acessos" description="Consulte as solicitações e o resultado dos níveis de segurança."><button className="btn secondary" onClick={exportCsv} disabled={!visible.length}><Download size={17}/> Exportar CSV</button></PageIntro>
  <div className="filters-row filters-outside"><div className="search-field"><Search size={18}/><input placeholder="Buscar usuário" aria-label="Buscar usuário no histórico" value={query} onChange={(e) => setQuery(e.target.value)}/></div><select className="text-input filter-select" value={filter} onChange={(e) => setFilter(e.target.value)} aria-label="Filtrar resultados"><option value="todos">Todos os resultados</option><option value="permitidos">Autorizados</option><option value="negados">Negados</option></select></div>
  {DEMO_MODE && <div className="info-box compact"><History size={18}/><p>Estes registros são exemplos locais e simulações. Não representam acessos reais ao cofre.</p></div>}{error && <div className="inline-error"><AlertCircle size={17}/>{error}</div>}<AccessTable items={visible}/></div>;
}
