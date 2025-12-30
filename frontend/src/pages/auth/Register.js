// frontend/src/pages/auth/Register.js
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';

export default function Register() {
const navigate = useNavigate();
const [carreras, setCarreras] = useState([]);
const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    cedula: '',
    carrera: '',
    password_confirm: ''
});

  // Cargar carreras para el selector
useEffect(() => {
    const getCarreras = async () => {
    try {
        const res = await axios.get('/carreras/');
        const data = Array.isArray(res.data) ? res.data : res.data.results;
        setCarreras(data || []);
    } catch (err) { console.error(err); }
    };
    getCarreras();
}, []);

const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // Ruta según tu universidad_repositorio/urls.py
    await axios.post('/auth/register/', formData);
    toast.success("Registro exitoso. ¡Ahora puedes iniciar sesión!");
    navigate('/login');
    } catch (err) {
    toast.error("Error en el registro: " + JSON.stringify(err.response?.data));
    }
};

return (
    <div className="max-w-md mx-auto bg-white p-8 rounded shadow-lg mt-10">
    <h2 className="text-2xl font-bold mb-6">Registro de Usuario</h2>
    <form onSubmit={handleSubmit} className="space-y-4">
        <input type="text" placeholder="Cédula" required className="w-full border p-2" 
        onChange={e => setFormData({...formData, cedula: e.target.value})} />
        
        <div className="grid grid-cols-2 gap-2">
        <input type="text" placeholder="Nombre" required className="border p-2" 
            onChange={e => setFormData({...formData, first_name: e.target.value})} />
        <input type="text" placeholder="Apellido" required className="border p-2" 
            onChange={e => setFormData({...formData, last_name: e.target.value})} />
        </div>

        <input type="text" placeholder="Usuario" required className="w-full border p-2" 
        onChange={e => setFormData({...formData, username: e.target.value})} />
        
        <input type="email" placeholder="Correo" required className="w-full border p-2" 
        onChange={e => setFormData({...formData, email: e.target.value})} />

        <select required className="w-full border p-2" 
        onChange={e => setFormData({...formData, carrera: e.target.value})}>
        <option value="">Selecciona tu carrera</option>
        {carreras.map(c => <option key={c.id} value={c.id}>{c.nombre}</option>)}
        </select>

        <input type="password" placeholder="Contraseña" required className="w-full border p-2" 
        onChange={e => setFormData({...formData, password: e.target.value})} />

        <input type="password" placeholder="Confirmar Contraseña" required className="w-full border p-2" 
        onChange={e => setFormData({...formData, password_confirm: e.target.value})}
/>

        <button type="submit" className="w-full bg-primary-800 text-white py-2 rounded">
        Registrarse
        </button>
    </form>
    </div>
);
}