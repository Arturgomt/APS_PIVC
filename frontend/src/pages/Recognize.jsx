import React, { useState } from 'react';
import { ScanFace, ShieldCheck, AlertCircle, LockKeyhole, CheckCircle2, XCircle } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { DEMO_MODE } from '../services/api';
import { recognitionService } from '../services/recognition';
import { Avatar, PageIntro, SectionHeading, LoadText } from '../components/UI';
import CameraPanel from '../components/CameraPanel';
import AccessLevelSelect from '../components/AccessLevelSelect';
export default function Recognize({ embedded = false }) {
  const { user, token } = useAuth();
  const [level, setLevel] = useState(1);
  const [image, setImage] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  async function doRecognize() {
    setLoading(true); setError(''); setResult(null);
    try { setResult(await recognitionService.recognize({ image, level, token, demoUser: user })); }
    catch (err) { setError(err.message || 'Falha no reconhecimento.'); }
    finally { setLoading(false); }
  }
  // Na API, a identidade vem do rosto capturado, não da sessão.
  const person = DEMO_MODE ? user : result?.user;
  const identityTag = DEMO_MODE ? 'SESSÃO DEMO' : person ? 'IDENTIFICADO' : 'AGUARDANDO';
  return <div className="page-fade">{!embedded && <PageIntro title="Reconhecimento facial"/>}
    <div className="recognition-layout"><section className="card camera-card"><SectionHeading icon={ScanFace} title="Captura facial"/><CameraPanel onCapture={setImage}/></section>
    <div className="recognition-side"><section className="card identification-card"><SectionHeading title="Identificação" icon={ShieldCheck}/><div className="identity-row"><Avatar name={person?.name} size="large"/><div><strong>{person?.name || 'Não identificado'}</strong><small>{person?.job || '—'}</small><span className="id-tag">{identityTag}</span></div></div><div className="identity-meta"><div><small>Nível cadastrado</small><strong>{person ? `Nível ${person.level}` : '—'}</strong></div><div><small>Setor</small><strong>{person?.department || '—'}</strong></div></div></section>
    <section className="card"><SectionHeading title="Nível de acesso" icon={LockKeyhole}/><AccessLevelSelect value={level} onChange={setLevel}/></section></div></div>
    <div className="recognize-footer"><div/><button type="button" className="btn primary large" disabled={loading || (!DEMO_MODE && !image)} onClick={doRecognize}><ScanFace size={19}/><LoadText loading={loading}>{DEMO_MODE ? 'Simular verificação' : 'Verificar acesso'}</LoadText></button></div>
    {error && <div className="inline-error big"><AlertCircle size={18}/>{error}</div>}
    {result && <div className={`result-card ${result.authorized ? 'ok' : 'no'}`}><span className="result-icon">{result.authorized ? <CheckCircle2 size={29}/> : <XCircle size={29}/>}</span><div><strong>{result.simulated ? `Simulação: acesso ${result.authorized ? 'permitido' : 'negado'}` : `Acesso ${result.authorized ? 'autorizado' : 'negado'}`}</strong><p>{result.reason || `Solicitação para o nível ${level}.`}</p>{result.confidence != null && <small>Similaridade: {result.confidence.toFixed(3)}</small>}{result.resource && <div className="info-box compact"><LockKeyhole size={17}/><p><strong>{result.resource.title}:</strong> {result.resource.content}</p></div>}</div></div>}
  </div>;
}
