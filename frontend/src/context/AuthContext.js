// frontend/src/context/AuthContext.js
import React, { createContext, useContext, useReducer, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';

// Initial state
const initialState = {
  user: null,
  token: localStorage.getItem('token'),
  isLoading: true,
  isAuthenticated: false,
};

// Action types
const AUTH_ACTIONS = {
  LOGIN_START: 'LOGIN_START',
  LOGIN_SUCCESS: 'LOGIN_SUCCESS',
  LOGIN_FAILURE: 'LOGIN_FAILURE',
  LOGOUT: 'LOGOUT',
  SET_USER: 'SET_USER',
  SET_LOADING: 'SET_LOADING',
  TOKEN_REFRESHED: 'TOKEN_REFRESHED',
};

// Reducer
function authReducer(state, action) {
  switch (action.type) {
    case AUTH_ACTIONS.LOGIN_START:
      return {
        ...state,
        isLoading: true,
      };
    
    case AUTH_ACTIONS.LOGIN_SUCCESS:
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        isLoading: false,
      };
    
    case AUTH_ACTIONS.LOGIN_FAILURE:
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
      };
    
    case AUTH_ACTIONS.LOGOUT:
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
      };
    
    case AUTH_ACTIONS.SET_USER:
      return {
        ...state,
        user: action.payload,
        isAuthenticated: true,
      };
    
    case AUTH_ACTIONS.SET_LOADING:
      return {
        ...state,
        isLoading: action.payload,
      };
    
    case AUTH_ACTIONS.TOKEN_REFRESHED:
      return {
        ...state,
        token: action.payload,
      };
    
    default:
      return state;
  }
}

// Create context
const AuthContext = createContext();

// Provider component
export function AuthProvider({ children }) {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Configure axios defaults
  useEffect(() => {
    // base API URL for development - prefer relative paths so CRA `proxy` can avoid CORS
    axios.defaults.baseURL = 'http://localhost:8001/api/v1';
    const token = localStorage.getItem('token');
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      // Verify token and get user info
      verifyToken();
    } else {
      dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: false });
    }
  }, []);

  // Set axios interceptors for token management
  useEffect(() => {
    const { interceptors } = axios;
    const { request, response } = interceptors;

    // Request interceptor to add token
    const requestInterceptor = request.use(
      (config) => {
        const token = localStorage.getItem('token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor to handle token refresh
    const responseInterceptor = response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          
          try {
            const refreshToken = localStorage.getItem('refresh_token');
            if (refreshToken) {
              const response = await axios.post('/auth/token/refresh/', {
                refresh: refreshToken,
              });
              
              const { access } = response.data;
              localStorage.setItem('token', access);
              axios.defaults.headers.common['Authorization'] = `Bearer ${access}`;
              
              dispatch({ type: AUTH_ACTIONS.TOKEN_REFRESHED, payload: access });
              originalRequest.headers.Authorization = `Bearer ${access}`;
              
              return axios(originalRequest);
            }
          } catch (refreshError) {
            // Refresh failed, logout user
            logout();
          }
        }
        
        return Promise.reject(error);
      }
    );

    // Cleanup interceptors on unmount
    return () => {
      request.eject(requestInterceptor);
      response.eject(responseInterceptor);
    };
  }, []);

  // Verify token function
  const verifyToken = async () => {
    try {
      dispatch({ type: AUTH_ACTIONS.LOGIN_START });
      
      const response = await axios.get('/usuarios/perfil/');
      dispatch({ 
        type: AUTH_ACTIONS.SET_USER, 
        payload: response.data 
      });
      
    } catch (error) {
      console.error('Token verification failed:', error);
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
      dispatch({ type: AUTH_ACTIONS.LOGIN_FAILURE });
    }
  };

  // Login function
  const login = async (credentials) => {
    try {
      dispatch({ type: AUTH_ACTIONS.LOGIN_START });
      
      const response = await axios.post('/auth/login/', credentials);
      const { user, tokens } = response.data;
      
      // Store tokens
      localStorage.setItem('token', tokens.access);
      localStorage.setItem('refresh_token', tokens.refresh);
      
      // Set axios default header
      axios.defaults.headers.common['Authorization'] = `Bearer ${tokens.access}`;
      
      dispatch({
        type: AUTH_ACTIONS.LOGIN_SUCCESS,
        payload: { user, token: tokens.access }
      });
      
      toast.success(`¡Bienvenido, ${user.first_name || user.username}!`);
      return { success: true };
      
    } catch (error) {
      const message = error.response?.data?.detail || 'Error al iniciar sesión';
      toast.error(message);
      dispatch({ type: AUTH_ACTIONS.LOGIN_FAILURE });
      return { success: false, error: message };
    }
  };

  // Register function
  const register = async (userData) => {
    try {
      dispatch({ type: AUTH_ACTIONS.LOGIN_START });
      
      const response = await axios.post('/auth/register/', userData);
      const { user, tokens } = response.data;
      
      // Store tokens
      localStorage.setItem('token', tokens.access);
      localStorage.setItem('refresh_token', tokens.refresh);
      
      // Set axios default header
      axios.defaults.headers.common['Authorization'] = `Bearer ${tokens.access}`;
      
      dispatch({
        type: AUTH_ACTIONS.LOGIN_SUCCESS,
        payload: { user, token: tokens.access }
      });
      
      toast.success('¡Registro exitoso! Bienvenido al repositorio.');
      return { success: true };
      
    } catch (error) {
      const message = error.response?.data?.detail || 'Error al registrarse';
      toast.error(message);
      dispatch({ type: AUTH_ACTIONS.LOGIN_FAILURE });
      return { success: false, error: message };
    }
  };

  // Logout function
  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('refresh_token');
    delete axios.defaults.headers.common['Authorization'];
    dispatch({ type: AUTH_ACTIONS.LOGOUT });
    toast.info('Sesión cerrada');
  };

  // Update user function
  const updateUser = (userData) => {
    dispatch({ type: AUTH_ACTIONS.SET_USER, payload: userData });
  };

  // Check if user has role
  const hasRole = (role) => {
    if (!state.user) return false;
    
    const userRoles = [
      state.user.rol,
      ...(state.user.roles || [])
    ];
    
    return userRoles.includes(role);
  };

  // Check if user has any of the given roles
  const hasAnyRole = (roles) => {
    if (!state.user || !roles) return false;
    
    const userRoles = [
      state.user.rol,
      ...(state.user.roles || [])
    ];
    
    return roles.some(role => userRoles.includes(role));
  };

  // Check if user can upload certain type of work
  const canUpload = (tipoTrabajo) => {
    if (!state.user) return false;
    
    switch (tipoTrabajo) {
      case 'especial_grado':
        return state.user.puede_subir_especial_grado || hasRole('administrador');
      case 'practicas_profesionales':
        return state.user.puede_subir_pasantias || hasRole('administrador');
      default:
        return false;
    }
  };

  const value = {
    user: state.user,
    token: state.token,
    isLoading: state.isLoading,
    isAuthenticated: state.isAuthenticated,
    login,
    register,
    logout,
    updateUser,
    hasRole,
    hasAnyRole,
    canUpload,
    verifyToken,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// Custom hook to use auth context
export function useAuth() {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
}

// Export context for advanced usage
export { AuthContext };