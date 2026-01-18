// frontend/src/pages/auth/ProtectedRoute.js
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user, isLoading } = useAuth();

  if (isLoading) return <div>Cargando...</div>;
  
  if (!user) {
    return <Navigate to="/login" />;
  }

  // LLAVE MAESTRA: Si el usuario es superusuario real de Django, entra siempre
  if (user.is_superuser) {
    return children;
  }

  // Si se definieron roles permitidos
  if (allowedRoles) {
    if (allowedRoles.includes(user.rol)) {
      return children;
    } else {
      console.warn(`Acceso denegado: El rol '${user.rol}' no está en la lista permitida.`);
      return <Navigate to="/" />;
    }
  }

  return children;
};