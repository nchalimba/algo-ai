from datetime import datetime
from astrapy.constants import VectorMetric
from astrapy import DataAPIClient, Collection

from src.config.config import app_config

class VectorStore:
    def __init__(self):
        client = DataAPIClient()
        self.db = client.get_database(
            app_config.vector_db.api_endpoint,
            token=app_config.vector_db.application_token
        )

        self.collection: Collection = self.db.get_collection(app_config.vector_db.collection_name)
        if self.collection is None:
            self.collection = self.db.create_collection(
                app_config.vector_db.collection_name,
                dimension=3,
                metric=VectorMetric.COSINE,
            )

    def delete_embeddings(self, source_key: str):
        """
        Delete existing embeddings in the vector database for a specific source ID.
        """
        self.collection.delete_many({"source_key": source_key})
    
    def ping(self):
        """
        Ping the vector database to verify connectivity.
        """
        self.collection.find_one()
    
    def insert_embeddings(self, chunks, embeddings, source_key, source_label, type):
        """
        Insert new embeddings into the vector database with source metadata.
        """
        documents = [
            {
                "text": chunk,
                "$vector": embedding,
                "source_key": source_key,
                "source_label": source_label,
                "created_at": datetime.now().isoformat(),
                "type": type
            }
            for chunk, embedding in zip(chunks, embeddings)
        ]
        self.collection.insert_many(documents)

    def similarity_search(self, embedding, limit=10):
        return self.collection.find(
            {},
            sort={"$vector": embedding},
            limit=limit,
            include_similarity=True)