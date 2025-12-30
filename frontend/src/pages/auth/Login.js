// frontend/src/pages/auth/Login.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    const res = await login({ username, password });
    setLoading(false);
    if (res?.success) {
      navigate('/');
    }
  };

  return (
    <div className="container">
      <div className="card" style={{ maxWidth: 420, margin: '1rem auto' }}>
        <h2>Iniciar sesión</h2>
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: 8 }}>
            <label>Usuario</label>
            <input
              autoFocus
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="input"
              style={{ width: '100%', padding: 8, marginTop: 4 }}
            />
          </div>
          <div style={{ marginBottom: 8 }}>
            <label>Contraseña</label>
            <input
              required
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input"
              style={{ width: '100%', padding: 8, marginTop: 4 }}
            />
          </div>
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
            <button type="submit" disabled={loading} className="btn">
              {loading ? 'Ingresando...' : 'Entrar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
