# backend/apps/trabajos/services.py
import os
import requests
import logging

logger = logging.getLogger(__name__)

def enviar_pdf_a_ia(trabajo_id, pdf_file):
    url = "http://ai-service:8000/process_pdf"
    try:
        pdf_file.seek(0)
        # Enviamos el archivo: usar basename para evitar enviar rutas internas
        filename_only = os.path.basename(pdf_file.name)
        files = {'file': (filename_only, pdf_file.read(), 'application/pdf')}
        logger.info(f"Enviando PDF a IA: trabajo_id={trabajo_id}, filename={filename_only}")
        # Enviamos el ID como dato de formulario
        data = {'trabajo_id': str(trabajo_id)}
        
        response = requests.post(url, files=files, data=data, timeout=60)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Error de la IA: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error conexión: {e}")
        return None
    
def buscar_trabajos_ia(query, top_k=5):
    """
    Envía una consulta de texto a la IA y devuelve los IDs de los trabajos encontrados.
    """
    url = "http://ai-service:8000/search"
    payload = {
        "query": query,
        "top_k": top_k
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            return response.json() # Devuelve la lista de resultados con trabajo_id y score
        return []
    except Exception as e:
        logger.error(f"Error buscando en IA: {e}")
        return []