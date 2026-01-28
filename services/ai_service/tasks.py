# services/ai_service/tasks.py
import os
import logging
from ai_processor import get_ai_service
import requests
import json

logger = logging.getLogger(__name__)

def process_document_task(trabajo_id: str, pdf_path: str):
    """
    Tarea para procesar un documento en segundo plano.
    """
    try:
        logger.info(f"Iniciando tarea de fondo para trabajo_id: {trabajo_id}")
        service = get_ai_service()
        
        # Llamamos a la función pesada que ya definiste en ai_processor.py
        result = service.process_pdf_and_extract(pdf_path, trabajo_id)
        
        if result.get('success'):
            logger.info(f"Tarea completada con éxito para {trabajo_id}")
            # Enviar resultados estructurados al backend para actualizar el registro
            try:
                backend_url = os.environ.get('BACKEND_API_URL', 'http://backend:8001')
                endpoint = f"{backend_url}/api/v1/trabajos/{trabajo_id}/aplicar_ia/"
                payload = {
                    'structured_info': result.get('structured_info'),
                    'embedding': result.get('embedding_generated'),
                    'file_hash': result.get('file_hash'),
                }
                # Envío en JSON. En desarrollo asumimos endpoint abierto o en red interna.
                headers = {'Content-Type': 'application/json'}
                logger.info(f"Enviando resultados IA al backend: {endpoint}")
                resp = requests.post(endpoint, data=json.dumps(payload), headers=headers, timeout=10)
                logger.info(f"Backend responded {resp.status_code}: {resp.text}")
            except Exception as cb_exc:
                logger.exception(f"No se pudo enviar resultados a backend: {cb_exc}")
        else:
            logger.error(f"Error en la tarea: {result.get('error')}")
            
        return result
    except Exception as e:
        logger.error(f"Fallo crítico en la tarea de fondo: {str(e)}")
        return {"success": False, "error": str(e)}
    finally:
        # IMPORTANTE: Borrar el archivo temporal para no llenar el disco
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            logger.info(f"Copiado temporal eliminado: {pdf_path}")