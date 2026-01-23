// frontend/src/pages/dashboard/Perfil.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Perfil = () => {
    const [usuario, setUsuario] = useState(null);
    const [loading, setLoading] = useState(true);
    const [passwordData, setPasswordData] = useState({
        password_actual: '',
        password_nueva: '',
        password_nueva_confirm: ''
    });
    const [mensaje, setMensaje] = useState({ tipo: '', texto: '' });

    useEffect(() => {
        const fetchPerfil = async () => {
            try {
                const token = localStorage.getItem('token');
                const res = await axios.get('http://localhost:8001/api/v1/usuarios/perfil/', {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setUsuario(res.data);
            } catch (err) {
                console.error("Error al cargar perfil", err);
            } finally {
                setLoading(false);
            }
        };
        fetchPerfil();
    }, []);

    const handlePasswordChange = async (e) => {
        e.preventDefault();
        setMensaje({ tipo: '', texto: '' });

        try {
            const token = localStorage.getItem('token');
            await axios.post('http://localhost:8001/api/v1/usuarios/cambiar_password/', passwordData, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setMensaje({ tipo: 'success', texto: 'Contraseña actualizada correctamente.' });
            setPasswordData({ password_actual: '', password_nueva: '', password_nueva_confirm: '' });
        } catch (err) {
            setMensaje({ 
                tipo: 'error', 
                texto: err.response?.data?.non_field_errors || "Error al cambiar la contraseña. Verifica tus datos." 
            });
        }
    };

    if (loading) return <div className="p-10 text-center">Cargando perfil...</div>;

    return (
        <div className="p-6 max-w-4xl mx-auto">
            <h1 className="text-3xl font-bold mb-8 text-primary-800">Mi Perfil</h1>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Columna Izquierda: Información General */}
                <div className="md:col-span-2 space-y-6">
                    <div className="bg-white p-6 rounded-xl shadow-md border border-gray-100">
                        <h2 className="text-xl font-semibold mb-4 border-b pb-2">Datos Personales</h2>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <p className="text-sm text-gray-500">Nombre Completo</p>
                                <p className="font-medium">{usuario?.first_name} {usuario?.last_name}</p>
                            </div>
                            <div>
                                <p className="text-sm text-gray-500">Cédula</p>
                                <p className="font-medium">{usuario?.cedula}</p>
                            </div>
                            <div>
                                <p className="text-sm text-gray-500">Correo Electrónico</p>
                                <p className="font-medium">{usuario?.email}</p>
                            </div>
                            <div>
                                <p className="text-sm text-gray-500">Teléfono</p>
                                <p className="font-medium">{usuario?.telefono || 'No registrado'}</p>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white p-6 rounded-xl shadow-md border border-gray-100">
                        <h2 className="text-xl font-semibold mb-4 border-b pb-2">Información Académica</h2>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <p className="text-sm text-gray-500">Carrera</p>
                                <p className="font-medium">{usuario?.carrera_display}</p>
                            </div>
                            <div>
                                <p className="text-sm text-gray-500">Rol de Usuario</p>
                                <p className="font-medium capitalize">{usuario?.rol_display}</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Columna Derecha: Cambio de Contraseña */}
                <div className="bg-white p-6 rounded-xl shadow-md border border-gray-100 h-fit">
                    <h2 className="text-xl font-semibold mb-4 border-b pb-2">Seguridad</h2>
                    <form onSubmit={handlePasswordChange} className="space-y-4">
                        <div>
                            <label className="block text-sm text-gray-600">Contraseña Actual</label>
                            <input 
                                type="password" 
                                className="w-full p-2 border rounded mt-1"
                                value={passwordData.password_actual}
                                onChange={(e) => setPasswordData({...passwordData, password_actual: e.target.value})}
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm text-gray-600">Nueva Contraseña</label>
                            <input 
                                type="password" 
                                className="w-full p-2 border rounded mt-1"
                                value={passwordData.password_nueva}
                                onChange={(e) => setPasswordData({...passwordData, password_nueva: e.target.value})}
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm text-gray-600">Confirmar Nueva</label>
                            <input 
                                type="password" 
                                className="w-full p-2 border rounded mt-1"
                                value={passwordData.password_nueva_confirm}
                                onChange={(e) => setPasswordData({...passwordData, password_nueva_confirm: e.target.value})}
                                required
                            />
                        </div>
                        
                        {mensaje.texto && (
                            <div className={`p-2 text-xs rounded ${mensaje.tipo === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                                {mensaje.texto}
                            </div>
                        )}

                        <button 
                            type="submit"
                            className="w-full bg-primary-600 text-white py-2 rounded-lg hover:bg-primary-700 transition"
                        >
                            Actualizar Contraseña
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default Perfil;