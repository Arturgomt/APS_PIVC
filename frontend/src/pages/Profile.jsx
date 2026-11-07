import React from 'react';
import { UserRound, ShieldCheck, Mail, Building2, BriefcaseBusiness } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { PERFIS } from '../data/cadastros';
import { Avatar, PageIntro, SectionHeading } from '../components/UI';
export default function Profile() {
  const { user } = useAuth();
  return <div className="page-fade"><PageIntro title="Meu perfil"/><section className="card profile-card"><div className="profile-hero"><Avatar name={user?.name} size="huge"/><div><h2>{user?.name}</h2><p>{user?.job}</p></div></div><SectionHeading title="Dados" icon={UserRound}/><div className="profile-grid"><div><Mail size={19}/><span>E-mail</span><strong>{user?.email}</strong></div><div><BriefcaseBusiness size={19}/><span>Cargo</span><strong>{user?.job}</strong></div><div><Building2 size={19}/><span>Setor</span><strong>{user?.department}</strong></div><div><ShieldCheck size={19}/><span>Perfil</span><strong>{PERFIS[user?.level]} · nível {user?.level}</strong></div></div></section></div>;
}
