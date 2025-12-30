// frontend/src/pages/DetalleTrabajo.js
import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { FileText, Download, Calendar, User, GraduationCap, ArrowLeft, Star, Tag } from 'lucide-react';

export default function DetalleTrabajo() {
const { id } = useParams();
const navigate = useNavigate();
const [trabajo, setTrabajo] = useState(null);
const [loading, setLoading] = useState(true);
const handleDescargar = async () => {
    try {
    const response = await axios.get(`/trabajos/${id}/descargar/`, {
        responseType: 'blob', // Importante para manejar archivos
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}` // Asegúrate de enviar el token
        }
    });

    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    
    link.setAttribute('download', `trabajo_investigacion_${id}.pdf`); 
    
    document.body.appendChild(link);
    link.click();
    
    link.parentNode.removeChild(link);
    window.URL.revokeObjectURL(url);
    } catch (err) {
    console.error("Error al descargar el archivo:", err);
    alert("No se pudo descargar el archivo. Asegúrate de tener permisos.");
    }
};


useEffect(() => {
    const fetchDetalle = async () => {
    try {
        const res = await axios.get(`/trabajos/${id}/`);
        setTrabajo(res.data);
    } catch (err) {
        console.error("Error al obtener detalle:", err);
    } finally {
        setLoading(false);
    }
    };
    fetchDetalle();
}, [id]);

if (loading) return <div className="p-10 text-center">Cargando investigación...</div>;
if (!trabajo) return <div className="p-10 text-center">Trabajo no encontrado.</div>;

return (
    <div className="max-w-5xl mx-auto pb-10">
      {/* Botón Volver */}
    <button 
        onClick={() => navigate(-1)}
        className="flex items-center text-primary-600 hover:text-primary-800 mb-6 transition-colors"
    >
        <ArrowLeft className="w-4 h-4 mr-2" /> Volver al listado
    </button>

    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Columna Izquierda: Información Principal */}
        <div className="lg:col-span-2 space-y-6">
        <header className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100">
            <div className="flex items-center space-x-2 mb-4">
            <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-bold uppercase">
                {trabajo.tipo_trabajo_display}
            </span>
            <span className="text-gray-400">•</span>
            <span className="text-sm text-gray-500">{trabajo.carrera_display}</span>
            </div>
            
            <h1 className="text-3xl font-extrabold text-gray-900 mb-4">{trabajo.titulo}</h1>
            
            <div className="flex flex-wrap gap-4 text-gray-600">
            <div className="flex items-center"><User className="w-4 h-4 mr-2" /> {trabajo.autores}</div>
            <div className="flex items-center"><Calendar className="w-4 h-4 mr-2" /> {trabajo.año}</div>
            <div className="flex items-center text-yellow-600">
                <Star className="w-4 h-4 mr-2 fill-current" /> 
                {trabajo.calificacion_promedio?.promedio || '0.0'} ({trabajo.calificacion_promedio?.total_comentarios} reseñas)
            </div>
            </div>
        </header>

        <section className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100">
            <h2 className="text-xl font-bold mb-4 flex items-center">
            <FileText className="w-5 h-5 mr-2 text-primary-600" /> Resumen
            </h2>
            <p className="text-gray-700 leading-relaxed whitespace-pre-line">{trabajo.resumen}</p>
            
            <h2 className="text-xl font-bold mt-8 mb-4">Objetivos</h2>
            <p className="text-gray-700 leading-relaxed whitespace-pre-line">{trabajo.objetivos}</p>
        </section>

          {/* Tags de IA */}
        {typeof trabajo.tags_ia === 'string' && trabajo.tags_ia.length > 0 && (
            <section className="bg-primary-50 p-6 rounded-2xl border border-primary-100">
            <h2 className="text-sm font-bold text-primary-800 uppercase tracking-wider mb-3 flex items-center">
                <Tag className="w-4 h-4 mr-2" /> Conceptos Clave (IA)
            </h2>
            <div className="flex flex-wrap gap-2">
                {trabajo.tags_ia.split(',').map((tag, i) => (
                <span key={i} className="bg-white px-3 py-1 rounded-lg text-sm text-primary-700 border border-primary-200 shadow-sm">
                    {tag.trim()}
                </span>
                ))}
            </div>
            </section>
        )}
        </div>

        {/* Columna Derecha: Sidebar de Acciones */}
        <div className="space-y-6">
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 sticky top-4">
            <h3 className="font-bold text-gray-900 mb-4">Acciones</h3>
            
            <button
            onClick={handleDescargar} // <--- Conexión aquí
            disabled={!trabajo.puede_descargar}
            className={`w-full flex items-center justify-center py-3 rounded-xl font-bold transition-all shadow-lg ${
                trabajo.puede_descargar 
                ? 'bg-primary-600 text-white hover:bg-primary-700' 
                : 'bg-gray-200 text-gray-500 cursor-not-allowed'
            }`}
            >
            <Download className="w-5 h-5 mr-2" /> Descargar PDF
            </button>
            
            {!trabajo.puede_descargar && (
            <p className="text-xs text-red-500 mt-2 text-center">Debes iniciar sesión para descargar este archivo.</p>
            )}

            <hr className="my-6 border-gray-100" />

            <div className="space-y-4">
            <div>
                <span className="block text-xs text-gray-400 uppercase font-bold">Tutor(es)</span>
                <span className="text-gray-700 font-medium">{trabajo.tutores || 'No especificado'}</span>
            </div>
            <div>
                <span className="block text-xs text-gray-400 uppercase font-bold">Fecha de Subida</span>
                <span className="text-gray-700 font-medium">{new Date(trabajo.fecha_subida).toLocaleDateString()}</span>
            </div>
            <div>
                <span className="block text-xs text-gray-400 uppercase font-bold">Descargas Totales</span>
                <span className="text-gray-700 font-medium">{trabajo.total_descargas} veces</span>
            </div>
            </div>
        </div>
        </div>
    </div>
    </div>
);
}