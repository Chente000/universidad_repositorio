// frontend/src/components/layout/Header.js
import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { 
  MagnifyingGlassIcon, 
  UserCircleIcon, 
  Bars3Icon, 
  XMarkIcon,
  AcademicCapIcon,
  DocumentTextIcon,
  ChartBarIcon,
  ArrowRightOnRectangleIcon,
  UserIcon,
  Cog6ToothIcon
} from '@heroicons/react/24/outline';
import { useAuth } from '../../context/AuthContext';

function Header() {
  const { user, isAuthenticated, logout, hasAnyRole } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/');
    setIsProfileMenuOpen(false);
  };

  const navigationItems = [
    { name: 'Inicio', href: '/', icon: AcademicCapIcon },
    { name: 'Buscar', href: '/busqueda', icon: MagnifyingGlassIcon },
    { name: 'Trabajos', href: '/trabajos', icon: DocumentTextIcon },
  ];

  const dashboardItems = [
    { name: 'Dashboard', href: '/dashboard', icon: ChartBarIcon },
    { name: 'Subir Trabajo', href: '/dashboard/subir', icon: DocumentTextIcon },
    { name: 'Gestión', href: '/dashboard/Gestion', icon: Cog6ToothIcon },
  ];

  return (
    <header className="bg-white shadow-lg border-b-4 border-primary-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo y título */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-3">
              <div className="bg-primary-800 p-2 rounded-lg">
                <AcademicCapIcon className="h-8 w-8 text-white" />
              </div>
              <div className="hidden md:block">
                <h1 className="text-xl font-bold text-primary-800">
                  Repositorio UNEFA
                </h1>
                <p className="text-sm text-gray-600">
                  Trabajos de Investigación
                </p>
              </div>
            </Link>
          </div>

          {/* Navegación desktop */}
          <nav className="hidden md:flex space-x-8">
            {navigationItems.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive
                      ? 'text-primary-800 bg-primary-50 border-b-2 border-primary-800'
                      : 'text-gray-700 hover:text-primary-800 hover:bg-gray-50'
                  }`}
                >
                  <item.icon className="h-4 w-4" />
                  <span>{item.name}</span>
                </Link>
              );
            })}

            {/* NUEVO: Link para Estudiantes */}
            {user?.rol === 'estudiante' && (
              <Link
                to="/dashboard/mis-trabajos"
                className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  location.pathname === '/dashboard/mis-trabajos'
                    ? 'text-primary-800 bg-primary-50 border-b-2 border-primary-800'
                    : 'text-gray-700 hover:text-primary-800 hover:bg-gray-50'
                }`}
              >
                <DocumentTextIcon className="h-4 w-4" />
                <span>Mis Trabajos</span>
              </Link>
            )}

            {/* Dashboard para usuarios autorizados */}
            {hasAnyRole(['encargado_especial_grado', 'superuser_especial_grado', 'encargado_pasantias', 'superuser_pasantias', 'administrador']) && (
              <div className="relative group">
                <button className="flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-primary-800 hover:bg-gray-50 transition-colors">
                  <Cog6ToothIcon className="h-4 w-4" />
                  <span>Gestión</span>
                </button>
                <div className="absolute left-0 mt-2 w-48 bg-white rounded-md shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                  <div className="py-1">
                    {dashboardItems.map((item) => (
                      <Link
                        key={item.name}
                        to={item.href}
                        className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 hover:bg-primary-50 hover:text-primary-800"
                      >
                        <item.icon className="h-4 w-4" />
                        <span>{item.name}</span>
                      </Link>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </nav>

          {/* Botones de autenticación */}
          <div className="hidden md:flex items-center space-x-4">
            {isAuthenticated ? (
              <div className="relative">
                <button
                  onClick={() => setIsProfileMenuOpen(!isProfileMenuOpen)}
                  className="flex items-center space-x-2 text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <UserCircleIcon className="h-8 w-8 text-gray-600" />
                  <div className="text-left">
                    <p className="text-sm font-medium text-gray-900">
                      {user?.first_name || user?.username}
                    </p>
                    <p className="text-xs text-gray-600">
                      {user?.rol_display || user?.rol}
                    </p>
                  </div>
                </button>

                {/* Menú desplegable del perfil */}
                {isProfileMenuOpen && (
                  <div className="absolute right-0 mt-2 w-56 bg-white rounded-md shadow-lg py-1 z-50">
                    <div className="px-4 py-3 border-b border-gray-100">
                      <p className="text-sm font-medium text-gray-900">
                        {user?.first_name} {user?.last_name}
                      </p>
                      <p className="text-sm text-gray-600">
                        {user?.email}
                      </p>
                    </div>
                    
                  {user?.rol === 'estudiante' && (
                    <Link
                      to="/dashboard/mis-trabajos"
                      className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 border-b border-gray-100"
                      onClick={() => setIsProfileMenuOpen(false)}
                    >
                      <DocumentTextIcon className="h-4 w-4 text-primary-600" />
                      <span className="font-semibold text-primary-700">Mis Trabajos</span>
                    </Link>
                  )}

                    <Link
                      to="/dashboard/perfil"
                      className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                      onClick={() => setIsProfileMenuOpen(false)}
                    >
                      <UserIcon className="h-4 w-4" />
                      <span>Mi Perfil</span>
                    </Link>
                    
                    <button
                      onClick={handleLogout}
                      className="flex items-center space-x-2 w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                    >
                      <ArrowRightOnRectangleIcon className="h-4 w-4" />
                      <span>Cerrar Sesión</span>
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center space-x-3">
                <Link
                  to="/login"
                  className="text-gray-700 hover:text-primary-800 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  Iniciar Sesión
                </Link>
                <Link
                  to="/register"
                  className="bg-primary-800 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-primary-700 transition-colors"
                >
                  Registrarse
                </Link>
              </div>
            )}
          </div>

          {/* Botón de menú móvil */}
          <div className="md:hidden">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="text-gray-700 hover:text-primary-800 p-2"
            >
              {isMenuOpen ? (
                <XMarkIcon className="h-6 w-6" />
              ) : (
                <Bars3Icon className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>

        {/* Menú móvil */}
        {isMenuOpen && (
          <div className="md:hidden py-4 border-t border-gray-200">
            <div className="space-y-1">
              {navigationItems.map((item) => {
                const isActive = location.pathname === item.href;
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`flex items-center space-x-2 px-3 py-2 rounded-md text-base font-medium ${
                      isActive
                        ? 'text-primary-800 bg-primary-50'
                        : 'text-gray-700 hover:text-primary-800 hover:bg-gray-50'
                    }`}
                    onClick={() => setIsMenuOpen(false)}
                  >
                    <item.icon className="h-5 w-5" />
                    <span>{item.name}</span>
                  </Link>
                );
              })}

              {/* NUEVO: Link Móvil para Estudiantes */}
              {user?.rol === 'estudiante' && (
                <Link
                  to="/dashboard/mis-trabajos"
                  className={`flex items-center space-x-2 px-3 py-2 rounded-md text-base font-medium ${
                    location.pathname === '/dashboard/mis-trabajos'
                      ? 'text-primary-800 bg-primary-50'
                      : 'text-gray-700 hover:text-primary-800 hover:bg-gray-50'
                  }`}
                  onClick={() => setIsMenuOpen(false)}
                >
                  <DocumentTextIcon className="h-5 w-5" />
                  <span>Mis Trabajos</span>
                </Link>
              )}

              {/* Dashboard móvil para usuarios autorizados */}
              {hasAnyRole(['encargado_especial_grado', 'superuser_especial_grado', 'encargado_pasantias', 'superuser_pasantias', 'administrador']) && (
                <>
                  <div className="pt-4 border-t border-gray-200">
                    <p className="px-3 text-sm font-medium text-gray-500 uppercase tracking-wider">
                      Gestión
                    </p>
                    {dashboardItems.map((item) => (
                      <Link
                        key={item.name}
                        to={item.href}
                        className="flex items-center space-x-2 px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-primary-800 hover:bg-gray-50"
                        onClick={() => setIsMenuOpen(false)}
                      >
                        <item.icon className="h-5 w-5" />
                        <span>{item.name}</span>
                      </Link>
                    ))}
                  </div>
                </>
              )}

              {/* Autenticación móvil */}
              <div className="pt-4 border-t border-gray-200">
                {isAuthenticated ? (
                  <div className="space-y-1">
                    <div className="px-3 py-2">
                      <p className="text-base font-medium text-gray-900">
                        {user?.first_name} {user?.last_name}
                      </p>
                      <p className="text-sm text-gray-600">
                        {user?.email}
                      </p>
                    </div>
                    <Link
                      to="/dashboard/perfil"
                      className="flex items-center space-x-2 px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-primary-800 hover:bg-gray-50"
                      onClick={() => setIsMenuOpen(false)}
                    >
                      <UserIcon className="h-5 w-5" />
                      <span>Mi Perfil</span>
                    </Link>
                    <button
                      onClick={() => {
                        handleLogout();
                        setIsMenuOpen(false);
                      }}
                      className="flex items-center space-x-2 w-full text-left px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-primary-800 hover:bg-gray-50"
                    >
                      <ArrowRightOnRectangleIcon className="h-5 w-5" />
                      <span>Cerrar Sesión</span>
                    </button>
                  </div>
                ) : (
                  <div className="space-y-1">
                    <Link
                      to="/login"
                      className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-primary-800 hover:bg-gray-50"
                      onClick={() => setIsMenuOpen(false)}
                    >
                      Iniciar Sesión
                    </Link>
                    <Link
                      to="/register"
                      className="block px-3 py-2 rounded-md text-base font-medium bg-primary-800 text-white hover:bg-primary-700"
                      onClick={() => setIsMenuOpen(false)}
                    >
                      Registrarse
                    </Link>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}

export default Header;