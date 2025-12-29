// frontend/src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Componentes
import Header from './components/layout/Header';
import { AuthProvider } from './context/AuthContext';

// Páginas
import ListaTrabajos from './pages/ListaTrabajos';
import SubirTrabajo from './pages/dashboard/SubirTrabajo';
import Login from './pages/auth/Login';

// Configuración de React Query
const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Router>
          <div className="min-h-screen bg-gray-50 flex flex-col">
            {/* El Header aparece en todas las páginas porque está dentro del Router */}
            <Header /> 
            
            {/* El contenido principal cambia según la ruta */}
            <main className="flex-1 p-4 container mx-auto mt-4">
              <Routes>
                <Route path="/" element={<ListaTrabajos />} />
                <Route path="/trabajos" element={<ListaTrabajos />} />
                <Route path="/login" element={<Login />} />
                <Route path="/dashboard/subir" element={<SubirTrabajo />} />
                {/* Aquí puedes ir agregando más rutas en el futuro */}
              </Routes>
            </main>
            
            {/* Contenedor para las notificaciones flotantes */}
            <ToastContainer position="top-right" autoClose={3000} />
          </div>
        </Router>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;