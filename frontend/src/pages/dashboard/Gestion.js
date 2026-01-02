// frontend/src/pages/dashboard/Gestion.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';

export default function Gestion() {
const [trabajos, setTrabajos] = useState([]);
const [loading, setLoading] = useState(true);

  // 1. Cargar trabajos desde el backend
const fetchTrabajos = async () => {
    try {
    const token = localStorage.getItem('token');
      // Asegúrate de que esta URL coincida con tu backend
    const res = await axios.get('/trabajos/pendientes/', {
        headers: { Authorization: `Bearer ${token}` }
    });
    setTrabajos(res.data);
    } catch (err) {
    console.error("Error al cargar trabajos", err);
    } finally {
    setLoading(false);
    }
};

useEffect(() => { fetchTrabajos(); }, []);

  // 2. Función para Aprobar/Rechazar
const handleAccion = async (id, accion) => {
    try {
    const token = localStorage.getItem('token');
    await axios.post(`/trabajos/${id}/${accion}/`, {}, {
        headers: { Authorization: `Bearer ${token}` }
    });
    alert(`Trabajo ${accion === 'aprobar' ? 'Aprobado' : 'Rechazado'}`);
      fetchTrabajos(); // Recargar la lista
    } catch (err) {
    alert("Error al procesar la acción");
    }
};

if (loading) return <p>Cargando gestión...</p>;

return (
    <div className="p-6">
    <h2 className="text-2xl font-bold mb-4">Gestión de Trabajos</h2>
    <div className="bg-white shadow rounded-lg overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
            <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Título</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Autor</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Acciones</th>
            </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
            {trabajos.length === 0 ? (
            <tr><td colSpan="3" className="p-4 text-center">No hay trabajos pendientes</td></tr>
            ) : (
            trabajos.map((t) => (
                <tr key={t.id}>
                <td className="px-6 py-4 text-sm text-gray-900">{t.titulo}</td>
                <td className="px-6 py-4 text-sm text-gray-500">{t.autor_nombre}</td>
                <td className="px-6 py-4 text-sm font-medium space-x-3">
                    <button onClick={() => handleAccion(t.id, 'aprobar')} className="text-green-600 hover:underline">Aprobar</button>
                    <button onClick={() => handleAccion(t.id, 'rechazar')} className="text-red-600 hover:underline">Rechazar</button>
                </td>
                </tr>
            ))
            )}
        </tbody>
        </table>
    </div>
    </div>
);
}