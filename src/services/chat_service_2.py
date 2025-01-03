from langchain_cohere import ChatCohere
from langchain_openai import OpenAI
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
        self.llm = self.get_llm()

    def get_llm(self):
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

    def retrieve(self, state: State):
        print("###########")
        print(state)
        # TODO: get embedding from question
        # TODO -> for that: create abstraction for embedding model
        # TODO -> generally: check if this structure can be improved
        # TODO: -> e.g. with dependency injection (vector strore and embedding model get init twice)
        # TODO: read chapter 2 for context
        # TODO: how to implement prompts? what is hub.pull?
        # TODO: how to really use similarity search?

        retrieved_docs = self.vector_store.similarity_search(state["question"])
        return {"context": retrieved_docs}
    
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