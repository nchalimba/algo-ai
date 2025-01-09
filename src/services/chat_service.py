from langchain_cohere import ChatCohere
from langchain_openai import OpenAI
from langchain_cohere import CohereEmbeddings
from langchain_community.embeddings import OpenAIEmbeddings
from langgraph.graph import START, StateGraph
from langchain import hub
from langchain_core.documents import Document
from typing_extensions import List, TypedDict

from src.services.vector_store import VectorStore
from src.config.config import LLMProvider, app_config

class State(TypedDict):
    question: str
    context: List[Document]
    answer: str


class ChatService:
    def __init__(self):
        self.vector_store = VectorStore()
        self.prompt = hub.pull("rlm/rag-prompt")
        self.llm = self._get_llm()
        self.embedding_model = self._get_embedding_model()

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

    def retrieve(self, state: State):
        embedding = self.embedding_model.embed_query(state["question"])
        # TODO -> generally: improve structure
        # TODO: -> e.g. with dependency injection (vector strore and embedding model get init twice)
        # TODO: include service

        rows = self.vector_store.similarity_search(embedding, limit=10)
        context: List[Document] = []
        for row in rows:
            document = Document(
                page_content=row["text"],
                metadata={
                    "source_key": row["source_key"],
                    "source_label": row["source_label"]
                }
            )
            context.append(document)
        return {"context": context}
    
    def generate(self, state: State):
        docs_content = "\n\n".join(doc.page_content for doc in state["context"])
        messages = self.prompt.invoke({"question": state["question"], "context": docs_content})
        response = self.llm.invoke(messages)
        return {"answer": response.content}
    
    def ask_question(self, question: str):
        graph_builder = StateGraph(State).add_sequence([self.retrieve, self.generate])
        graph_builder.add_edge(START, "retrieve")
        graph = graph_builder.compile()
        response = graph.invoke({"question": question})
        return response