// frontend/src/components/BuscadorIA.js
import React, { useState } from 'react';

const BuscadorIA = ({ onResultados }) => {
    const [query, setQuery] = useState('');
    const [loading, setLoading] = useState(false);

    const ejecutarBusqueda = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            // Llamamos al endpoint que ya tienes en Django
            const response = await fetch(`http://localhost:8000/api/v1/trabajos/buscar_inteligente/?q=${query}`);
            const data = await response.json();
            onResultados(data.resultados); // Pasamos los trabajos encontrados al padre
        } catch (error) {
            console.error("Error en búsqueda:", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <form onSubmit={ejecutarBusqueda} className="flex gap-2 p-4 bg-white rounded-lg shadow-md">
            <input 
                type="text" 
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Pregúntale a la IA (ej: Diferencias entre IA y redes neuronales)"
                className="flex-1 p-2 border border-blue-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button 
                type="submit" 
                disabled={loading}
                className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 transition-colors"
            >
                {loading ? 'Buscando...' : 'Buscar con IA'}
            </button>
        </form>
    );
};

export default BuscadorIA;