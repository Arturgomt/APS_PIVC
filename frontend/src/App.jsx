import React from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import AppShell from './components/AppShell';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Recognize from './pages/Recognize';
import UsersPage from './pages/UsersPage';
import Enrollment from './pages/Enrollment';
import HistoryPage from './pages/HistoryPage';
import Profile from './pages/Profile';
import SettingsPage from './pages/SettingsPage';

function Protected({ role, children }) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace/>;
  if (role && user.role !== role) return <Navigate to={user.role === 'admin' ? '/admin' : '/usuario'} replace/>;
  return <AppShell>{children}</AppShell>;
}
function HomeRedirect() {
  const { user } = useAuth();
  return <Navigate replace to={!user ? '/login' : user.role === 'admin' ? '/admin' : '/usuario'}/>;
}
export default function App() {
  return <AuthProvider><Routes>
    <Route path="/login" element={<Login/>}/>
    <Route path="/admin" element={<Protected role="admin"><Dashboard admin/></Protected>}/>
    <Route path="/admin/usuarios" element={<Protected role="admin"><UsersPage/></Protected>}/>
    <Route path="/admin/cadastro" element={<Protected role="admin"><Enrollment/></Protected>}/>
    <Route path="/admin/historico" element={<Protected role="admin"><HistoryPage/></Protected>}/>
    <Route path="/admin/configuracoes" element={<Protected role="admin"><SettingsPage/></Protected>}/>
    <Route path="/usuario" element={<Protected role="user"><Dashboard/></Protected>}/>
    <Route path="/usuario/reconhecimento" element={<Protected role="user"><Recognize/></Protected>}/>
    <Route path="/usuario/perfil" element={<Protected role="user"><Profile/></Protected>}/>
    <Route path="*" element={<HomeRedirect/>}/>
  </Routes></AuthProvider>;
}
