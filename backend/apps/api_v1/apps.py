# backend/apps/api_v1/apps.py
from django.apps import AppConfig

class ApiV1Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.api_v1' # <--- ESTO DEBE COINCIDIR CON INSTALLED_APPS