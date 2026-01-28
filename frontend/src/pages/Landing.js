// frontend/src/pages/Landing.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Landing() {
const navigate = useNavigate();
const [searchTerm, setSearchTerm] = useState('');

const handleSearch = () => {
    if (searchTerm.trim()) {
      // Navegar a la lista de trabajos con el parámetro de búsqueda
    navigate(`/trabajos?q=${encodeURIComponent(searchTerm)}`);
    } else {
      // Si está vacío, solo vamos a trabajos
    navigate('/trabajos');
    }
};

const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
    handleSearch();
    }
};

return (
    <div className="bg-white min-h-screen">
      {/* SECCIÓN HERO */}
    <header className="relative bg-primary-900 text-white py-20 px-6">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center">
        <div className="md:w-1/2 mb-10 md:mb-0">
            <h1 className="text-4xl md:text-6xl font-bold leading-tight mb-6">
            Repositorio Digital de Trabajos de Grado
            </h1>
            <p className="text-xl text-primary-100 mb-8">
            Accede al conocimiento académico de nuestra universidad. Consulta, descarga y gestiona proyectos de grado y pasantías.
            </p>
            <div className="flex gap-4">
            <button 
                onClick={() => navigate('/login')}
                className="bg-white text-primary-900 px-8 py-3 rounded-lg font-bold hover:bg-gray-100 transition-colors"
            >
                Ingresar
            </button>
            <button 
                onClick={() => navigate('/register')}
                className="border-2 border-white text-white px-8 py-3 rounded-lg font-bold hover:bg-white hover:text-primary-900 transition-all"
            >
                Registrarse
            </button>
            </div>
        </div>
          {/* Ilustración o imagen decorativa */}
        <div className="md:w-1/2 flex justify-center text-8xl">
            📚
        </div>
        </div>
    </header>

      {/* SECCIÓN DE BÚSQUEDA RÁPIDA */}
    <section className="py-16 bg-gray-50 px-6">
        <div className="max-w-4xl mx-auto text-center">
        <h2 className="text-3xl font-bold mb-8 text-gray-800">¿Buscas algún proyecto específico?</h2>
        <div className="relative">
            <input 
            type="text" 
            placeholder="Ej: Inteligencia Artificial, Ingeniería Civil..."
            className="w-full p-5 rounded-full shadow-lg border-none focus:ring-2 focus:ring-primary-500 text-lg pl-8 text-gray-800"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyDown={handleKeyPress}
            />
            <button 
            onClick={handleSearch}
            className="absolute right-4 top-1/2 -translate-y-1/2 bg-primary-600 text-white px-6 py-2 rounded-full font-bold hover:bg-primary-700 transition-colors"
            >
            Buscar
            </button>
        </div>
        <p className="mt-4 text-sm text-gray-500">
            Nuestra IA analizará el contenido semántico de tu búsqueda para encontrar los mejores resultados.
        </p>
        </div>
    </section>

      {/* ESTADÍSTICAS O FEATURES */}
    <section className="py-20 px-6 max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-12 text-center">
        <div>
        <div className="text-primary-600 text-4xl mb-4 font-bold">1,200+</div>
        <h3 className="text-xl font-bold mb-2">Proyectos</h3>
        <p className="text-gray-600">Trabajos de grado y pasantías indexados y listos para consulta.</p>
        </div>
        <div>
        <div className="text-primary-600 text-4xl mb-4 font-bold">7+</div>
        <h3 className="text-xl font-bold mb-2">Carreras</h3>
        <p className="text-gray-600">Diversidad académica abarcando todas las áreas de estudio de la universidad.</p>
        </div>
        <div>
        <div className="text-primary-600 text-4xl mb-4 font-bold">24/7</div>
        <h3 className="text-xl font-bold mb-2">Acceso Remoto</h3>
        <p className="text-gray-600">Disponible en cualquier momento y lugar para toda la comunidad.</p>
        </div>
    </section>
    </div>
);
}