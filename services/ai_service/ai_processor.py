import os
import sys
import json
import pickle
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

import PyPDF2
import pdfplumber
import nltk
import spacy
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from sklearn.metrics.pairwise import cosine_similarity
import faiss
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
except:
    logger.warning("NLTK downloads failed, some features may not work")

# Load spaCy model
try:
    nlp = spacy.load("es_core_news_sm")
except OSError:
    logger.warning("Spanish spaCy model not found. Install with: python -m spacy download es_core_news_sm")
    nlp = None

class AIService:
    """
    Servicio de IA para procesamiento de documentos y búsqueda semántica
    """
    
    def __init__(self):
        self.setup_models()
        self.setup_vector_store()
        
    def setup_models(self):
        """Configurar modelos de IA"""
        try:
            # Modelo para embeddings (en español)
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Sentence transformer model loaded successfully")
            
            # Modelo para resumen (BART en español o T5)
            try:
                self.summarizer = pipeline(
                    "summarization", 
                    model="facebook/mbart-large-50-many-to-many-mmt"
                )
            except:
                # Fallback a modelo en inglés
                self.summarizer = pipeline(
                    "summarization",
                    model="facebook/bart-large-cnn"
                )
            logger.info("Summarization model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading AI models: {e}")
            self.embedding_model = None
            self.summarizer = None
    
    def setup_vector_store(self):
        """Configurar almacenamiento vectorial"""
        try:
            # Crear directorio para vector store
            self.vector_store_dir = Path("vector_store")
            self.vector_store_dir.mkdir(exist_ok=True)
            
            # Cargar índices existentes
            self.load_vector_indexes()
            
        except Exception as e:
            logger.error(f"Error setting up vector store: {e}")
    
    def load_vector_indexes(self):
        """Cargar índices vectoriales existentes"""
        try:
            # Índice FAISS para búsqueda rápida
            index_path = self.vector_store_dir / "faiss_index.bin"
            metadata_path = self.vector_store_dir / "metadata.json"
            
            if index_path.exists():
                self.faiss_index = faiss.read_index(str(index_path))
                logger.info(f"FAISS index loaded with {self.faiss_index.ntotal} vectors")
            else:
                # Crear nuevo índice FAISS
                dimension = 384  # Dimensión del modelo all-MiniLM-L6-v2
                self.faiss_index = faiss.IndexFlatIP(dimension)  # Inner Product for cosine similarity
                logger.info("New FAISS index created")
            
            # Cargar metadatos
            if metadata_path.exists():
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    self.index_metadata = json.load(f)
            else:
                self.index_metadata = {}
                
        except Exception as e:
            logger.error(f"Error loading vector indexes: {e}")
            self.faiss_index = None
            self.index_metadata = {}
    
    def save_vector_indexes(self):
        """Guardar índices vectoriales"""
        try:
            if self.faiss_index is not None:
                faiss.write_index(self.faiss_index, str(self.vector_store_dir / "faiss_index.bin"))
                
                with open(self.vector_store_dir / "metadata.json", 'w', encoding='utf-8') as f:
                    json.dump(self.index_metadata, f, ensure_ascii=False, indent=2)
                    
                logger.info("Vector indexes saved successfully")
                
        except Exception as e:
            logger.error(f"Error saving vector indexes: {e}")
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extraer texto de un archivo PDF
        """
        text = ""
        
        try:
            # Método principal con pdfplumber (mejor para PDFs académicos)
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            # Si pdfplumber falla, usar PyPDF2 como fallback
            if not text or len(text.strip()) < 100:
                text = ""
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            
            logger.info(f"Extracted {len(text)} characters from PDF: {pdf_path}")
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF {pdf_path}: {e}")
            return ""
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocesar texto para análisis
        """
        if not text:
            return ""
        
        # Limpiar texto
        import re
        
        # Remover caracteres especiales pero mantener acentos
        text = re.sub(r'[^\w\s\-\.]', ' ', text)
        
        # Normalizar espacios
        text = re.sub(r'\s+', ' ', text)
        
        # Convertir a minúsculas
        text = text.lower().strip()
        
        # Procesamiento con spaCy si está disponible
        if nlp:
            doc = nlp(text)
            # Filtrar stopwords y lematizar
            tokens = [
                token.lemma_ for token in doc 
                if not token.is_stop and not token.is_punct and token.is_alpha
            ]
            text = ' '.join(tokens)
        
        return text
    
    def extract_structured_info(self, text: str, pdf_path: str) -> Dict[str, Any]:
        """
        Extraer información estructurada del texto según el formato de la universidad
        """
        info = {
            'titulo': '',
            'autores': '',
            'tutores': '',
            'año': '',
            'objetivos': '',
            'resumen': '',
            'carrera': '',
            'tipo_trabajo': ''
        }
        
        try:
            # Patrones para extraer información (basados en formato estándar)
            lines = text.split('\n')
            
            # Buscar título (generalmente en las primeras líneas)
            for i, line in enumerate(lines[:10]):
                line = line.strip()
                if len(line) > 10 and len(line) < 300:
                    if not any(word in line.lower() for word in ['universidad', 'trabajo', 'grado', 'pasantia']):
                        info['titulo'] = line
                        break
            
            # Buscar autores (patrón común en trabajos académicos)
            for line in lines:
                if any(word in line.lower() for word in ['autor', 'estudiante', 'presentado por']):
                    # Buscar en las siguientes líneas los nombres
                    continue
            
            # Buscar año (formato YYYY)
            import re
            year_pattern = r'\b(19|20)\d{2}\b'
            years = re.findall(year_pattern, text)
            if years:
                info['año'] = years[0] + (years[1] if len(years) > 1 else '')
            
            # Buscar objetivos (sección típica)
            objectives_start = False
            for line in lines:
                line_lower = line.lower()
                if any(phrase in line_lower for phrase in ['objetivo', 'propósito', 'meta']):
                    objectives_start = True
                    continue
                
                if objectives_start and line.strip():
                    info['objetivos'] += line + ' '
                    
                if objectives_start and len(info['objetivos']) > 500:
                    break
            
            # Determinar carrera basado en palabras clave
            carreras_keywords = {
                'ingenieria_naval': ['naval', 'buque', 'marítimo', 'barco'],
                'ingenieria_sistemas': ['sistema', 'software', 'programación', 'tecnología'],
                'ingenieria_petroquimica': ['petroquímica', 'petróleo', 'química', 'refinería'],
                'tsu_enfermeria': ['enfermería', 'salud', 'paciente', 'médico'],
                'tsu_turismo': ['turismo', 'hotel', 'viaje', 'recreación'],
                'licenciatura_economia_social': ['economía', 'social', 'comunidad', 'desarrollo']
            }
            
            text_lower = text.lower()
            for carrera, keywords in carreras_keywords.items():
                if any(keyword in text_lower for keyword in keywords):
                    info['carrera'] = carrera
                    break
            
            # Determinar tipo de trabajo
            if any(word in text_lower for word in ['especial de grado', 'proyecto especial']):
                info['tipo_trabajo'] = 'especial_grado'
            elif any(word in text_lower for word in ['práctica', 'pasantia', 'profesional']):
                info['tipo_trabajo'] = 'practicas_profesionales'
            
            # Generar resumen usando IA
            if self.summarizer:
                try:
                    # Tomar primeros 1000 caracteres para el resumen
                    summary_input = text[:1000]
                    if len(summary_input) > 100:
                        summary = self.summarizer(summary_input, max_length=150, min_length=50, do_sample=False)
                        info['resumen'] = summary[0]['summary_text']
                except Exception as e:
                    logger.warning(f"Error generating summary: {e}")
            
            logger.info(f"Extracted structured info: {list(info.keys())}")
            
        except Exception as e:
            logger.error(f"Error extracting structured info: {e}")
        
        return info
    
    def generate_embedding(self, text: str) -> Optional[np.ndarray]:
        """
        Generar embedding del texto
        """
        if not self.embedding_model or not text:
            return None
        
        try:
            # Preprocesar texto
            clean_text = self.preprocess_text(text)
            
            if not clean_text:
                return None
            
            # Generar embedding
            embedding = self.embedding_model.encode(clean_text, convert_to_numpy=True)
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None
    
    def add_to_vector_store(self, trabajo_id: str, text: str, metadata: Dict[str, Any]):
        """
        Agregar trabajo al almacén vectorial
        """
        try:
            # Generar embedding
            embedding = self.generate_embedding(text)
            
            if embedding is None:
                logger.error(f"Could not generate embedding for trabajo {trabajo_id}")
                return False
            
            # Normalizar embedding para similitud coseno
            embedding = embedding / np.linalg.norm(embedding)
            
            # Agregar al índice FAISS
            embedding_2d = embedding.reshape(1, -1)
            self.faiss_index.add(embedding_2d)
            
            # Guardar metadatos
            self.index_metadata[str(len(self.index_metadata))] = {
                'trabajo_id': trabajo_id,
                'embedding_id': len(self.index_metadata),
                'metadata': metadata
            }
            
            logger.info(f"Added trabajo {trabajo_id} to vector store")
            return True
            
        except Exception as e:
            logger.error(f"Error adding to vector store: {e}")
            return False
    
    def semantic_search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Búsqueda semántica usando embeddings
        """
        try:
            if not self.embedding_model or self.faiss_index is None:
                logger.warning("Vector search not available, using text search")
                return self.text_search_fallback(query, top_k)
            
            # Generar embedding de la consulta
            query_embedding = self.generate_embedding(query)
            
            if query_embedding is None:
                return []
            
            # Normalizar embedding
            query_embedding = query_embedding / np.linalg.norm(query_embedding)
            query_embedding_2d = query_embedding.reshape(1, -1)
            
            # Realizar búsqueda en el índice FAISS
            similarities, indices = self.faiss_index.search(query_embedding_2d, min(top_k, self.faiss_index.ntotal))
            
            # Preparar resultados
            results = []
            for similarity, idx in zip(similarities[0], indices[0]):
                if idx < len(self.index_metadata):
                    # Buscar metadatos por embedding_id
                    metadata = None
                    for key, value in self.index_metadata.items():
                        if value.get('embedding_id') == idx:
                            metadata = value
                            break
                    
                    if metadata:
                        results.append({
                            'trabajo_id': metadata['trabajo_id'],
                            'metadata': metadata['metadata'],
                            'similarity_score': float(similarity),
                            'reason': self._generate_search_reason(query, metadata['metadata'])
                        })
            
            return results
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return self.text_search_fallback(query, top_k)
    
    def text_search_fallback(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Búsqueda por texto como fallback
        """
        try:
            # Aquí se integraría con la base de datos Django
            # Por ahora, retornar resultado vacío
            logger.info("Using text search fallback")
            return []
            
        except Exception as e:
            logger.error(f"Error in text search fallback: {e}")
            return []
    
    def _generate_search_reason(self, query: str, metadata: Dict[str, Any]) -> str:
        """
        Generar explicación de por qué el trabajo es relevante para la búsqueda
        """
        try:
            title = metadata.get('titulo', '')
            summary = metadata.get('resumen', '')
            objectives = metadata.get('objetivos', '')
            
            # Buscar coincidencias en palabras clave
            query_words = query.lower().split()
            matches = []
            
            for field in [title, summary, objectives]:
                field_lower = field.lower()
                for word in query_words:
                    if word in field_lower:
                        matches.append(word)
            
            if matches:
                return f"Coincide con las palabras clave: {', '.join(set(matches))}"
            else:
                return "Contenido relacionado encontrado por búsqueda semántica"
                
        except Exception as e:
            logger.error(f"Error generating search reason: {e}")
            return "Relevancia determinada por IA"
    
    def find_similar_trabajos(self, trabajo_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Encontrar trabajos similares a uno existente
        """
        try:
            if not self.embedding_model or self.faiss_index is None:
                logger.warning("Vector search not available")
                return []
            
            # Obtener embedding del trabajo (esto requeriría acceso a la base de datos)
            # Por simplicidad, retornamos resultado vacío
            logger.info(f"Finding similar trabajos to {trabajo_id}")
            return []
            
        except Exception as e:
            logger.error(f"Error finding similar trabajos: {e}")
            return []
    
    def process_pdf_and_extract(self, pdf_path: str, trabajo_id: str) -> Dict[str, Any]:
        """
        Procesar PDF y extraer toda la información
        """
        try:
            logger.info(f"Processing PDF: {pdf_path} for trabajo {trabajo_id}")
            
            # Extraer texto
            text = self.extract_text_from_pdf(pdf_path)
            
            if not text:
                return {'error': 'No se pudo extraer texto del PDF'}
            
            # Generar hash para detectar duplicados
            file_hash = hashlib.md5(text.encode()).hexdigest()
            
            # Extraer información estructurada
            structured_info = self.extract_structured_info(text, pdf_path)
            
            # Agregar al vector store
            self.add_to_vector_store(trabajo_id, text, structured_info)
            
            # Guardar índices
            self.save_vector_indexes()
            
            result = {
                'success': True,
                'trabajo_id': trabajo_id,
                'file_hash': file_hash,
                'content_length': len(text),
                'structured_info': structured_info,
                'embedding_generated': True
            }
            
            logger.info(f"Successfully processed PDF for trabajo {trabajo_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            return {
                'success': False,
                'error': str(e),
                'trabajo_id': trabajo_id
            }
    
    def batch_process_trabajos(self, trabajos_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Procesar múltiples trabajos en lote
        """
        results = []
        
        for trabajo_data in trabajos_data:
            result = self.process_pdf_and_extract(
                trabajo_data['pdf_path'],
                trabajo_data['trabajo_id']
            )
            results.append(result)
        
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Obtener información sobre los modelos cargados
        """
        return {
            'embedding_model': 'all-MiniLM-L6-v2' if self.embedding_model else None,
            'summarization_model': 'facebook/mbart-large-50-many-to-many-mmt' if self.summarizer else None,
            'spacy_model': 'es_core_news_sm' if nlp else None,
            'faiss_index_size': self.faiss_index.ntotal if self.faiss_index else 0,
            'total_metadata_entries': len(self.index_metadata)
        }

# Función para crear instancia global del servicio
_ai_service_instance = None

def get_ai_service() -> AIService:
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = AIService()
    return _ai_service_instance

if __name__ == "__main__":
    # Test del servicio
    service = get_ai_service()
    info = service.get_model_info()
    print(f"AI Service Info: {json.dumps(info, indent=2)}")