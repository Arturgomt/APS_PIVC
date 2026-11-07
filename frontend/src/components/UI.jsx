import React from 'react';
import { Search, ShieldCheck, X, LoaderCircle } from 'lucide-react';
import { DEMO_MODE } from '../services/api';
import { initials } from '../utils/format';

export function DemoNotice({ children }) {
  return DEMO_MODE && <div className="demo-notice"><span className="demo-dot" /> <strong>Ambiente de demonstração</strong><span className="demo-notice-extra">{children || 'Sem reconhecimento biométrico ou controle de acesso real.'}</span></div>;
}
export function Avatar({ name, size = '' }) { return <span className={`avatar ${size}`} aria-label={name}>{initials(name)}</span>; }
export function StatusPill({ allowed, text }) { return <span className={`status-pill ${allowed ? 'allowed' : 'denied'}`}><span className="status-dot" />{text || (allowed ? 'Autorizado' : 'Negado')}</span>; }
export function EmptyState({ icon: Icon = Search, title, description }) { return <div className="empty"><Icon size={26} /><strong>{title}</strong>{description && <span>{description}</span>}</div>; }
export function PageIntro({ eyebrow, title, description, children }) { return <div className="page-intro"><div><div className="eyebrow">{eyebrow}</div><h1>{title}</h1><p>{description}</p></div>{children}</div>; }
export function SectionHeading({ icon: Icon = ShieldCheck, title, children }) { return <div className="section-heading"><h2><Icon size={19}/>{title}</h2>{children}</div>; }
export function Modal({ title, children, onClose }) { return <div className="modal-backdrop" onMouseDown={(e) => { if (e.target === e.currentTarget) onClose(); }}><div className="modal" role="dialog" aria-modal="true" aria-label={title}><div className="modal-top"><h2>{title}</h2><button aria-label="Fechar" className="icon-btn" onClick={onClose}><X size={20}/></button></div>{children}</div></div>; }
export function LoadText({ loading, children }) { return <>{loading && <LoaderCircle className="spin" size={16}/>} {children}</>; }
