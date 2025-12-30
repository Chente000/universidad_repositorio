import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Search, BookOpen, User, Calendar, Download, Star } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function ListaTrabajos() {
  const [trabajos, setTrabajos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchTrabajos();
  }, []);

  const fetchTrabajos = async (query = '') => {
    try {
      setLoading(true);
      // Usamos el parámetro 'search' que ya configuraste en Django
      const res = await axios.get(`/trabajos/${query ? `?search=${query}` : ''}`);
      const data = Array.isArray(res.data) ? res.data : (res.data.results || []);
      setTrabajos(data);
      setError(null);
    } catch (err) {
      console.error("Error cargando trabajos:", err);
      setError("No se pudieron cargar los trabajos. Intenta de nuevo más tarde.");
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    fetchTrabajos(searchTerm);
  };

  return (
    <div className="space-y-8">
      {/* Encabezado y Buscador */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-primary-900">Explorar Investigaciones</h1>
          <p className="text-gray-600">Encuentra trabajos especiales de grado y pasantías.</p>
        </div>

        <form onSubmit={handleSearch} className="relative w-full md:w-96">
          <input
            type="text"
            placeholder="Buscar por título, autor o tutor..."
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none transition-all"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <Search className="absolute left-3 top-2.5 text-gray-400 w-5 h-5" />
        </form>
      </div>

      {/* Estado de Carga */}
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-800"></div>
        </div>
      ) : error ? (
        <div className="bg-red-50 text-red-700 p-4 rounded-lg border border-red-200">
          {error}
        </div>
      ) : (
        <>
          {/* Grid de Tarjetas */}
          {trabajos.length === 0 ? (
            <div className="text-center py-20 bg-white rounded-xl shadow-sm">
              <BookOpen className="mx-auto w-16 h-16 text-gray-300 mb-4" />
              <p className="text-gray-500 text-xl">No se encontraron trabajos que coincidan.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {trabajos.map((trabajo) => (
                <div 
                  key={trabajo.id} 
                  className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow border border-gray-100 overflow-hidden flex flex-col"
                >
                  {/* Badge de Tipo de Trabajo */}
                  <div className="p-4 flex-1">
                    <div className="flex justify-between items-start mb-3">
                      <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${
                        trabajo.tipo_trabajo === 'especial_grado' 
                        ? 'bg-blue-100 text-blue-700' 
                        : 'bg-green-100 text-green-700'
                      }`}>
                        {trabajo.tipo_trabajo_display}
                      </span>
                      <div className="flex items-center text-yellow-500">
                        <Star className="w-4 h-4 fill-current" />
                        <span className="ml-1 text-sm font-semibold text-gray-700">
                          {trabajo.calificacion_promedio?.promedio || '0.0'}
                        </span>
                      </div>
                    </div>

                    <h3 className="text-lg font-bold text-gray-900 mb-2 line-clamp-2 h-14">
                      {trabajo.titulo}
                    </h3>

                    <div className="space-y-2 text-sm text-gray-600">
                      <div className="flex items-center">
                        <User className="w-4 h-4 mr-2 text-primary-600" />
                        <span className="truncate">{trabajo.autores}</span>
                      </div>
                      <div className="flex items-center">
                        <BookOpen className="w-4 h-4 mr-2 text-primary-600" />
                        <span>{trabajo.carrera_display}</span>
                      </div>
                      <div className="flex items-center">
                        <Calendar className="w-4 h-4 mr-2 text-primary-600" />
                        <span>Año: {trabajo.año}</span>
                      </div>
                    </div>
                  </div>

                  {/* Pie de la tarjeta */}
                  <div className="bg-gray-50 p-4 border-t border-gray-100 flex justify-between items-center">
                    <div className="flex items-center text-gray-500 text-xs">
                      <Download className="w-4 h-4 mr-1" />
                      {trabajo.total_descargas} descargas
                    </div>
                    <button 
                      className="text-primary-800 font-bold text-sm hover:text-primary-600 transition-colors"
                      onClick={() => navigate(`/trabajos/${trabajo.id}`)}
                    >
                      Ver detalles →
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}