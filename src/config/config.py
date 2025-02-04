from pydantic import BaseModel
from enum import Enum
from dotenv import load_dotenv
import os

load_dotenv()

#PROMPTS:
NO_INFO_RESPONSE = "I apologize, but I don't have enough relevant information in my knowledge base to provide an accurate answer to your question. Please feel free to rephrase your question or ask about a different topic."
SYSTEM_PROMPT = """
    You are an AI assistant specialized in question-answering data structures and algorithms.
    Please answer without any introductory sentence about your decision-making process.
    Provide answers that are accurate, well-structured, and professional. Also provide code examples if appropriate. 
    Please use markdown to format your responses. For code snippets, use the ``` syntax and use javascript.
"""
SYSTEM_PROMPT_GENERATE = SYSTEM_PROMPT + """
    Your responses must be strictly based on the provided retrieved context. 
    Do not include information or assumptions outside the provided context.
    If the context does not contain sufficient information to answer the question, respond with:
    """ + NO_INFO_RESPONSE + """
    Context for this task:
    {docs_content}
"""

class LLMProvider(str, Enum):
    OPENAI = "OPENAI"
    COHERE = "COHERE"

class ChunkingStrategy(str, Enum):
    RECURSIVE = "RECURSIVE"
    FIXED_SIZE = "FIXED_SIZE"
    SEMANTIC = "SEMANTIC"

class VectorDBConfig(BaseModel):
    collection_name: str = os.getenv("ASTRA_DB_COLLECTION_NAME", "dsa_rag_vectors")
    api_endpoint: str = os.getenv("ASTRA_DB_API_ENDPOINT")
    application_token: str = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
    keyspace: str = os.getenv("ASTRA_DB_KEYSPACE", "default_keyspace")
    vector_dimension: int = 1024

class ModelConfig(BaseModel):
    llm_provider: LLMProvider = LLMProvider(os.getenv("LLM_PROVIDER", "COHERE"))
    api_key: str = os.getenv("COHERE_API_KEY" if llm_provider == LLMProvider.COHERE else "OPENAI_API_KEY")
    embedding_model: str = "embed-english-v3.0"
    llm_model: str = "command-r-plus-08-2024"

class PostgresConfig(BaseModel):
    uri: str = os.getenv("POSTGRES_CONNECTION_STRING")
    max_pool_size: int = 20
    autocommit: bool = True
    prepare_threshold: int = 0

class InfoConfig(BaseModel):
    title: str = "DSA RAG API"
    description: str = "A RAG system for answering questions about Data Structures and Algorithms"
    version: str = "1.0.0"

class AdminConfig(BaseModel):
    api_key: str = os.getenv("ADMIN_API_KEY")
    jwt_secret: str = os.getenv("JWT_SECRET")
    jwt_expiration: int = 3600  # 1 hour

class Config(BaseModel):
    vector_db: VectorDBConfig = VectorDBConfig()
    postgres: PostgresConfig = PostgresConfig()
    model: ModelConfig = ModelConfig()
    info: InfoConfig = InfoConfig()
    admin: AdminConfig = AdminConfig()
    chunk_size: int = 512
    chunk_overlap: int = 20
    port: int = int(os.getenv("PORT", 10000))


app_config = Config()
