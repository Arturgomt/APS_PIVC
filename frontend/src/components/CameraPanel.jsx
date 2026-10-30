import React, { useEffect, useRef, useState } from 'react';
import { Camera, CameraOff, ScanFace, RotateCcw, ImagePlus, AlertCircle } from 'lucide-react';

export default function CameraPanel({ onCapture, small = false }) {
  const video = useRef(null);
  const stream = useRef(null);
  const inputRef = useRef(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState('');
  const [preview, setPreview] = useState(null);
  const previewRef = useRef(null);

  function stop() {
    stream.current?.getTracks().forEach((track) => track.stop());
    stream.current = null;
    if (video.current) video.current.srcObject = null;
    setRunning(false);
  }
  useEffect(() => () => {
    stream.current?.getTracks().forEach((track) => track.stop());
    if (previewRef.current) URL.revokeObjectURL(previewRef.current);
  }, []);
  async function start() {
    setError('');
    if (!navigator.mediaDevices?.getUserMedia) { setError('Webcam indisponível. Use localhost ou HTTPS.'); return; }
    try {
      stop();
      const feed = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user', width: { ideal: 1280 }, height: { ideal: 720 } }, audio: false });
      stream.current = feed;
      if (video.current) { video.current.srcObject = feed; await video.current.play(); }
      setRunning(true);
    } catch (e) { setError(e.name === 'NotAllowedError' ? 'Permita o uso da câmera no navegador.' : 'Não foi possível ativar a câmera.'); }
  }
  function setPhoto(blob) {
    if (previewRef.current) URL.revokeObjectURL(previewRef.current);
    const url = URL.createObjectURL(blob);
    previewRef.current = url;
    setPreview(url);
    onCapture?.(blob);
  }
  function capture() {
    const el = video.current;
    if (!running || !el?.videoWidth) { setError('Ative a câmera antes de capturar.'); return; }
    const canvas = document.createElement('canvas');
    canvas.width = Math.min(el.videoWidth, 1280);
    canvas.height = Math.round(canvas.width * el.videoHeight / el.videoWidth);
    canvas.getContext('2d').drawImage(el, 0, 0, canvas.width, canvas.height);
    canvas.toBlob((blob) => blob && setPhoto(blob), 'image/jpeg', 0.86);
  }
  function fromFile(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type) || file.size > 5_000_000) {
      setError('Envie uma imagem JPG, PNG ou WEBP de até 5 MB.');
      event.target.value = '';
      return;
    }
    setError(''); setPhoto(file);
  }
  function clear() {
    if (previewRef.current) URL.revokeObjectURL(previewRef.current);
    previewRef.current = null; setPreview(null); onCapture?.(null);
  }
  return <div className={`camera-component ${small ? 'compact' : ''}`}>
    <div className="camera-stage">
      <video ref={video} playsInline muted autoPlay className={running ? 'active' : ''}/>
      {!running && <div className="camera-placeholder"><span className="camera-graphic"><ScanFace size={76} strokeWidth={1.1}/></span><strong>Câmera pronta para conexão</strong><p>Ative a webcam ou selecione uma imagem para teste.</p></div>}
      <div className={`camera-live-badge ${running ? 'on' : ''}`}><span/> {running ? 'Câmera ativa' : 'Câmera desligada'}</div>
      {running && <span className="camera-corner-label"><ScanFace size={16}/> Captura local</span>}
      {preview && <div className="captured-preview"><img alt="Prévia da captura facial" src={preview}/><button className="icon-btn" onClick={clear} aria-label="Descartar imagem"><RotateCcw size={17}/></button><span>Imagem capturada</span></div>}
    </div>
    {error && <div className="inline-error"><AlertCircle size={16}/>{error}</div>}
    <div className="camera-actions">
      <button className="btn primary" type="button" onClick={running ? capture : start}><Camera size={17}/>{running ? 'Capturar imagem' : 'Ativar câmera'}</button>
      <button className="btn secondary" type="button" onClick={() => inputRef.current?.click()}><ImagePlus size={17}/> Enviar foto</button>
      {running && <button className="btn subtle icon-only" type="button" onClick={stop} title="Desligar câmera"><CameraOff size={19}/></button>}
      <input ref={inputRef} className="sr-only" type="file" accept="image/png,image/jpeg,image/webp" onChange={fromFile}/>
    </div>
  </div>;
}
