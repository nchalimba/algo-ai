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
    Please always use the tools provided to answer the question. Do not answer directly without using a tool.
    If you cannot answer the question by using the tools provided, respond with:
    """ + NO_INFO_RESPONSE + """
"""
SYSTEM_PROMPT_GENERATE = SYSTEM_PROMPT + """
    Your responses must be based on the provided retrieved context. 
    Do not include information or assumptions outside the provided context.
    Context for this task:
    {docs_content}
"""

class LLMProvider(str, Enum):
    OPENAI = "OPENAI"
    COHERE = "COHERE"
    GEMINI = "GEMINI"

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

def get_llm_model(llm_provider: LLMProvider):
    if llm_provider == LLMProvider.GEMINI:
        return "gemini-2.0-flash"
    elif llm_provider == LLMProvider.COHERE:
        return "command-r-plus"
    else:
        return "gpt-4-turbo"

class ModelConfig(BaseModel):
    llm_provider: LLMProvider = LLMProvider(os.getenv("LLM_PROVIDER", "COHERE"))
    
    @property
    def api_key(self) -> str:
        key_map = {
            LLMProvider.GEMINI: "GOOGLE_API_KEY",
            LLMProvider.COHERE: "COHERE_API_KEY",
            LLMProvider.OPENAI: "OPENAI_API_KEY"
        }
        return os.getenv(key_map[self.llm_provider], "")
    
    embedding_model: str = "embed-english-v3.0"
    embedding_api_key: str = os.getenv("COHERE_API_KEY", "")
    llm_model: str = get_llm_model(llm_provider)

class PostgresConfig(BaseModel):
    uri: str = os.getenv("POSTGRES_CONNECTION_STRING")
    max_pool_size: int = 20
    autocommit: bool = True
    prepare_threshold: int = 0

class InfoConfig(BaseModel):
    title: str = "AlgoAI API"
    description: str = "Official Swagger documentation for the AlgoAI API, a RAG system for answering questions about Data Structures and Algorithms."
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
