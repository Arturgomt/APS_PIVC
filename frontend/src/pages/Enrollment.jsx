import React, { useEffect, useState } from 'react';
import { Camera, Fingerprint, ScanFace, AlertCircle, Info, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { userService } from '../services/users';
import { recognitionService } from '../services/recognition';
import CameraPanel from '../components/CameraPanel';
import { PageIntro, SectionHeading } from '../components/UI';
export default function Enrollment() {
  const { token } = useAuth();
  const [users, setUsers] = useState([]);
  const [userId, setUserId] = useState('');
  const [image, setImage] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  useEffect(() => { let mounted = true; userService.list(token).then((list) => { if (mounted) { setUsers(list); setUserId(list[0]?.id || ''); } }).catch((e) => mounted && setError(e.message)); return () => { mounted = false; }; }, [token]);
  async function enroll() {
    setError(''); setSuccess(''); setBusy(true);
    try { const res = await recognitionService.enroll({ image, userId, token }); setSuccess(res.message || 'Referência facial enviada ao servidor.'); }
    catch (err) { setError(err.message); }
    finally { setBusy(false); }
  }
  return <div className="page-fade"><PageIntro eyebrow="ADMINISTRAÇÃO · BIOMETRIA" title="Cadastro facial" description="Selecione um usuário e capture uma imagem para cadastrar sua referência biométrica."/>
    <div className="enrollment-layout"><section className="card"><SectionHeading title="Captura da imagem" icon={Camera}/><CameraPanel onCapture={(blob) => { setImage(blob); setSuccess(''); }}/></section><section className="card enrollment-controls"><SectionHeading title="Dados do cadastro" icon={Fingerprint}/><label className="field-label">Usuário cadastrado<select value={userId} onChange={(e) => setUserId(e.target.value)} className="text-input"><option value="">Selecione um usuário</option>{users.map((u) => <option key={u.id} value={u.id}>{u.name} · Nível {u.level}</option>)}</select></label><div className="enrollment-check"><ScanFace size={22}/><div><strong>{image ? 'Imagem selecionada' : 'Aguardando imagem'}</strong><small>{image ? 'A captura está pronta para envio.' : 'Capture pelo navegador ou selecione um arquivo.'}</small></div></div><div className="info-box"><Info size={18}/><p>Somente a API Python deve armazenar e processar a referência facial. Este Front-end mantém a imagem apenas temporariamente na sessão de captura.</p></div>{error && <div className="inline-error"><AlertCircle size={16}/>{error}</div>}{success && <div className="inline-success"><CheckCircle2 size={16}/>{success}</div>}<button className="btn primary full" disabled={!image || !userId || busy} onClick={enroll}>{busy ? 'Enviando...' : 'Enviar referência facial'}</button></section></div>
  </div>;
}
