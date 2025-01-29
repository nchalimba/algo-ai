from src.config.config import app_config
from src.services.vector_store import VectorStore

class InfoService:
    def __init__(self):
        self.vector_store = VectorStore()

    def get_config_values(self):
        return {
            "llm_provider": app_config.model.llm_provider,
            "llm": app_config.model.llm_model,
            "embedding_model": app_config.model.embedding_model,
            "rag_version": app_config.info.version,
            "chunk_size": app_config.chunk_size,
            "chunk_overlap": app_config.chunk_overlap,
            "vector_dimension": app_config.vector_db.vector_dimension,
            "sources": self.vector_store.get_distinct_sources()
        }
