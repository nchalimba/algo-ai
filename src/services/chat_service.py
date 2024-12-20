from langchain_cohere import ChatCohere
from langchain_openai import OpenAI
from langchain.chains import create_history_aware_retriever
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.config.config import LLMProvider, app_config
from src.services.document_processor import DocumentProcessor
from src.models.request_models import QuestionRequest
import traceback
from fastapi import HTTPException

# Custom prompt templates
CUSTOM_PROMPT_TEMPLATE = """
You are a friendly virtual assistant called RagBot that serves as an example for a chatbot with retrieval augmented generation.

Always be polite.
Use simple language.

If you cannot answer the question from the context, just say so and do not answer it at all.
Do not make up answers but rather ask for clarification.

Context: {context}
"""

CONTEXTUALIZE_SYSTEM_PROMPT = """
Given a chat history and the latest user question
which might reference context in the chat history, formulate a standalone question
which can be understood without the chat history. Do NOT answer the question,
just reformulate it if needed and otherwise return it as is.
"""

class ChatService:
    def __init__(self, temperature: float = 0.01, k: int = 6):
        self.client = self.get_llm()
        self.temperature = temperature
        self.k = k
        self.document_processor = DocumentProcessor()
        self._retrieval_chain = self._build_retrieval_chain()

    def _build_retrieval_chain(self):
        # Create the retrieval chain using the custom prompts
        contextualize_prompt = ChatPromptTemplate(
            [
                ("system", CONTEXTUALIZE_SYSTEM_PROMPT),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )

        history_aware_retriever = create_history_aware_retriever(
            self.client,
            self.document_processor.collection.as_retriever(k=self.k),
            contextualize_prompt
        )

        main_prompt = ChatPromptTemplate(
            [
                ("system", CUSTOM_PROMPT_TEMPLATE),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )

        return create_retrieval_chain(
            history_aware_retriever,
            create_stuff_documents_chain(self.client, main_prompt)
        )

    def ask_question(self, question: str, history: list[dict[str, any]]):
        try:
            memory = self._build_history(history)
            result = self._retrieval_chain.invoke({
                "input": question,
                "chat_history": memory
            })
            return {
                "question": question,
                "answer": result['answer'],
                "context": result['context']
            }
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

    def _build_history(self, custom_memory: list[dict[str, any]]) -> list[BaseMessage]:
        history = []
        for elem in custom_memory:
            history.append(HumanMessage(elem["question"]))
            history.append(AIMessage(elem["answer"]))
        return history

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
