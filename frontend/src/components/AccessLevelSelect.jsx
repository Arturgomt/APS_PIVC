import React from 'react';
import { LockKeyhole, ChevronRight, Check } from 'lucide-react';
import { ACCESS_LEVELS } from '../data/demo';
export default function AccessLevelSelect({ value, onChange }) {
  return <div className="level-list">{ACCESS_LEVELS.map((item) => <button type="button" key={item.value} className={`level-card ${Number(value) === item.value ? 'active' : ''}`} aria-pressed={Number(value) === item.value} onClick={() => onChange(item.value)}><span className="level-icon"><LockKeyhole size={20}/></span><span className="level-text"><strong>{item.title}</strong><small>{item.description}</small></span>{Number(value) === item.value ? <Check className="level-arrow" size={19}/> : <ChevronRight className="level-arrow" size={19}/>}</button>)}</div>;
}
