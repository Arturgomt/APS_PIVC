import React, { useState } from 'react';
import { ScanFace, ShieldCheck, AlertCircle, LockKeyhole, CheckCircle2, XCircle, Info } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { DEMO_MODE } from '../services/api';
import { recognitionService } from '../services/recognition';
import CameraPanel from '../components/CameraPanel';
import AccessLevelSelect from '../components/AccessLevelSelect';
import { Avatar, PageIntro, SectionHeading, LoadText } from '../components/UI';

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
  return <div className="page-fade">{!embedded && <PageIntro eyebrow="IDENTIFICAÇÃO BIOMÉTRICA" title="Reconhecimento facial" description="Solicite acesso ao ambiente de segurança utilizando a câmera."/>}
    <div className="recognition-layout"><section className="card camera-card"><SectionHeading icon={ScanFace} title="Captura facial"><span className="eyebrow mini">ETAPA 01</span></SectionHeading><CameraPanel onCapture={setImage}/>
    <div className="camera-footnote"><Info size={16}/> {image ? 'Imagem pronta para envio.' : 'A câmera só é ativada após sua permissão.'}</div></section>
    <div className="recognition-side"><section className="card identification-card"><SectionHeading title="Identificação" icon={ShieldCheck}/><div className="identity-row"><Avatar name={user?.name} size="large"/><div><strong>{user?.name || 'Não identificado'}</strong><small>{user?.job || 'Usuário'}</small><span className="id-tag">{DEMO_MODE ? 'IDENTIDADE DA SESSÃO DEMO' : 'USUÁRIO LOGADO'}</span></div></div><div className="identity-meta"><div><small>Nível cadastrado</small><strong>Nível {user?.level ?? '—'}</strong></div><div><small>Departamento</small><strong>{user?.department || '—'}</strong></div></div></section>
    <section className="card"><SectionHeading title="Selecionar nível de acesso" icon={LockKeyhole}/><AccessLevelSelect value={level} onChange={setLevel}/></section></div></div>
    <div className="recognize-footer"><div><h3>Pronto para verificar o acesso?</h3><p>{DEMO_MODE ? 'O botão executa apenas uma simulação das permissões, sem reconhecer a face.' : 'A imagem será enviada à API Python para identificação e autorização.'}</p></div><button type="button" className="btn primary large" disabled={loading || (!DEMO_MODE && !image)} onClick={doRecognize}><ScanFace size={19}/><LoadText loading={loading}>{DEMO_MODE ? 'Simular verificação' : 'Iniciar reconhecimento'}</LoadText></button></div>
    {error && <div className="inline-error big"><AlertCircle size={18}/>{error}</div>}
    {result && <div className={`result-card ${result.authorized ? 'ok' : 'no'}`}><span className="result-icon">{result.authorized ? <CheckCircle2 size={29}/> : <XCircle size={29}/>}</span><div><strong>{result.simulated ? `Simulação: acesso ${result.authorized ? 'permitido' : 'negado'}` : `Acesso ${result.authorized ? 'autorizado' : 'negado'}`}</strong><p>{result.reason || `Solicitação para o nível ${level}.`}</p>{result.simulated && <small>Nenhuma comparação facial foi executada. Este resultado não comprova identidade.</small>}</div></div>}
  </div>;
}
