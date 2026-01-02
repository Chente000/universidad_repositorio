// frontend/src/pages/auth/ProtectedRoute.js
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user, isLoading } = useAuth();

  console.log("Valores en ProtectedRoute:", { user, isLoading });

  if (isLoading) return <div>Cargando...</div>;
  
  if (!user) {
    console.log("Redirigiendo al login porque user es null");
    return <Navigate to="/login" />;
  }

  // Si se definieron roles permitidos y el rol del usuario no está incluido
  if (allowedRoles && !allowedRoles.includes(user.rol)) {
    return <Navigate to="/" />; // O a una página de "No autorizado"
  }

  return children;
};