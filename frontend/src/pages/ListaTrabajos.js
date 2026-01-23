// frontend/src/pages/ListaTrabajos.js
import React, { useEffect, useState, useCallback } from 'react';
import axios from 'axios';
import { Search, BookOpen, User, Calendar, Download, Star, FilterX } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function ListaTrabajos() {
  const [trabajos, setTrabajos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const navigate = useNavigate();

  const [carreras, setCarreras] = useState([]); // <-- Nuevo estado para carreras
  // Estados para filtros
  const [filtroCarrera, setFiltroCarrera] = useState('');
  const [filtroTipo, setFiltroTipo] = useState('');

  // 1. Efecto para cargar las carreras desde el backend
  useEffect(() => {
    const fetchCarreras = async () => {
      try {
        const res = await axios.get('/carreras/'); // Ajusta la URL según tu router de Django
        if (Array.isArray(res.data)) {
        setCarreras(res.data);
      } else if (res.data.results && Array.isArray(res.data.results)) {
        // Por si acaso Django está paginando la respuesta
        setCarreras(res.data.results);
      }
      } catch (err) {
        console.error("Error cargando carreras:", err);
        setCarreras([]); // Mantenemos el array vacío en caso de error
      }
    };
    fetchCarreras();
  }, []);

  // 2. PETICIÓN DE TRABAJOS (Se mantiene casi igual)
  const fetchTrabajos = useCallback(async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (searchTerm) params.append('search', searchTerm);
      
      // Enviamos el ID de la carrera si existe
      if (filtroCarrera) params.append('carrera', filtroCarrera); 
      
      // Enviamos el slug exacto que espera el modelo ('practicas_profesionales')
      if (filtroTipo) params.append('tipo_trabajo', filtroTipo);

      const res = await axios.get(`/trabajos/?${params.toString()}`);
      const data = Array.isArray(res.data) ? res.data : (res.data.results || []);
      setTrabajos(data);
      setError(null);
    } catch (err) {
      setError("No se pudieron cargar los trabajos.");
    } finally {
      setLoading(false);
    }
  }, [searchTerm, filtroCarrera, filtroTipo]);

  useEffect(() => {
    const setTimeoutId = setTimeout(() => {
    fetchTrabajos();
  }, 300); // Añadimos un pequeño retraso para evitar demasiadas llamadas rápidas
    return () => clearTimeout(setTimeoutId);
  }, [fetchTrabajos]);

  const limpiarFiltros = () => {
    setSearchTerm('');
    setFiltroCarrera('');
    setFiltroTipo('');
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
          <p className="text-gray-600">Filtra por carrera o tipo de proyecto para encontrar lo que buscas.</p>
        </div>

        {/* BARRA DE FILTROS */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Buscador de Texto */}
          <div className="relative col-span-1 md:col-span-2">
            <input
              type="text"
              placeholder="Título, autor o tutor..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <Search className="absolute left-3 top-2.5 text-gray-400 w-5 h-5" />
          </div>

          {/* Filtro Carrera */}
          <select 
            className="p-2 border border-gray-300 rounded-lg outline-none focus:ring-2 focus:ring-primary-500"
            value={filtroCarrera}
            onChange={(e) => setFiltroCarrera(e.target.value)}
          >
            <option value="">Todas las Carreras</option>
          {carreras.map((c) => (
            <option key={c.id} value={c.id}> {/* Usamos el ID para el filtro de ForeignKey */}
              {c.nombre}
            </option>
          ))}
        </select>

          {/* Filtro Tipo */}
          <select 
            className="p-2 border border-gray-300 rounded-lg outline-none focus:ring-2 focus:ring-primary-500"
            value={filtroTipo}
            onChange={(e) => setFiltroTipo(e.target.value)}
          >
            <option value="">Todos los Tipos</option>
            <option value="especial_grado">Trabajo Especial de Grado</option>
            <option value="practicas_profesionales">Pasantía / Prácticas</option>
          </select>
        </div>

        {(searchTerm || filtroCarrera || filtroTipo) && (
          <button 
            onClick={limpiarFiltros}
            className="mt-4 text-sm text-red-600 flex items-center hover:underline"
          >
            <FilterX className="w-4 h-4 mr-1" /> Limpiar filtros
          </button>
        )}
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