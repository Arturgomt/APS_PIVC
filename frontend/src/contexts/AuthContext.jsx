import React, { createContext, useContext, useState } from 'react';
import { signIn } from '../services/auth';

const SESSION_KEY = 'iris-session-v2';
const AuthContext = createContext(null);
function readSession() {
  try { const data = JSON.parse(sessionStorage.getItem(SESSION_KEY) || 'null'); return data?.user ? data : null; }
  catch { return null; }
}
export function AuthProvider({ children }) {
  const [session, setSession] = useState(readSession);
  async function login(email, password) {
    const answer = await signIn(email, password);
    const next = { user: answer.user, token: answer.token || null };
    sessionStorage.setItem(SESSION_KEY, JSON.stringify(next));
    setSession(next);
    return next.user;
  }
  function logout() { sessionStorage.removeItem(SESSION_KEY); setSession(null); }
  return <AuthContext.Provider value={{ user: session?.user, token: session?.token, login, logout }}>
    {children}
  </AuthContext.Provider>;
}
export function useAuth() { return useContext(AuthContext); }
