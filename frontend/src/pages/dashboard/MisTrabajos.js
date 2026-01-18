// frontend/src/pages/dashboard/MisTrabajos.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const MisTrabajos = () => {
    const [trabajos, setTrabajos] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchTrabajos = async () => {
            try {
                const token = localStorage.getItem('token');
                // Nota: Asegúrate de que este endpoint exista en tu backend
                const res = await axios.get('/trabajos/mis_trabajos/', {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setTrabajos(res.data);
            } catch (err) {
                console.error("Error al obtener mis trabajos:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchTrabajos();
    }, []);

    if (loading) return <div className="p-10 text-center">Cargando tus trabajos...</div>;

    return (
        <div className="p-6">
            <h1 className="text-2xl font-bold mb-6 text-primary-800">Mis Trabajos de Investigación</h1>
            
            {trabajos.length === 0 ? (
                <p className="text-gray-500">No tienes trabajos registrados aún.</p>
            ) : (
                <div className="grid gap-4">
                    {trabajos.map(t => (
                        <div key={t.id} className="bg-white border rounded-lg shadow-sm p-5">
                            <div className="flex justify-between items-start">
                                <h3 className="font-bold text-lg">{t.titulo}</h3>
                                <span className={`px-3 py-1 rounded-full text-sm ${
                                    t.estado === 'aprobado' ? 'bg-green-100 text-green-800' :
                                    t.estado === 'rechazado' ? 'bg-red-100 text-red-800' :
                                    'bg-yellow-100 text-yellow-800'
                                }`}>
                                    {t.estado.toUpperCase()}
                                </span>
                            </div>
                            
                            {/* Usamos carrera_nombre que ahora sí viene del backend */}
                            <p className="text-sm text-gray-600 mt-2">
                                Año: {t.año} | Carrera: {t.carrera_nombre || 'No especificada'}
                            </p>

                            {/* LÓGICA DEL MOTIVO DE RECHAZO MEJORADA */}
                            {t.estado === 'rechazado' && t.resumen && (
                                <div className="mt-4 p-3 bg-red-50 border-l-4 border-red-500 rounded">
                                    <p className="text-sm font-bold text-red-700">Nota del Revisor:</p>
                                    <p className="text-sm text-red-900">
                                        {/* Si el texto contiene el separador lo cortamos, si no, mostramos el resumen completo */}
                                        {t.resumen.includes('Motivo de rechazo:') 
                                            ? t.resumen.split('Motivo de rechazo:')[1] 
                                            : t.resumen}
                                    </p>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

// ESTA ES LA LÍNEA QUE FALTABA Y CAUSÓ EL ERROR:
export default MisTrabajos;