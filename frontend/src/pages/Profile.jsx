import React from 'react';
import { UserRound, ShieldCheck, Mail, Building2, BriefcaseBusiness, Fingerprint, Info } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { Avatar, PageIntro, SectionHeading } from '../components/UI';
export default function Profile() {
  const { user } = useAuth();
  return <div className="page-fade"><PageIntro eyebrow="MINHA CONTA" title="Meu perfil" description="Seus dados e permissões de acesso cadastrados no sistema."/><section className="card profile-card"><div className="profile-hero"><Avatar name={user?.name} size="huge"/><div><h2>{user?.name}</h2><p>{user?.job}</p><span className="id-tag">{user?.id}</span></div></div><SectionHeading title="Informações do usuário" icon={UserRound}/><div className="profile-grid"><div><Mail size={19}/><span>E-mail</span><strong>{user?.email}</strong></div><div><BriefcaseBusiness size={19}/><span>Cargo</span><strong>{user?.job}</strong></div><div><Building2 size={19}/><span>Departamento</span><strong>{user?.department}</strong></div><div><ShieldCheck size={19}/><span>Permissão do cofre</span><strong>Nível {user?.level}</strong></div></div><div className="info-box"><Info size={17}/><p>Os dados são exibidos conforme a sessão autenticada. Alterações devem ser solicitadas ao administrador.</p></div></section></div>;
}
