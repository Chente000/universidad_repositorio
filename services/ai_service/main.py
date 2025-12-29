from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import os
import tempfile
import logging
from pathlib import Path

# Importar servicio de IA
from ai_processor import get_ai_service, AIService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title="Servicio de IA - Repositorio UNEFA",
    description="API para procesamiento de documentos y búsqueda inteligente",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 10
    filters: Optional[Dict[str, Any]] = {}

class SearchResult(BaseModel):
    trabajo_id: str
    metadata: Dict[str, Any]
    similarity_score: float
    reason: str

class ProcessResponse(BaseModel):
    success: bool
    trabajo_id: str
    file_hash: Optional[str] = None
    content_length: Optional[int] = None
    structured_info: Optional[Dict[str, Any]] = None
    embedding_generated: Optional[bool] = None
    error: Optional[str] = None

class SimilarityRequest(BaseModel):
    trabajo_id: str
    top_k: Optional[int] = 5

class ModelInfoResponse(BaseModel):
    embedding_model: Optional[str]
    summarization_model: Optional[str]
    spacy_model: Optional[str]
    faiss_index_size: int
    total_metadata_entries: int

# Dependencias
def get_ai_service_dependency() -> AIService:
    return get_ai_service()

# Endpoints
@app.get("/")
async def root():
    """Endpoint raíz del servicio de IA"""
    return {
        "service": "AI Service - Repositorio UNEFA",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "process_pdf": "/process_pdf",
            "search": "/search",
            "similar": "/similar",
            "model_info": "/model_info"
        }
    }

@app.get("/health")
async def health_check():
    """Verificar estado del servicio"""
    try:
        service = get_ai_service()
        model_info = service.get_model_info()
        
        return {
            "status": "healthy",
            "timestamp": "2025-11-19T07:41:33Z",
            "models_loaded": model_info['embedding_model'] is not None,
            "vector_store_ready": model_info['faiss_index_size'] >= 0,
            "model_info": model_info
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service Unavailable")

@app.post("/process_pdf", response_model=ProcessResponse)
async def process_pdf(
    file: UploadFile = File(...),
    trabajo_id: str = "",
    service: AIService = Depends(get_ai_service_dependency)
):
    """
    Procesar PDF y extraer información
    """
    if not trabajo_id:
        raise HTTPException(status_code=400, detail="trabajo_id is required")
    
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Guardar archivo temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            pdf_path = tmp_file.name
        
        try:
            # Procesar PDF
            result = service.process_pdf_and_extract(pdf_path, trabajo_id)
            return ProcessResponse(**result)
            
        finally:
            # Limpiar archivo temporal
            os.unlink(pdf_path)
            
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@app.post("/search", response_model=List[SearchResult])
async def semantic_search(
    request: SearchRequest,
    service: AIService = Depends(get_ai_service_dependency)
):
    """
    Búsqueda semántica de trabajos
    """
    try:
        results = service.semantic_search(
            query=request.query,
            top_k=request.top_k
        )
        
        return [
            SearchResult(
                trabajo_id=result['trabajo_id'],
                metadata=result['metadata'],
                similarity_score=result['similarity_score'],
                reason=result['reason']
            )
            for result in results
        ]
        
    except Exception as e:
        logger.error(f"Error in semantic search: {e}")
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@app.post("/similar")
async def find_similar_trabajos(
    request: SimilarityRequest,
    service: AIService = Depends(get_ai_service_dependency)
):
    """
    Encontrar trabajos similares
    """
    try:
        similar_trabajos = service.find_similar_trabajos(
            trabajo_id=request.trabajo_id,
            top_k=request.top_k
        )
        
        return {
            "trabajo_id": request.trabajo_id,
            "similar_trabajos": similar_trabajos,
            "total_found": len(similar_trabajos)
        }
        
    except Exception as e:
        logger.error(f"Error finding similar trabajos: {e}")
        raise HTTPException(status_code=500, detail=f"Similarity search error: {str(e)}")

@app.get("/model_info", response_model=ModelInfoResponse)
async def get_model_info(
    service: AIService = Depends(get_ai_service_dependency)
):
    """
    Obtener información sobre los modelos de IA
    """
    try:
        model_info = service.get_model_info()
        return ModelInfoResponse(**model_info)
        
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        raise HTTPException(status_code=500, detail=f"Model info error: {str(e)}")

@app.post("/batch_process")
async def batch_process_trabajos(
    trabajos_data: List[Dict[str, Any]],
    service: AIService = Depends(get_ai_service_dependency)
):
    """
    Procesar múltiples trabajos en lote
    """
    try:
        results = service.batch_process_trabajos(trabajos_data)
        
        return {
            "total_processed": len(trabajos_data),
            "results": results,
            "successful": sum(1 for r in results if r.get('success', False))
        }
        
    except Exception as e:
        logger.error(f"Error in batch processing: {e}")
        raise HTTPException(status_code=500, detail=f"Batch processing error: {str(e)}")

@app.post("/rebuild_index")
async def rebuild_vector_index(
    service: AIService = Depends(get_ai_service_dependency)
):
    """
    Reconstruir índice vectorial (requiere autenticación en producción)
    """
    try:
        # En un entorno real, esto requeriría autenticación y acceso a la base de datos
        logger.info("Rebuilding vector index...")
        
        # Esta función requeriría acceso a todos los trabajos de la base de datos
        # Por simplicidad, retornamos información sobre el estado actual
        
        model_info = service.get_model_info()
        
        return {
            "status": "rebuilding",
            "current_index_size": model_info['faiss_index_size'],
            "message": "Index rebuild initiated. This would require database access in production."
        }
        
    except Exception as e:
        logger.error(f"Error rebuilding index: {e}")
        raise HTTPException(status_code=500, detail=f"Index rebuild error: {str(e)}")

# Manejo de excepciones globales
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": "2025-11-19T07:41:33Z"
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "timestamp": "2025-11-19T07:41:33Z"
        }
    )

if __name__ == "__main__":
    # Configuración para desarrollo
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )