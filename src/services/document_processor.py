import hashlib
import tempfile
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_cohere import CohereEmbeddings
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.document_loaders import WebBaseLoader

from src.config.config import app_config, LLMProvider
from src.services.vector_store import VectorStore

import time
import logging

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        self.vector_store = VectorStore()
        
        # Initialize embedding model
        self.embedding_model = self._get_embedding_model()
       
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=app_config.chunk_size, chunk_overlap=app_config.chunk_overlap
        )
    
    def _generate_source_key(self, input_data: str) -> str:
        """
        Generate a unique source key by hashing the input data.
        """
        return hashlib.sha256(input_data.encode('utf-8')).hexdigest()

    def process_text(self, text: str, title: str):
        """
        Process raw text: delete existing embeddings, generate new embeddings, and insert them.
        """
        source_key = self._generate_source_key(title)
        self.vector_store.delete_embeddings(source_key)
        text = self._clean_text(text)
        chunks = self.text_splitter.split_text(text)
        embeddings = self._create_embeddings(chunks)
        self.vector_store.insert_embeddings(chunks, embeddings, source_key, title, "text")

    def process_pdf(self, file_bytes: bytes, title: str):
        """
        Process a PDF file: extract text, chunk, delete old embeddings, create new embeddings, and insert.
        """
        source_key = self._generate_source_key(title)
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(file_bytes)
            temp_file_path = temp_file.name  # Get the file path of the temporary file
    
        loader = PyPDFLoader(temp_file_path)
        text = " ".join([doc.page_content for doc in loader.load()])
        
        # Process the text after extraction
        self._process_text_with_source_key(text, source_key, title, "pdf")

    def process_urls(self, urls: list):
        """
        Process a list of URLs: fetch text, chunk, delete old embeddings, create new embeddings, and insert.
        """
        for url in urls:
            source_key = self._generate_source_key(url)
            loader = WebBaseLoader(url)
            text = " ".join([doc.page_content for doc in loader.load()])
            self._process_text_with_source_key(text, source_key, url, "url")

    def _process_text_with_source_key(self, text: str, source_key: str, source_label: str, type: str):
        """
        Process text with a predefined source key and label.
        """
        self.vector_store.delete_embeddings(source_key)
        text = self._clean_text(text)
        chunks = self.text_splitter.split_text(text)
        embeddings = self._create_embeddings(chunks)
        self.vector_store.insert_embeddings(chunks, embeddings, source_key, source_label, type)

    def _create_embeddings(self, chunks: list):
        # split these into batches
        # reason: trial token rate limit exceeded, limit is 100000 tokens per minute

        '''
        Math:
        100_000 tokens -> how many words?
        100_000 / 3 -> 33_333 words
        chunk size = 512 -> 65 chunks

        --> after 65 chunks, wait for 1 minute


        '''
        logger.info("Creating embeddings. Chunks: %s", len(chunks))
        CHUNK_LIMIT = 700
        embeddings = []
        for i in range(0, len(chunks), CHUNK_LIMIT):
            batch = chunks[i:i + CHUNK_LIMIT]
            embeddings_batch = self.embedding_model.embed_documents(batch)
            embeddings.extend(embeddings_batch)
            logger.info("Created embeddings for chunks %s of %s", i + CHUNK_LIMIT, len(chunks))
            if i + CHUNK_LIMIT < len(chunks):
                time.sleep(60)  # wait for 1 minute if there are more chunks
        return embeddings
    
    def _clean_text(self, text):
        '''
        Remove extra whitespaces and newlines
        '''
        text = re.sub(r'\s+', ' ', text)  
        return text.strip()

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
     