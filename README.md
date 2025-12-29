# Repositorio Digital de Trabajos de Investigación - UNEFA

Sistema integral de gestión de trabajos de investigación asistido por inteligencia artificial para la Universidad Nacional Experimental de las Fuerzas Armadas Nacional Bolivariana.

## 🎯 Características Principales

### Funcionalidades Core
- **Búsqueda Inteligente**: Sistema de búsqueda semántica con IA que recomienda trabajos relevantes
- **Procesamiento Automático**: Extracción automática de metadatos (título, autores, objetivos, resumen)
- **Gestión de Usuarios**: Control de acceso por roles y permisos específicos
- **Descarga Controlada**: Sistema de descargas con registro obligatorio y retroalimentación
- **Calificaciones y Comentarios**: Sistema de evaluación y comentarios de usuarios
- **Aprobación de Trabajos**: Flujo de aprobación con superusuarios

### Tipos de Trabajos Soportados
- **Trabajos Especiales de Grado**: Para estudiantes de ingeniería y licenciatura
- **Prácticas Profesionales**: Para estudiantes de TSU

### Carreras Incluidas
- Ingeniería Naval
- Ingeniería de Sistemas
- Ingeniería Petroquímica
- TSU en Enfermería
- TSU en Turismo
- Licenciatura en Economía Social

## 🏗️ Arquitectura del Sistema

### Backend (Django + DRF)
```
backend/
├── universidad_repositorio/          # Configuración principal
├── apps/
│   ├── usuarios/                     # Gestión de usuarios
│   ├── trabajos/                     # Trabajos de investigación
│   └── comentarios/                  # Sistema de comentarios
├── requirements.txt                  # Dependencias Python
└── manage.py                        # Script de administración
```

### Frontend (React + Tailwind)
```
frontend/
├── src/
│   ├── components/                   # Componentes reutilizables
│   ├── pages/                        # Páginas principales
│   ├── context/                      # Context API (Auth, etc.)
│   ├── hooks/                        # Custom hooks
│   ├── utils/                        # Utilidades
│   └── App.js                        # Componente principal
├── package.json                      # Dependencias Node.js
└── tailwind.config.js               # Configuración Tailwind
```

### Servicio de IA (FastAPI)
```
services/ai_service/
├── main.py                          # API FastAPI
├── ai_processor.py                  # Procesamiento de documentos
├── requirements.txt                 # Dependencias IA
└── README.md                        # Documentación del servicio
```

## 🚀 Instalación y Configuración

### Prerrequisitos
- Python 3.11+
- Node.js 16+
- PostgreSQL 14+
- Redis
- Git

### 1. Clonar el Repositorio
```bash
git clone <repository-url>
cd universidad_repositorio
```

### 2. Configurar Base de Datos
```bash
# Crear base de datos PostgreSQL
createdb universidad_repositorio

# Configurar variables de entorno
cp .env.example .env
# Editar .env con las credenciales de la base de datos
```

### 3. Backend Django
```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con configuración local

# Ejecutar migraciones
python manage.py makemigrations
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Recolectar archivos estáticos
python manage.py collectstatic
```

### 4. Frontend React
```bash
cd frontend

# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env.local
# Editar .env.local con API URL

# Ejecutar en desarrollo
npm start
```

### 5. Servicio de IA
```bash
cd services/ai_service

# Crear entorno virtual
python -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Descargar modelos de spaCy
python -m spacy download es_core_news_sm

# Ejecutar servicio
python main.py
```

## 🛠️ Configuración de Servicios

### Variables de Entorno Backend (.env)
```env
# Django
DEBUG=True
SECRET_KEY=tu-clave-secreta-aqui
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de Datos
DB_NAME=universidad_repositorio
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/1
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# AWS S3 (opcional)
AWS_ACCESS_KEY_ID=tu-access-key
AWS_SECRET_ACCESS_KEY=tu-secret-key
AWS_STORAGE_BUCKET_NAME=universidad-repositorio-files

# Servicio de IA
AI_SERVICE_URL=http://localhost:8000
AI_SERVICE_TOKEN=tu-ai-service-token
```

### Variables de Entorno Frontend (.env.local)
```env
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_AI_SERVICE_URL=http://localhost:8000
```

## 👥 Gestión de Usuarios y Roles

### Roles del Sistema
1. **Estudiante**: Puede buscar y descargar trabajos aprobados
2. **Encargado Trabajo Especial de Grado**: Puede subir y gestionar trabajos de grado
3. **Super Usuario Trabajo Especial de Grado**: Puede aprobar/rechazar trabajos de grado
4. **Encargado Prácticas Profesionales**: Puede subir y gestionar prácticas
5. **Super Usuario Prácticas Profesionales**: Puede aprobar/rechazar prácticas
6. **Administrador**: Acceso completo al sistema

### Permisos por Rol
| Funcionalidad | Estudiante | Encargado | Superuser | Admin |
|---------------|------------|-----------|-----------|--------|
| Ver trabajos aprobados | ✅ | ✅ | ✅ | ✅ |
| Descargar trabajos | ✅ | ✅ | ✅ | ✅ |
| Subir trabajos | ❌ | ✅ | ✅ | ✅ |
| Aprobar/rechazar | ❌ | ❌ | ✅ | ✅ |
| Gestionar usuarios | ❌ | ❌ | ❌ | ✅ |
| Ver estadísticas | ❌ | ✅ | ✅ | ✅ |

## 🔄 Flujo de Trabajo

### 1. Subida de Trabajos
1. Usuario con permisos sube archivo PDF
2. Sistema valida permisos y formato
3. Servicio de IA procesa documento automáticamente:
   - Extrae texto completo
   - Identifica título, autores, tutores, año
   - Genera resumen automático
   - Extrae objetivos
   - Crea embeddings para búsqueda semántica
4. Trabajo queda en estado "Pendiente"

### 2. Aprobación de Trabajos
1. Superusuario revisa trabajo procesado
2. Verifica información extraída por IA
3. Aprueba, rechaza o solicita correcciones
4. Trabajo aprobado se vuelve visible para estudiantes

### 3. Búsqueda y Descarga
1. Estudiante busca trabajos por texto o filtros
2. Sistema usa IA para encontrar trabajos relevantes
3. Muestra resultados con explicación de relevancia
4. Usuario debe registrarse para descargar
5. Sistema registra descarga y solicita retroalimentación

## 🤖 Sistema de Inteligencia Artificial

### Componentes de IA
- **Procesamiento de Texto**: spaCy + NLTK para análisis lingüístico
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Resumen Automático**: BART/T5 para generación de resúmenes
- **Búsqueda Semántica**: FAISS + cosine similarity
- **Detección de Duplicados**: Hash MD5 de contenido

### Endpoints de IA
```
POST /process_pdf     # Procesar documento PDF
POST /search          # Búsqueda semántica
POST /similar         # Encontrar trabajos similares
GET  /model_info      # Información de modelos
POST /batch_process   # Procesamiento en lote
```

## 📊 Monitoreo y Logs

### Logs del Sistema
- **Actividades de Usuario**: Login, búsqueda, descarga
- **Procesamiento de IA**: Extracción de datos, generación de embeddings
- **Operaciones de Archivo**: Subidas, descargas, validaciones
- **Errores del Sistema**: Fallos de procesamiento, errores de base de datos

### Métricas Disponibles
- Total de trabajos por carrera y tipo
- Trabajos más descargados
- Calificaciones promedio
- Uso por tipo de usuario
- Rendimiento del sistema de IA

## 🔒 Seguridad

### Medidas de Seguridad
- Autenticación JWT con refresh tokens
- Validación de permisos por rol
- Sanitización de archivos subidos
- Rate limiting en APIs
- Logs de auditoría completos
- Hash de archivos para detección de duplicados

### Almacenamiento Seguro
- Archivos PDF en Amazon S3 o almacenamiento local seguro
- Base de datos PostgreSQL con conexiones cifradas
- Variables de entorno para datos sensibles
- Backup automático de datos críticos

## 🚀 Despliegue en Producción

### Docker (Recomendado)
```bash
# Construir imágenes
docker-compose build

# Ejecutar servicios
docker-compose up -d

# Ejecutar migraciones
docker-compose exec backend python manage.py migrate

# Crear superusuario
docker-compose exec backend python manage.py createsuperuser
```

### Servidor Web (Nginx + Gunicorn)
```bash
# Backend con Gunicorn
gunicorn universidad_repositorio.wsgi:application --bind 0.0.0.0:8000

# Frontend con Nginx
# Configurar proxy_pass a React build
```

### Variables de Producción
- Cambiar `DEBUG=False`
- Configurar `SECRET_KEY` segura
- Configurar base de datos de producción
- Configurar almacenamiento S3
- Configurar Redis en producción
- Configurar CORS para dominios de producción

## 🧪 Testing

### Backend Tests
```bash
cd backend
python manage.py test
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Tests de IA
```bash
cd services/ai_service
python -m pytest tests/
```

## 📚 Documentación API

### Autenticación
```bash
# Login
POST /api/v1/auth/login/
{
  "username": "usuario",
  "password": "password"
}

# Registro
POST /api/v1/auth/register/
{
  "username": "nuevo_usuario",
  "email": "email@ejemplo.com",
  "password": "password123",
  "first_name": "Juan",
  "last_name": "Pérez",
  "cedula": "12345678"
}
```

### Trabajos de Investigación
```bash
# Listar trabajos
GET /api/v1/trabajos/

# Crear trabajo (solo usuarios autorizados)
POST /api/v1/trabajos/
{
  "titulo": "Título del trabajo",
  "autores": "Autor 1, Autor 2",
  "tutores": "Tutor 1",
  "carrera": "ingenieria_sistemas",
  "tipo_trabajo": "especial_grado",
  "año": 2024,
  "archivo_pdf": "archivo.pdf"
}

# Búsqueda inteligente
GET /api/v1/trabajos/buscar_inteligente/?q=programación&carrera=ingenieria_sistemas
```

## 🤝 Contribución

### Guías de Contribución
1. Fork el repositorio
2. Crear branch para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push al branch (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

### Estándares de Código
- Python: PEP 8
- JavaScript: ESLint + Prettier
- Documentación: Docstrings y comentarios claros
- Tests: Cobertura mínima del 80%

## 📞 Soporte

### Contacto
- **Desarrollador**: MiniMax Agent
- **Universidad**: UNEFA
- **Proyecto**: Repositorio Digital de Trabajos de Investigación

### Documentación Adicional
- [Documentación de la API](./docs/api.md)
- [Guía de部署](./docs/deployment.md)
- [Manual de Usuario](./docs/user-manual.md)
- [Guía de Administración](./docs/admin-guide.md)

## 📄 Licencia

Este proyecto está desarrollado específicamente para la Universidad Nacional Experimental de las Fuerzas Armadas Nacional Bolivariana (UNEFA).

---

**Desarrollado con ❤️ por MiniMax Agent para UNEFA**

*Última actualización: 19 de noviembre de 2025*