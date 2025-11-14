"""
Preprocessing module for RAG Pipeline.
Handles data preprocessing and database operations.
"""

from typing import List, Dict, Any, Optional
import psycopg2
from elasticsearch import Elasticsearch, helpers
import ujson
import numpy as np
import config
from embedding import EmbeddingGenerator


class DataPreprocessor:
    """
    Preprocess data and import into PostgreSQL and Elasticsearch.
    """
    
    def __init__(self):
        """
        Initialize preprocessor with database connections.
        """
        self.pg_config = config.PG_CONFIG
        self.es_config = config.ES_CONFIG
        self.embedding_gen = EmbeddingGenerator()
    
    def get_pg_connection(self):
        """
        Get PostgreSQL connection.
        
        Returns:
            PostgreSQL connection object
        """
        return psycopg2.connect(
            dbname=self.pg_config["dbname"],
            user=self.pg_config["user"],
            password=self.pg_config["password"],
            host=self.pg_config["host"],
            port=self.pg_config["port"]
        )
    
    def get_es_connection(self):
        """
        Get Elasticsearch connection.
        
        Returns:
            Elasticsearch client
        """
        return Elasticsearch(
            self.es_config["host"],
            api_key=self.es_config["api_key"],
            ca_certs=self.es_config["ca_certs"]
        )
    
    def create_es_index(self, index_name: Optional[str] = None, force_recreate: bool = False):
        """
        Create Elasticsearch index with proper mappings.
        
        Args:
            index_name: Index name (defaults to config)
            force_recreate: Whether to delete existing index
        """
        index_name = index_name or self.es_config["index_name"]
        es = self.get_es_connection()
        
        # Delete existing index if needed
        if force_recreate and es.indices.exists(index=index_name):
            es.indices.delete(index=index_name)
            print(f"🧹 Deleted existing index: {index_name}")
        
        # Create index
        if not es.indices.exists(index=index_name):
            es.indices.create(
                index=index_name,
                mappings={
                    "properties": {
                        "id": {"type": "keyword"},
                        "category": {"type": "keyword"},
                        "source": {"type": "keyword"},
                        "content": {"type": "text"},
                        "embedding": {
                            "type": "dense_vector",
                            "dims": config.OPENAI_CONFIG["embedding_dim"],
                            "index": True,
                            "similarity": "cosine"
                        }
                    }
                }
            )
            print(f"✅ Created index: {index_name}")
        else:
            print(f"ℹ️  Index already exists: {index_name}")
    
    def import_from_postgres_to_elasticsearch(
        self,
        batch_size: int = 1000,
        index_name: Optional[str] = None
    ):
        """
        Import data from PostgreSQL to Elasticsearch with embeddings.
        
        Args:
            batch_size: Batch size for bulk operations
            index_name: Index name (defaults to config)
        """
        index_name = index_name or self.es_config["index_name"]
        es = self.get_es_connection()
        
        # Get PostgreSQL connection
        pg_conn = self.get_pg_connection()
        pg_cur = pg_conn.cursor(name="kb_cursor")
        pg_cur.itersize = batch_size
        pg_cur.execute("SELECT id, category, content, embedding, source FROM knowledge_base;")
        
        actions = []
        count = 0
        
        print("📥 Starting data import...")
        
        for row in pg_cur:
            _id, category, content, embedding_str, source = row
            
            # Parse embedding from JSON string
            emb = ujson.loads(embedding_str)
            v = np.array(emb, dtype=np.float32)
            
            # Normalize embedding
            if config.DATA_CONFIG["embedding_normalize"]:
                v = v / (np.linalg.norm(v) + 1e-12)
            
            # Prepare action
            actions.append({
                "_op_type": "index",
                "_index": index_name,
                "_id": str(_id),
                "id": str(_id),
                "category": category.lower() if category else None,
                "content": content,
                "source": source,
                "embedding": v.tolist()
            })
            
            # Bulk insert when batch is full
            if len(actions) >= batch_size:
                helpers.bulk(es, actions)
                count += len(actions)
                print(f"📥 Imported {count} documents")
                actions.clear()
        
        # Process remaining
        if actions:
            helpers.bulk(es, actions)
            count += len(actions)
        
        pg_cur.close()
        pg_conn.close()
        
        print(f"✅ Import completed. Total: {count} documents")

