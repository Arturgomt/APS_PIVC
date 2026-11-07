import React, { useEffect, useState } from 'react';
import { Camera, Fingerprint, ScanFace, AlertCircle, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { userService } from '../services/users';
import { recognitionService } from '../services/recognition';
import { PageIntro, SectionHeading } from '../components/UI';
import CameraPanel from '../components/CameraPanel';
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
  return <div className="page-fade"><PageIntro title="Cadastro facial"/>
    <div className="enrollment-layout"><section className="card"><SectionHeading title="Captura da imagem" icon={Camera}/><CameraPanel onCapture={(blob) => { setImage(blob); setSuccess(''); }}/></section><section className="card enrollment-controls"><SectionHeading title="Usuário" icon={Fingerprint}/><label className="field-label">Usuário<select value={userId} onChange={(e) => setUserId(e.target.value)} className="text-input"><option value="">Selecione</option>{users.map((u) => <option key={u.id} value={u.id}>{u.name}</option>)}</select></label><div className="enrollment-check"><ScanFace size={22}/><div><strong>{image ? 'Imagem selecionada' : 'Sem imagem'}</strong></div></div>{error && <div className="inline-error"><AlertCircle size={16}/>{error}</div>}{success && <div className="inline-success"><CheckCircle2 size={16}/>{success}</div>}<button className="btn primary full" disabled={!image || !userId || busy} onClick={enroll}>{busy ? 'Enviando...' : 'Cadastrar rosto'}</button></section></div>
  </div>;
}
