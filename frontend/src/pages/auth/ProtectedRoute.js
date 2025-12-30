// frontend/src/pages/auth/ProtectedRoute.js
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user, loading } = useAuth();

  if (loading) return <div>Cargando...</div>;
  
  if (!user) return <Navigate to="/login" />;

  // Si se definieron roles permitidos y el rol del usuario no está incluido
  if (allowedRoles && !allowedRoles.includes(user.rol)) {
    return <Navigate to="/" />; // O a una página de "No autorizado"
  }

  return children;
};