import React, { useState } from 'react';
import { Settings, Server, Database, ShieldCheck, RotateCcw, CheckCircle2 } from 'lucide-react';
import { DEMO_MODE } from '../services/api';
import { demoStore } from '../data/demo';
import { PageIntro, SectionHeading } from '../components/UI';
export default function SettingsPage() {
  const [reset, setReset] = useState(false);
  function clearDemo() { if (!window.confirm('Restaurar os dados de demonstração?')) return; demoStore.reset(); setReset(true); }
  const modulos = [['Front-end', ShieldCheck, true], ['API Python', Server, !DEMO_MODE], ['Banco de dados', Database, !DEMO_MODE]];
  return <div className="page-fade"><PageIntro title="Configurações"/><section className="card settings-card"><SectionHeading title="Módulos" icon={Settings}/><div className="module-list">
    {modulos.map(([nome, Icone, ligado]) => <div key={nome}><span className="stat-icon blue"><Icone size={22}/></span><div><strong>{nome}</strong></div><span className={`status-pill ${ligado ? 'allowed' : 'denied'}`}>{ligado ? 'Conectado' : 'Desligado'}</span></div>)}
  </div>{DEMO_MODE && <div className="settings-reset"><div><strong>Dados de demonstração</strong></div><button className="btn secondary" onClick={clearDemo}><RotateCcw size={17}/> Restaurar</button></div>}{reset && <div className="inline-success"><CheckCircle2 size={16}/> Dados restaurados. Recarregue a página.</div>}</section></div>;
}
