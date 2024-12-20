from pydantic import BaseModel
from enum import Enum
from dotenv import load_dotenv
import os

load_dotenv()

class LLMProvider(str, Enum):
    OPENAI = "OPENAI"
    COHERE = "COHERE"

class ChunkingStrategy(str, Enum):
    RECURSIVE = "RECURSIVE"
    FIXED_SIZE = "FIXED_SIZE"
    SEMANTIC = "SEMANTIC"
  

class RAGModelConfig(BaseModel):
    name: str = "dsa_rag"
    chunk_size: int = 512

class VectorDBConfig(BaseModel):
    collection_name: str = os.getenv("ASTRA_DB_COLLECTION_NAME", "dsa_rag_vectors")
    api_endpoint: str = os.getenv("ASTRA_DB_API_ENDPOINT")
    application_token: str = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
    keyspace: str = os.getenv("ASTRA_DB_KEYSPACE", "default_keyspace")
    vector_dimension: int = 1024

class ModelApiConfig(BaseModel):
    llm_provider: LLMProvider = LLMProvider(os.getenv("LLM_PROVIDER", "COHERE"))
    api_key: str = os.getenv("COHERE_API_KEY" if llm_provider == LLMProvider.COHERE else "OPENAI_API_KEY")
    embedding_model: str = "embed-english-v3.0"
    llm_model: str = "command-r7b-12-2024"

class Config(BaseModel):
    vector_db: VectorDBConfig = VectorDBConfig()
    model: ModelApiConfig = ModelApiConfig()
    chunk_size: int = 512
    chunk_overlap: int = 20

app_config = Config()
