import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

export default function SubirTrabajo() {
  const [formData, setFormData] = useState({
    titulo: '',
    autores: '',
    tutores: '',
    // IMPORTANTE: Ponemos un ID de carrera que exista en tu BD (ej: 1)
    // Más abajo añadiremos un <select> para que esto sea dinámico
    carrera: '1', 
    tipo_trabajo: 'especial_grado',
    año: new Date().getFullYear(),
  });
  
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validar que el archivo exista
    if (!file) {
        alert("Por favor selecciona un archivo PDF");
        return;
    }

    const data = new FormData();
    
    // Agregamos los campos de texto
    data.append('titulo', formData.titulo);
    data.append('autores', formData.autores);
    data.append('tutores', formData.tutores);
    data.append('carrera', formData.carrera); // Enviamos el ID de la carrera
    data.append('tipo_trabajo', formData.tipo_trabajo);
    data.append('año', formData.año);
    
    // IMPORTANTE: El nombre del campo debe coincidir con Django (archivo_pdf)
    data.append('archivo_pdf', file);

    try {
      setLoading(true);
      
      // Enviamos la petición
      // Si configuraste la BaseURL con /api/v1/ en otro lado, usa solo '/trabajos/'
      // Si no, usa la ruta completa como aparece abajo:
      await axios.post('/trabajos/', data, {
        headers: { 
            'Content-Type': 'multipart/form-data',
            // Si el usuario debe estar logueado, axios suele enviar el token 
            // automáticamente si lo configuraste en el AuthContext.
        },
      });

      alert("¡Trabajo subido con éxito!");
      navigate('/trabajos');
    } catch (err) {
      console.error("Error completo:", err.response?.data);
      
      let mensajeError = "Error de conexión con el servidor";

      if (err.response?.data) {
        // Si el error es un objeto (JSON), lo convertimos a texto
        if (typeof err.response.data === 'object') {
          mensajeError = JSON.stringify(err.response.data);
        } 
        // Si el error empieza con <!DOCTYPE, es un error 500 de Django (HTML)
        else if (typeof err.response.data === 'string' && err.response.data.includes('<!DOCTYPE')) {
          mensajeError = "Error interno del servidor (500). Verifica los logs de Django.";
        }
        // Cualquier otro caso de texto
        else {
          mensajeError = err.response.data;
        }
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

        {/* Carrera - CAMPO NUEVO PARA EVITAR EL ERROR 400 */}
        <div>
          <label className="block text-sm font-medium text-gray-700">Carrera</label>
          <select 
            name="carrera" 
            value={formData.carrera} 
            onChange={handleChange}
            required
            className="w-full border border-gray-300 p-2 rounded focus:ring-2 focus:ring-primary-500 outline-none bg-white"
          >
            <option value="1">Ingeniería de Sistemas</option>
            <option value="2">Ingeniería Civil</option>
            <option value="3">Economía Social</option>
            {/* Asegúrate de que los valores 1, 2, 3 correspondan a los IDs en tu base de datos */}
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