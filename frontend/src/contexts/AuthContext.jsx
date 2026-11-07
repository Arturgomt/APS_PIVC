import React, { createContext, useContext, useState } from 'react';
import { signIn, signOut } from '../services/auth';
import { SESSION_KEY } from '../services/api';

const AuthContext = createContext(null);
function readSession() {
  try { const data = JSON.parse(sessionStorage.getItem(SESSION_KEY) || 'null'); return data?.user ? data : null; }
  catch { return null; }
}
export function AuthProvider({ children }) {
  const [session, setSession] = useState(readSession);
  async function login(credentials) {
    const answer = await signIn(credentials);
    const next = { user: answer.user, token: answer.token || null };
    sessionStorage.setItem(SESSION_KEY, JSON.stringify(next));
    setSession(next);
    return next.user;
  }
  function logout() { signOut(session?.token); sessionStorage.removeItem(SESSION_KEY); setSession(null); }
  return <AuthContext.Provider value={{ user: session?.user, token: session?.token, login, logout }}>
    {children}
  </AuthContext.Provider>;
}
export function useAuth() { return useContext(AuthContext); }
