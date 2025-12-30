// frontend/src/pages/dashboard/SubirTrabajo.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

export default function SubirTrabajo() {
  const [formData, setFormData] = useState({
    titulo: '',
    autores: '',
    tutores: '',
    // IMPORTANTE: Ponemos un ID de carrera que exista en tu BD (ej: 1)
    // Más abajo añadiremos un <select> para que esto sea dinámico
    carrera: '', 
    tipo_trabajo: 'especial_grado',
    año: new Date().getFullYear(),
  });
  
  const [carreras, setCarreras] = useState([]);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  // Cargar carreras desde el backend al montar el componente
  useEffect(() => {
  const fetchCarreras = async () => {
    try {
      // Intenta con la ruta completa si axios no tiene baseURL configurada
      const response = await axios.get('/carreras/');
      
      // IMPORTANTE: DRF a veces devuelve la lista dentro de response.data.results 
      // si tienes paginación activada. Verifica esto:
      const data = Array.isArray(response.data) ? response.data : response.data.results;
      setCarreras(data || []);

    console.log("Carreras cargadas:", data); // Para que verifiques en consola
      setCarreras(data || []);
    } catch (err) {
      console.error("Error al cargar carreras:", err);
      setCarreras([]); // Si falla, mantenemos el array vacío para que no rompa el .map
    }
  };
  fetchCarreras();
}, []);


  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
        alert("Por favor selecciona un archivo PDF");
        return;
    }

    const data = new FormData();
    // Agregamos todos los campos del formData de una vez
    Object.keys(formData).forEach(key => data.append(key, formData[key]));
    // Agregamos el archivo con el nombre exacto que espera Django
    data.append('archivo_pdf', file);

    try {
      setLoading(true);
      
      await axios.post('/trabajos/', data, {
        headers: { 
            'Content-Type': 'multipart/form-data',
            // El token se suele manejar en interceptores, pero si no, agrégalo aquí:
            // 'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
      });

      alert("¡Trabajo subido con éxito!");
      navigate('/trabajos');
    } catch (err) {
      console.error("Error al subir:", err.response?.data);
      
      let mensajeError = "Error de conexión con el servidor";
      if (err.response?.data) {
        mensajeError = typeof err.response.data === 'object' 
          ? JSON.stringify(err.response.data) 
          : err.response.data;
      }
      alert("Error al subir: " + mensajeError);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto bg-white p-8 rounded-lg shadow-university mt-10">
      <h1 className="text-2xl font-bold mb-6 text-primary-800">Subir Nuevo Trabajo</h1>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Título */}
        <div>
          <label className="block text-sm font-medium text-gray-700">Título del Trabajo</label>
          <input 
            name="titulo" 
            onChange={handleChange} 
            required 
            className="w-full border border-gray-300 p-2 rounded focus:ring-2 focus:ring-primary-500 outline-none" 
          />
        </div>

        {/* Autores y Tutores */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Autor(es)</label>
            <input 
              name="autores" 
              onChange={handleChange} 
              required 
              className="w-full border border-gray-300 p-2 rounded focus:ring-2 focus:ring-primary-500 outline-none" 
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Tutor(es)</label>
            <input 
              name="tutores" 
              onChange={handleChange} 
              required 
              className="w-full border border-gray-300 p-2 rounded focus:ring-2 focus:ring-primary-500 outline-none" 
            />
          </div>
        </div>

        {/* Carrera - AHORA DINÁMICO */}
        <div>
          <label className="block text-sm font-medium text-gray-700">Carrera</label>
          <select 
            name="carrera" 
            value={formData.carrera} 
            onChange={handleChange}
            required
            className="w-full border border-gray-300 p-2 rounded focus:ring-2 focus:ring-primary-500 outline-none bg-white"
          >
            <option value="" disabled hidden>Seleccione una carrera</option>
            {Array.isArray(carreras) && carreras.map((c) => (
              <option key={c.id} value={c.id}>
                {c.nombre}
              </option>
            ))}
          </select>
        </div>

        {/* Archivo */}
        <div>
          <label className="block text-sm font-medium text-gray-700">Archivo PDF</label>
          <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
            <input 
              type="file" 
              accept=".pdf" 
              onChange={(e) => setFile(e.target.files[0])} 
              required 
              className="w-full cursor-pointer" 
            />
          </div>
        </div>

        {/* Botón */}
        <button 
          type="submit" 
          disabled={loading} 
          className={`w-full py-3 rounded-md text-white font-bold transition-colors ${
            loading ? 'bg-gray-400' : 'bg-primary-800 hover:bg-primary-700'
          }`}
        >
          {loading ? 'Procesando...' : 'Enviar a Revisión'}
        </button>
      </form>
    </div>
  );
}