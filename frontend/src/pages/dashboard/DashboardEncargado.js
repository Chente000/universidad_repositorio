import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

export default function DashboardEncargado() {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const token = localStorage.getItem('token');
                const res = await axios.get('/trabajos/estadisticas/', {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setStats(res.data);
            } catch (err) {
                console.error("Error al cargar estadísticas", err);
            } finally {
                setLoading(false);
            }
        };
        fetchStats();
    }, []);

    if (loading) return <div className="p-10 text-center">Cargando panel...</div>;

    // Sustituimos los componentes de iconos por emojis o texto para evitar errores de importación
    const cards = [
        { title: 'Total Trabajos', value: stats?.total_trabajos, icon: "📄", color: 'bg-blue-500' },
        { title: 'Pendientes', value: stats?.trabajos_pendientes, icon: "⏳", color: 'bg-yellow-500' },
        { title: 'Aprobados', value: stats?.trabajos_aprobados, icon: "✅", color: 'bg-green-500' },
        { title: 'Descargas Totales', value: stats?.total_descargas, icon: "📥", color: 'bg-purple-500' },
    ];

    return (
        <div className="p-6 bg-gray-50 min-h-screen">
            <h2 className="text-3xl font-bold mb-8 text-gray-800">Panel de Control</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
                {cards.map((card, idx) => (
                    <div key={idx} className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center">
                        <div className={`${card.color} p-4 rounded-lg text-white text-2xl mr-4 flex items-center justify-center w-14 h-14`}>
                            {card.icon}
                        </div>
                        <div>
                            <p className="text-sm text-gray-500 font-medium">{card.title}</p>
                            <p className="text-2xl font-bold text-gray-800">{card.value}</p>
                        </div>
                    </div>
                ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-2 bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <h3 className="text-xl font-bold mb-4 text-gray-700">Trabajos Recientes</h3>
                    <div className="space-y-4">
                        {stats?.recientes?.map(t => (
                            <div key={t.id} className="flex items-center justify-between p-4 hover:bg-gray-50 rounded-lg border border-transparent hover:border-gray-200 transition-all">
                                <div>
                                    <p className="font-semibold text-gray-800">{t.titulo}</p>
                                    <p className="text-xs text-gray-500">{t.autores} • {t.carrera_nombre}</p>
                                </div>
                                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                                    t.estado === 'aprobado' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                                }`}>
                                    {t.estado}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="bg-primary-900 text-white p-8 rounded-xl shadow-lg flex flex-col justify-between">
                    <div>
                        <h3 className="text-2xl font-bold mb-2">Gestión Operativa</h3>
                        <p className="text-primary-100 mb-6">Tienes {stats?.trabajos_pendientes} trabajos esperando revisión técnica.</p>
                    </div>
                    <button 
                        onClick={() => navigate('/dashboard/Gestion')}
                        className="bg-white text-primary-900 font-bold py-3 px-6 rounded-lg flex items-center justify-center hover:bg-primary-50 transition-colors"
                    >
                        Ir a Revisar <span className="ml-2">→</span>
                    </button>
                </div>
            </div>
        </div>
    );
}