from langchain_cohere import CohereEmbeddings
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_cohere import ChatCohere
from langchain_openai import OpenAI

from src.config.config import app_config, LLMProvider

class ModelProvider:
    def __init__(self):
        self.llm = None
        self.embedding_model = self._get_embedding_model()
    
    def _get_embedding_model(self):
        # Embedding model initialization based on the provider (Cohere or OpenAI)
        if app_config.model.llm_provider == LLMProvider.OPENAI:
            return OpenAIEmbeddings(
                api_key=app_config.model.api_key,
                model=app_config.model.embedding_model
            )
        else:
            return CohereEmbeddings(
                cohere_api_key=app_config.model.api_key,
                model=app_config.model.embedding_model
            )
        
    def _get_llm(self):
        # LLM initialization based on the provider (Cohere or OpenAI)
        if app_config.model.llm_provider == LLMProvider.OPENAI:
            return OpenAI(
                api_key=app_config.model.api_key,
                model=app_config.model.llm_model
            )
        else:
            return ChatCohere(
                cohere_api_key=app_config.model.api_key,
                model=app_config.model.llm_model
            )