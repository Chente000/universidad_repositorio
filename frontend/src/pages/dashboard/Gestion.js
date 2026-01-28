// frontend/src/pages/dashboard/Gestion.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useAuth } from '../../context/AuthContext';

export default function Gestion() {
    const { user } = useAuth();
    const [trabajos, setTrabajos] = useState([]);
    const [loading, setLoading] = useState(true);

    // ESTADOS PARA EL MODAL DE RECHAZO
    const [showModal, setShowModal] = useState(false);
    const [motivo, setMotivo] = useState('');
    const [selectedTrabajoId, setSelectedTrabajoId] = useState(null);

    const fetchTrabajos = async () => {
        try {
            const token = localStorage.getItem('token');
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

    // ACCIÓN DE APROBAR
    const handleAprobar = async (id) => {
        if (!window.confirm("¿Estás seguro de aprobar este trabajo?")) return;
        try {
            const token = localStorage.getItem('token');
            await axios.post(`/trabajos/${id}/aprobar/`, {}, {
                headers: { Authorization: `Bearer ${token}` }
            });
            alert("Trabajo Aprobado");
            fetchTrabajos();
        } catch (err) {
            alert("Error al aprobar");
        }
    };

    // ACCIONES DE RECHAZO (MODAL)
    const abrirModalRechazo = (id) => {
        setSelectedTrabajoId(id);
        setShowModal(true);
    };

    const handleConfirmarRechazo = async () => {
        try {
            const token = localStorage.getItem('token');
            await axios.post(`/trabajos/${selectedTrabajoId}/rechazar/`, 
                { motivo: motivo }, 
                { headers: { Authorization: `Bearer ${token}` } }
            );
            alert("Trabajo Rechazado");
            setShowModal(false);
            setMotivo('');
            fetchTrabajos();
        } catch (err) {
            alert("Error al rechazar");
        }
    };

    if (loading) return <div className="p-10 text-center">Cargando gestión...</div>;

    return (
        <div className="p-6">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Gestión de Trabajos Pendientes</h2>
            
            <div className="bg-white shadow-md rounded-lg overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Título</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Autor</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Documento</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Acciones</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {trabajos.length === 0 ? (
                            <tr><td colSpan="4" className="p-6 text-center text-gray-500">No hay trabajos por revisar</td></tr>
                        ) : (
                            trabajos.map((t) => (
                                <tr key={t.id} className="hover:bg-gray-50">
                                    <td className="px-6 py-4 text-sm text-gray-900 font-medium">{t.titulo}</td>
                                    <td className="px-6 py-4 text-sm text-gray-500">{t.autores}</td>
                                    <td className="px-6 py-4 text-sm">
                                        <a href={t.archivo_pdf} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline flex items-center">
                                            Ver PDF
                                        </a>
                                    </td>
                                    <td className="px-6 py-4 text-sm font-medium space-x-2">
                                        {(user.rol === 'administrador' || user.rol.startsWith('superuser_')) ? (
                                            <>
                                                <button onClick={() => handleAprobar(t.id)} className="bg-green-100 text-green-700 px-3 py-1 rounded-md hover:bg-green-200">
                                                    Aprobar
                                                </button>
                                                <button onClick={() => abrirModalRechazo(t.id)} className="bg-red-100 text-red-700 px-3 py-1 rounded-md hover:bg-red-200">
                                                    Rechazar
                                                </button>
                                            </>
                                        ) : (
                                            <span className="text-gray-400 italic text-xs">Solo lectura</span>
                                        )}
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>

            {/* MODAL DE RECHAZO */}
            {showModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white rounded-xl p-6 max-w-md w-full shadow-2xl">
                        <h3 className="text-xl font-bold mb-2 text-gray-800">Rechazar Trabajo</h3>
                        <p className="text-sm text-gray-600 mb-4">Por favor, indica el motivo del rechazo para informar al autor.</p>
                        <textarea
                            className="w-full border-2 border-gray-200 p-3 rounded-lg h-32 mb-4 focus:border-blue-500 focus:outline-none"
                            placeholder="Ej: El archivo no cumple con el formato APA..."
                            value={motivo}
                            onChange={(e) => setMotivo(e.target.value)}
                        />
                        <div className="flex justify-end space-x-3">
                            <button onClick={() => setShowModal(false)} className="px-4 py-2 text-gray-500 hover:bg-gray-100 rounded-lg">
                                Cancelar
                            </button>
                            <button 
                                onClick={handleConfirmarRechazo} 
                                className={`px-4 py-2 rounded-lg text-white ${motivo.trim() ? 'bg-red-600 hover:bg-red-700' : 'bg-red-300 cursor-not-allowed'}`}
                                disabled={!motivo.trim()}
                            >
                                Confirmar Rechazo
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}