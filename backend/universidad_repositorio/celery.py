import os
from datetime import datetime
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'universidad_repositorio.settings')

app = Celery('universidad_repositorio')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


# Configuración de tareas de IA
@app.task
def procesar_trabajo_con_ia(trabajo_id, pdf_path):
    """
    Procesar trabajo con IA en background
    """
    from ai_processor import get_ai_service
    
    try:
        service = get_ai_service()
        result = service.process_pdf_and_extract(pdf_path, str(trabajo_id))
        
        # Aquí actualizarías la base de datos con los resultados
        # Esta es una tarea simplificada
        
        return result
        
    except Exception as e:
        # Registrar error
        print(f"Error procesando trabajo {trabajo_id}: {e}")
        return {'success': False, 'error': str(e)}


@app.task
def actualizar_embeddings_todos_trabajos():
    """
    Actualizar embeddings de todos los trabajos (tarea de mantenimiento)
    """
    from apps.trabajos.models import TrabajoInvestigacion
    
    try:
        trabajos = TrabajoInvestigacion.objects.filter(estado='aprobado')
        service = get_ai_service()
        
        results = []
        for trabajo in trabajos:
            if trabajo.archivo_pdf and trabajo.contenido_extraido:
                embedding = service.generate_embedding(trabajo.contenido_extraido)
                if embedding is not None:
                    trabajo.embedding_vector = embedding.tolist()
                    trabajo.save()
                    results.append(trabajo.id)
        
        return f"Actualizados {len(results)} embeddings"
        
    except Exception as e:
        print(f"Error actualizando embeddings: {e}")
        return f"Error: {str(e)}"


@app.task
def generar_estadisticas_semanales():
    """
    Generar estadísticas semanales del sistema
    """
    from datetime import datetime, timedelta
    from apps.trabajos.models import TrabajoInvestigacion, LogActividades
    
    try:
        fecha_inicio = datetime.now() - timedelta(days=7)
        
        # Estadísticas de trabajos
        trabajos_nuevos = TrabajoInvestigacion.objects.filter(
            fecha_subida__gte=fecha_inicio
        ).count()
        
        trabajos_aprobados = TrabajoInvestigacion.objects.filter(
            fecha_aprobacion__gte=fecha_inicio
        ).count()
        
        # Estadísticas de descargas
        descargas_semana = LogActividades.objects.filter(
            accion='download',
            fecha__gte=fecha_inicio
        ).count()
        
        # Búsquedas realizadas
        busquedas_semana = LogActividades.objects.filter(
            accion='search',
            fecha__gte=fecha_inicio
        ).count()
        
        estadisticas = {
            'periodo': f"{fecha_inicio.strftime('%Y-%m-%d')} - {datetime.now().strftime('%Y-%m-%d')}",
            'trabajos_nuevos': trabajos_nuevos,
            'trabajos_aprobados': trabajos_aprobados,
            'descargas_totales': descargas_semana,
            'busquedas_totales': busquedas_semana
        }
        
        # Aquí podrías guardar estas estadísticas en la base de datos
        # o enviarlas por email a los administradores
        
        return estadisticas
        
    except Exception as e:
        print(f"Error generando estadísticas: {e}")
        return f"Error: {str(e)}"


@app.task
def limpiar_archivos_temporales():
    """
    Limpiar archivos temporales y cache antiguos
    """
    import tempfile
    import shutil
    from pathlib import Path
    
    try:
        # Limpiar directorio temporal
        temp_dir = Path(tempfile.gettempdir())
        temp_files = list(temp_dir.glob('universidad_repositorio_*'))
        
        cleaned = 0
        for temp_file in temp_files:
            if temp_file.is_file():
                temp_file.unlink()
                cleaned += 1
            elif temp_file.is_dir():
                shutil.rmtree(temp_file)
                cleaned += 1
        
        # Limpiar cache de Django
        from django.core.cache import cache
        cache.clear()
        
        return f"Limpieza completada. {cleaned} elementos removidos."
        
    except Exception as e:
        print(f"Error en limpieza: {e}")
        return f"Error: {str(e)}"


@app.task
def verificar_salud_sistema():
    """
    Verificar salud del sistema y servicios externos
    """
    try:
        import requests
        from universidad_repositorio.settings import AI_SERVICE_URL
        
        status = {
            'timestamp': datetime.now().isoformat(),
            'database': 'ok',
            'redis': 'ok',
            'ai_service': 'unknown',
            'storage': 'unknown'
        }
        
        # Verificar servicio de IA
        try:
            response = requests.get(f"{AI_SERVICE_URL}/health", timeout=5)
            status['ai_service'] = 'ok' if response.status_code == 200 else 'error'
        except:
            status['ai_service'] = 'unavailable'
        
        # Verificar Redis
        try:
            from django.core.cache import cache
            cache.set('health_check', 'ok', 10)
            result = cache.get('health_check')
            status['redis'] = 'ok' if result == 'ok' else 'error'
        except:
            status['redis'] = 'error'
        
        # Aquí podrías agregar más verificaciones
        
        return status
        
    except Exception as e:
        return f"Error en verificación: {str(e)}"


# Tareas periódicas (celery beat)
app.conf.beat_schedule = {
    'generar-estadisticas-semanales': {
        'task': 'universidad_repositorio.celery.generar_estadisticas_semanales',
        'schedule': 7 * 24 * 60 * 60,  # Cada 7 días
    },
    'limpiar-archivos-temporales': {
        'task': 'universidad_repositorio.celery.limpiar_archivos_temporales',
        'schedule': 24 * 60 * 60,  # Cada 24 horas
    },
    'verificar-salud-sistema': {
        'task': 'universidad_repositorio.celery.verificar_salud_sistema',
        'schedule': 60 * 60,  # Cada hora
    },
    'actualizar-embeddings': {
        'task': 'universidad_repositorio.celery.actualizar_embeddings_todos_trabajos',
        'schedule': 24 * 7 * 60 * 60,  # Cada semana
    },
}

app.conf.timezone = 'America/Caracas'