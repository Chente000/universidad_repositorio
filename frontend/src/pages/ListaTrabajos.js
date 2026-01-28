// frontend/src/pages/ListaTrabajos.js
import React, { useEffect, useState, useCallback } from 'react';
import axios from 'axios';
import { Search, BookOpen, User, Calendar, Download, Star, FilterX, Sparkles, ChevronLeft, ChevronRight } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function ListaTrabajos() {
  const [trabajos, setTrabajos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const initialQuery = searchParams.get('q') || '';

  const [searchTerm, setSearchTerm] = useState(initialQuery);
  const navigate = useNavigate();

  const [carreras, setCarreras] = useState([]);
  const [filtroCarrera, setFiltroCarrera] = useState('');
  const [filtroTipo, setFiltroTipo] = useState('');

  // Paginación
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(12);
  const [totalCount, setTotalCount] = useState(0);

  // Ver pendientes (para encargados / administradores)
  const [verPendientes, setVerPendientes] = useState(false);

  const { user, hasAnyRole } = useAuth();
  const [esBusquedaIA, setEsBusquedaIA] = useState(false);

  // Cargar carreras
  useEffect(() => {
    const fetchCarreras = async () => {
      try {
        const res = await axios.get('/carreras/');
        if (Array.isArray(res.data)) setCarreras(res.data);
        else if (res.data.results) setCarreras(res.data.results);
      } catch (err) {
        console.error('Error cargando carreras:', err);
      }
    };
    fetchCarreras();
  }, []);

  // Fetch trabajos — maneja IA, list estándar y pendientes
  const fetchTrabajos = useCallback(async () => {
    try {
      setLoading(true);

      let url = '';
      const params = new URLSearchParams();

      if (verPendientes) {
        url = '/trabajos/pendientes/';
        if (filtroCarrera) params.append('carrera', filtroCarrera);
        setEsBusquedaIA(false);
      } else if (searchTerm.trim().length > 0) {
        url = '/trabajos/buscar_inteligente/';
        params.append('q', searchTerm);
        if (filtroCarrera) params.append('carrera', filtroCarrera);
        setEsBusquedaIA(true);
      } else {
        url = '/trabajos/';
        params.append('page', String(page));
        params.append('page_size', String(pageSize));
        if (filtroCarrera) params.append('carrera', filtroCarrera);
        if (filtroTipo) params.append('tipo_trabajo', filtroTipo);
        setEsBusquedaIA(false);
      }

      const res = await axios.get(`${url}?${params.toString()}`);

      let data = [];
      if (verPendientes) {
        data = Array.isArray(res.data) ? res.data : (res.data.results || []);
        setTrabajos(data);
        setTotalCount(data.length || 0);
      } else if (res.data.resultados) {
        data = res.data.resultados;
        setTrabajos(data);
        setTotalCount(res.data.total || data.length);
      } else if (res.data.results) {
        data = res.data.results;
        setTrabajos(data);
        setTotalCount(res.data.count || data.length);
      } else if (Array.isArray(res.data)) {
        data = res.data;
        setTrabajos(data);
        setTotalCount(data.length);
      }

      setError(null);
    } catch (err) {
      console.error(err);
      setError('No se pudieron cargar los trabajos.');
    } finally {
      setLoading(false);
    }
  }, [searchTerm, filtroCarrera, filtroTipo, verPendientes, page, pageSize]);

  // Debounce + efectos cuando cambian page/pageSize/verPendientes
  useEffect(() => {
    const t = setTimeout(() => fetchTrabajos(), 250);
    return () => clearTimeout(t);
  }, [fetchTrabajos, page, pageSize, verPendientes]);

  const limpiarFiltros = () => {
    setSearchTerm('');
    setFiltroCarrera('');
    setFiltroTipo('');
    navigate('/trabajos', { replace: true });
    setPage(1);
    setVerPendientes(false);
  };

  return (
    <div className="space-y-8 p-6 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-primary-900">Explorar Investigaciones</h1>
          <p className="text-gray-600">
            {esBusquedaIA ? (
              <span className="flex items-center text-indigo-600 font-medium"><Sparkles className="w-4 h-4 mr-1"/> Búsqueda semántica activada</span>
            ) : (
              'Filtra por carrera o tipo de proyecto.'
            )}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 w-full md:w-auto">
          <div className="relative col-span-1 md:col-span-2">
            <input
              type="text"
              placeholder="Busca por concepto, ej: 'Redes neuronales'..."
              className={`w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 outline-none transition-all ${
                esBusquedaIA ? 'border-indigo-300 focus:ring-indigo-500 bg-indigo-50' : 'border-gray-300 focus:ring-primary-500'
              }`}
              value={searchTerm}
              onChange={(e) => { setSearchTerm(e.target.value); setPage(1); }}
            />
            {esBusquedaIA ? (
              <Sparkles className="absolute left-3 top-2.5 text-indigo-500 w-5 h-5 animate-pulse" />
            ) : (
              <Search className="absolute left-3 top-2.5 text-gray-400 w-5 h-5" />
            )}
          </div>

          <select className="p-2 border border-gray-300 rounded-lg outline-none focus:ring-2 focus:ring-primary-500" value={filtroCarrera} onChange={(e) => { setFiltroCarrera(e.target.value); setPage(1); }}>
            <option value="">Todas las Carreras</option>
            {carreras.map((c) => (<option key={c.id} value={c.id}>{c.nombre}</option>))}
          </select>

          <select className="p-2 border border-gray-300 rounded-lg outline-none focus:ring-2 focus:ring-primary-500" value={filtroTipo} onChange={(e) => { setFiltroTipo(e.target.value); setPage(1); }}>
            <option value="">Todos los Tipos</option>
            <option value="especial_grado">Trabajo Especial de Grado</option>
            <option value="practicas_profesionales">Pasantía / Prácticas</option>
          </select>
        </div>

        <div className="flex items-center gap-4">
          {(searchTerm || filtroCarrera || filtroTipo) && (
            <button onClick={limpiarFiltros} className="text-sm text-red-600 flex items-center hover:underline">
              <FilterX className="w-4 h-4 mr-1"/> Limpiar filtros
            </button>
          )}

          {(user && (user.is_superuser || hasAnyRole(['encargado_pasantias','encargado_especial_grado','administrador']))) && (
            <label className="inline-flex items-center cursor-pointer text-sm">
              <input type="checkbox" className="form-checkbox h-4 w-4" checked={verPendientes} onChange={(e) => { setVerPendientes(e.target.checked); setPage(1); }} />
              <span className="ml-2">Ver pendientes</span>
            </label>
          )}
        </div>
      </div>

      {loading ? (
        <div className="flex flex-col justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-800"></div>
          {esBusquedaIA && <p className="mt-4 text-indigo-600 animate-pulse">La IA está analizando los documentos...</p>}
        </div>
      ) : error ? (
        <div className="bg-red-50 text-red-700 p-4 rounded-lg border border-red-200">{error}</div>
      ) : (
        <>
          {trabajos.length === 0 ? (
            <div className="text-center py-20 bg-white rounded-xl shadow-sm border border-gray-100">
              <BookOpen className="mx-auto w-16 h-16 text-gray-300 mb-4" />
              <p className="text-gray-500 text-xl">No se encontraron trabajos.</p>
              {esBusquedaIA && <p className="text-sm text-gray-400 mt-2">Intenta ser más específico con tu concepto.</p>}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {trabajos.map((trabajo) => (
                <div key={trabajo.id} className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow border border-gray-100 overflow-hidden flex flex-col">
                  <div className="p-4 flex-1">
                    <div className="flex justify-between items-start mb-3">
                      <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${trabajo.tipo_trabajo === 'especial_grado' ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'}`}>
                        {trabajo.tipo_trabajo_display || (trabajo.tipo_trabajo === 'especial_grado' ? 'TEG' : 'Pasantía')}
                      </span>
                      <div className="flex items-center text-yellow-500">
                        <Star className="w-4 h-4 fill-current" />
                        <span className="ml-1 text-sm font-semibold text-gray-700">{trabajo.calificacion_promedio?.promedio || '0.0'}</span>
                      </div>
                    </div>

                    <h3 className="text-lg font-bold text-gray-900 mb-2 line-clamp-2 min-h-[3.5rem]">{trabajo.titulo}</h3>

                    <div className="space-y-2 text-sm text-gray-600">
                      <div className="flex items-center"><User className="w-4 h-4 mr-2 text-primary-600 flex-shrink-0" /><span className="truncate">{trabajo.autores}</span></div>
                      <div className="flex items-center"><BookOpen className="w-4 h-4 mr-2 text-primary-600 flex-shrink-0" /><span className="truncate">{trabajo.carrera_nombre || trabajo.carrera}</span></div>
                      <div className="flex items-center"><Calendar className="w-4 h-4 mr-2 text-primary-600 flex-shrink-0" /><span>Año: {trabajo.año}</span></div>
                    </div>
                  </div>

                  <div className="bg-gray-50 p-4 border-t border-gray-100 flex justify-between items-center">
                    <div className="flex items-center text-gray-500 text-xs"><Download className="w-4 h-4 mr-1" />{trabajo.total_descargas || 0} descargas</div>
                    <button className="text-primary-800 font-bold text-sm hover:text-primary-600 transition-colors" onClick={() => navigate(`/trabajos/${trabajo.id}`)}>Ver detalles →</button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Paginador simple (solo cuando no es búsqueda IA y no estamos viendo pendientes) */}
          {!esBusquedaIA && !verPendientes && totalCount > pageSize && (
            <div className="mt-6 flex items-center justify-between">
              <div className="text-sm text-gray-600">Página {page} de {Math.max(1, Math.ceil(totalCount / pageSize))} — {totalCount} resultados</div>
              <div className="flex items-center gap-2">
                <button disabled={page <= 1} onClick={() => setPage(p => Math.max(1, p - 1))} className="p-2 bg-white border rounded disabled:opacity-50"><ChevronLeft className="w-4 h-4" /></button>
                <select value={pageSize} onChange={(e) => { setPageSize(Number(e.target.value)); setPage(1); }} className="p-2 border rounded">
                  <option value={6}>6 / pág</option>
                  <option value={12}>12 / pág</option>
                  <option value={24}>24 / pág</option>
                </select>
                <button disabled={page >= Math.ceil(totalCount / pageSize)} onClick={() => setPage(p => p + 1)} className="p-2 bg-white border rounded disabled:opacity-50"><ChevronRight className="w-4 h-4" /></button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}