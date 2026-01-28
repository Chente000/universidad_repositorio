// frontend/src/pages/ListaTrabajos.js
import React, { useEffect, useState, useCallback } from 'react';
import axios from 'axios';
import { Search, BookOpen, User, Calendar, Download, Star, FilterX, Sparkles } from 'lucide-react'; // Agregué Sparkles
import { useNavigate, useLocation } from 'react-router-dom'; // Agregué useLocation

export default function ListaTrabajos() {
  const [trabajos, setTrabajos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Leemos la URL para ver si vienen parámetros desde el Landing
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const initialQuery = searchParams.get('q') || '';

  const [searchTerm, setSearchTerm] = useState(initialQuery);
  const navigate = useNavigate();

  const [carreras, setCarreras] = useState([]);
  const [filtroCarrera, setFiltroCarrera] = useState('');
  const [filtroTipo, setFiltroTipo] = useState('');
  
  // Estado para saber si los resultados actuales vienen de la IA
  const [esBusquedaIA, setEsBusquedaIA] = useState(false);

  // 1. Cargar Carreras
  useEffect(() => {
    const fetchCarreras = async () => {
      try {
        const res = await axios.get('/carreras/');
        if (Array.isArray(res.data)) {
          setCarreras(res.data);
        } else if (res.data.results) {
          setCarreras(res.data.results);
        }
      } catch (err) {
        console.error("Error cargando carreras:", err);
      }
    };
    fetchCarreras();
  }, []);

  // 2. PETICIÓN DE TRABAJOS (INTELIGENTE VS TRADICIONAL)
  const fetchTrabajos = useCallback(async () => {
    try {
      setLoading(true);
      
      let url = '';
      const params = new URLSearchParams();

      // --- LÓGICA DE DECISIÓN ---
      if (searchTerm.trim().length > 0) {
        // A) Si hay texto, usamos el BUSCADOR INTELIGENTE (IA)
        url = '/trabajos/buscar_inteligente/';
        params.append('q', searchTerm); // La IA espera 'q'
        if (filtroCarrera) params.append('carrera', filtroCarrera);
        // Nota: Si tu backend IA soporta filtroTipo, agrégalo aquí también
        setEsBusquedaIA(true);
      } else {
        // B) Si no hay texto, usamos el LISTADO ESTÁNDAR (Django Filters)
        url = '/trabajos/';
        if (filtroCarrera) params.append('carrera', filtroCarrera);
        if (filtroTipo) params.append('tipo_trabajo', filtroTipo);
        setEsBusquedaIA(false);
      }

      const res = await axios.get(`${url}?${params.toString()}`);
      
      // --- NORMALIZACIÓN DE RESPUESTA ---
      // El endpoint de IA devuelve { resultados: [...] }
      // El endpoint estándar devuelve { results: [...] } o [...]
      let data = [];
      if (res.data.resultados) {
        data = res.data.resultados;
      } else if (res.data.results) {
        data = res.data.results;
      } else if (Array.isArray(res.data)) {
        data = res.data;
      }

      setTrabajos(data);
      setError(null);
    } catch (err) {
      console.error(err);
      setError("No se pudieron cargar los trabajos.");
    } finally {
      setLoading(false);
    }
  }, [searchTerm, filtroCarrera, filtroTipo]);

  // Debounce para la búsqueda
  useEffect(() => {
    const setTimeoutId = setTimeout(() => {
      fetchTrabajos();
    }, 500); // Subí un poco el tiempo para dar chance a escribir
    return () => clearTimeout(setTimeoutId);
  }, [fetchTrabajos]);

  const limpiarFiltros = () => {
    setSearchTerm('');
    setFiltroCarrera('');
    setFiltroTipo('');
    // Limpiamos la URL visualmente también
    navigate('/trabajos', { replace: true });
  };

  return (
    <div className="space-y-8 p-6 max-w-7xl mx-auto"> {/* Añadí un container básico */}
      
      {/* Encabezado y Buscador */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-primary-900">Explorar Investigaciones</h1>
          <p className="text-gray-600">
            {esBusquedaIA 
              ? <span className="flex items-center text-indigo-600 font-medium"><Sparkles className="w-4 h-4 mr-1"/> Búsqueda semántica activada</span>
              : "Filtra por carrera o tipo de proyecto."}
          </p>
        </div>

        {/* BARRA DE FILTROS */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Buscador de Texto */}
          <div className="relative col-span-1 md:col-span-2">
            <input
              type="text"
              placeholder="Busca por concepto, ej: 'Redes neuronales'..."
              className={`w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 outline-none transition-all ${
                esBusquedaIA ? 'border-indigo-300 focus:ring-indigo-500 bg-indigo-50' : 'border-gray-300 focus:ring-primary-500'
              }`}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            {esBusquedaIA ? (
               <Sparkles className="absolute left-3 top-2.5 text-indigo-500 w-5 h-5 animate-pulse" />
            ) : (
               <Search className="absolute left-3 top-2.5 text-gray-400 w-5 h-5" />
            )}
          </div>

          {/* Filtro Carrera */}
          <select 
            className="p-2 border border-gray-300 rounded-lg outline-none focus:ring-2 focus:ring-primary-500"
            value={filtroCarrera}
            onChange={(e) => setFiltroCarrera(e.target.value)}
          >
            <option value="">Todas las Carreras</option>
            {carreras.map((c) => (
              <option key={c.id} value={c.id}>{c.nombre}</option>
            ))}
          </select>

          {/* Filtro Tipo (Deshabilitado visualmente si es búsqueda IA estricta, opcional) */}
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
        <div className="flex flex-col justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-800"></div>
          {esBusquedaIA && <p className="mt-4 text-indigo-600 animate-pulse">La IA está analizando los documentos...</p>}
        </div>
      ) : error ? (
        <div className="bg-red-50 text-red-700 p-4 rounded-lg border border-red-200">
          {error}
        </div>
      ) : (
        <>
          {/* Grid de Tarjetas */}
          {trabajos.length === 0 ? (
            <div className="text-center py-20 bg-white rounded-xl shadow-sm border border-gray-100">
              <BookOpen className="mx-auto w-16 h-16 text-gray-300 mb-4" />
              <p className="text-gray-500 text-xl">No se encontraron trabajos.</p>
              {esBusquedaIA && <p className="text-sm text-gray-400 mt-2">Intenta ser más específico con tu concepto.</p>}
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
                        {trabajo.tipo_trabajo_display || (trabajo.tipo_trabajo === 'especial_grado' ? 'TEG' : 'Pasantía')}
                      </span>
                      <div className="flex items-center text-yellow-500">
                        <Star className="w-4 h-4 fill-current" />
                        <span className="ml-1 text-sm font-semibold text-gray-700">
                          {trabajo.calificacion_promedio?.promedio || '0.0'}
                        </span>
                      </div>
                    </div>

                    <h3 className="text-lg font-bold text-gray-900 mb-2 line-clamp-2 min-h-[3.5rem]">
                      {trabajo.titulo}
                    </h3>

                    <div className="space-y-2 text-sm text-gray-600">
                      <div className="flex items-center">
                        <User className="w-4 h-4 mr-2 text-primary-600 flex-shrink-0" />
                        <span className="truncate">{trabajo.autores}</span>
                      </div>
                      <div className="flex items-center">
                        <BookOpen className="w-4 h-4 mr-2 text-primary-600 flex-shrink-0" />
                        <span className="truncate">{trabajo.carrera_nombre || trabajo.carrera}</span>
                      </div>
                      <div className="flex items-center">
                        <Calendar className="w-4 h-4 mr-2 text-primary-600 flex-shrink-0" />
                        <span>Año: {trabajo.año}</span>
                      </div>
                    </div>
                  </div>

                  {/* Pie de la tarjeta */}
                  <div className="bg-gray-50 p-4 border-t border-gray-100 flex justify-between items-center">
                    <div className="flex items-center text-gray-500 text-xs">
                      <Download className="w-4 h-4 mr-1" />
                      {trabajo.total_descargas || 0} descargas
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