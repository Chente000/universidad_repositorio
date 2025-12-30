import os
from pathlib import Path
from decouple import config
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = ['*']

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'storages',
]

LOCAL_APPS = [
    'apps.usuarios',
    'apps.trabajos',
    'apps.busqueda',
    'apps.comentarios',
    'apps.api_v1',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Use custom user model
AUTH_USER_MODEL = 'usuarios.Usuario'

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'universidad_repositorio.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'universidad_repositorio.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='universidad_repositorio'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='password'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        # PostgreSQL/psycopg2 no utiliza 'charset' en OPTIONS; dejar sin OPTIONS
    }
}

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Celery Configuration
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Caracas'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Django REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FileUploadParser',
    ],
}

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# Internationalization
LANGUAGE_CODE = 'es-ve'
TIME_ZONE = 'America/Caracas'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Esta línea asegura que se guarden en tu carpeta /media/
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# File Storage Configuration
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='')
# AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='')
# AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='universidad-repositorio-files')
# AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')
# AWS_DEFAULT_ACL = None
# AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]
CORS_ALLOW_ALL_ORIGINS = False # <-- CAMBIO CLAVE
CORS_ALLOW_CREDENTIALS = True

# Añadir esto para asegurar el manejo de peticiones OPTIONS que requieren otros métodos/headers
CORS_ALLOW_METHODS = [
    'DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT',
]
CORS_ALLOW_HEADERS = [
    'accept', 'accept-encoding', 'authorization', 'content-type',
    'dnt', 'origin', 'user-agent', 'x-csrftoken', 'x-requested-with',
    'x-auth-token', # Si tu Frontend usa un header custom para el token
]

# NUEVA CONFIGURACIÓN: CSRF Trusted Origins
# Esto es crucial para solucionar el error 403 (Forbidden) en las peticiones POST.
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]
CSRF_COOKIE_DOMAIN = None # Esto le permite usar el dominio del host de la petición

# AI Service Configuration
AI_SERVICE_URL = config('AI_SERVICE_URL', default='http://localhost:8000')
AI_SERVICE_TOKEN = config('AI_SERVICE_TOKEN', default='your-ai-service-token')

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}

# University Configuration
UNIVERSITY_NAME = "Universidad Nacional Experimental de las Fuerzas Armadas Nacional Bolivariana"
UNIVERSITY_COLORS = {
    'primary': '#1e3a8a',  # Azul institucional
    'secondary': '#f59e0b',  # Dorado institucional
    'accent': '#dc2626',  # Rojo institucional
}

# Work Types
WORK_TYPES = [
    ('especial_grado', 'Trabajo Especial de Grado'),
    ('practicas_profesionales', 'Prácticas Profesionales'),
]

# Careers
CAREERS = [
    ('ingenieria_naval', 'Ingeniería Naval'),
    ('ingenieria_sistemas', 'Ingeniería de Sistemas'),
    ('ingenieria_petroquimica', 'Ingeniería Petroquímica'),
    ('tsu_enfermeria', 'TSU en Enfermería'),
    ('tsu_turismo', 'TSU en Turismo'),
    ('licenciatura_economia_social', 'Licenciatura en Economía Social'),
]

# User Roles
USER_ROLES = [
    ('estudiante', 'Estudiante'),
    ('encargado_especial_grado', 'Encargado Trabajo Especial de Grado'),
    ('superuser_especial_grado', 'Super Usuario Trabajo Especial de Grado'),
    ('encargado_pasantias', 'Encargado Prácticas Profesionales'),
    ('superuser_pasantias', 'Super Usuario Prácticas Profesionales'),
    ('administrador', 'Administrador'),
]

# Default settings
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Create logs directory if it doesn't exist
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# CONFIGURACIÓN PARA PROXY/DOCKER
# Le dice a Django que confíe en los headers que vienen del proxy
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')