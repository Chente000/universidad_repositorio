import React, { useEffect, useState } from 'react';
import axios from 'axios';

export default function ListaTrabajos() {
  const [trabajos, setTrabajos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
      axios.get('/trabajos/')
      .then((res) => {
        if (!mounted) return;
        const data = Array.isArray(res.data) ? res.data : (res.data.results || []);
        setTrabajos(data);
        setError(null);
      })
      .catch((err) => {
        if (!mounted) return;
        console.error("Detalle del error:", err);
        setError(err.response?.data || { detail: err.message });
        setTrabajos([]); // Resetear a array vacío en caso de error para que .map no falle
      })
      .finally(() => {
        if (!mounted) return;
        setLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, []);

  return (
    <div className="container">
      <div className="card">
        <h1>Lista de trabajos</h1>

        {loading && <p>Cargando trabajos...</p>}

        {error && (
          <div style={{ color: 'red' }}>
            Error cargando trabajos: {JSON.stringify(error)}
          </div>
        )}

        {!loading && !error && (
          <div>
            {trabajos.length === 0 ? (
              <p>No hay trabajos disponibles.</p>
            ) : (
              <ul>
                {Array.isArray(trabajos) && trabajos.map((t) => (
                  <li key={t.id} style={{ marginBottom: 8 }}>
                    <strong>{t.titulo || t.nombre || `Trabajo ${t.id}`}</strong>
                    <div style={{ fontSize: 12, color: '#444' }}>
                      {t.descripcion || t.resumen || ''}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

