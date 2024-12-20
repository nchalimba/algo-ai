import hashlib
import tempfile
from astrapy.constants import VectorMetric
from astrapy import DataAPIClient, Collection
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_cohere import CohereEmbeddings
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.document_loaders import WebBaseLoader

from src.config.config import app_config, LLMProvider

class DocumentProcessor:
    def __init__(self):
        client = DataAPIClient()
        self.db = client.get_database(
            app_config.vector_db.api_endpoint,
            token=app_config.vector_db.application_token
        )

        self.collection: Collection
        self.collection = self.db.get_collection(app_config.vector_db.collection_name)
        if (self.collection is None):
            self.collection = self.db.create_collection(
                app_config.vector_db.collection_name,
                dimension=3,
                metric=VectorMetric.COSINE,
            )
        
        # Initialize embedding model
        self.embedding_model = self._get_embedding_model()
       
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=app_config.chunk_size, chunk_overlap=app_config.chunk_overlap
        )
    
    def generate_source_key(self, input_data: str) -> str:
        """
        Generate a unique source key by hashing the input data.
        """
        return hashlib.sha256(input_data.encode('utf-8')).hexdigest()

    def process_text(self, text: str, admin_input: str):
        """
        Process raw text: delete existing embeddings, generate new embeddings, and insert them.
        """
        source_key = self.generate_source_key(admin_input)
        self._delete_existing_embeddings(source_key)
        chunks = self.text_splitter.split_text(text)
        embeddings = self.embedding_model.embed_documents(chunks)
        self._insert_embeddings(chunks, embeddings, source_key, admin_input)

    def process_pdf(self, file_bytes: bytes, admin_input: str = None):
        """
        Process a PDF file: extract text, chunk, delete old embeddings, create new embeddings, and insert.
        """
        source_key = self.generate_source_key(admin_input)
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(file_bytes)
            temp_file_path = temp_file.name  # Get the file path of the temporary file
    
        loader = PyPDFLoader(temp_file_path)
        text = " ".join([doc.page_content for doc in loader.load()])
        
        # Process the text after extraction
        self.process_text_with_source_key(text, source_key, admin_input)

    def process_urls(self, urls: list):
        """
        Process a list of URLs: fetch text, chunk, delete old embeddings, create new embeddings, and insert.
        """
        for url in urls:
            source_key = self.generate_source_key(url)
            loader = WebBaseLoader(url)
            text = " ".join([doc.page_content for doc in loader.load()])
            self.process_text_with_source_key(text, source_key, url)

    def process_text_with_source_key(self, text: str, source_key: str, source_label: str):
        """
        Process text with a predefined source key and label.
        """
        self._delete_existing_embeddings(source_key)
        chunks = self.text_splitter.split_text(text)
        embeddings = self.embedding_model.embed_documents(chunks)
        self._insert_embeddings(chunks, embeddings, source_key, source_label)
    
    def _get_embedding_model(self):
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

    def _delete_existing_embeddings(self, source_key: str):
        """
        Delete existing embeddings in the vector database for a specific source ID.
        """
        self.collection.delete_many({"source_key": source_key})

    def _insert_embeddings(self, chunks, embeddings, source_key, source_label):
        """
        Insert new embeddings into the vector database with source metadata.
        """
        documents = [
            {
                "text": chunk,
                "$vector": embedding,
                "source_key": source_key,
                "source_label": source_label
            }
            for chunk, embedding in zip(chunks, embeddings)
        ]
        self.collection.insert_many(documents)
     