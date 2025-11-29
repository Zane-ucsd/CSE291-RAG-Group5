"""
Retrieval module for RAG Pipeline.
Handles vector search and hybrid search in Elasticsearch.
"""

from typing import List, Dict, Any, Optional
from elasticsearch import Elasticsearch
from ..config import ES_CONFIG, RETRIEVAL_CONFIG
from ..utils import normalize_category


class Retriever:
    """
    Retrieve relevant documents from Elasticsearch using vector and/or keyword search.
    """
    
    def __init__(self, es_config: Optional[Dict[str, Any]] = None):
        """
        Initialize retriever with Elasticsearch connection.
        
        Args:
            es_config: Elasticsearch configuration (defaults to config.ES_CONFIG)
        """
        es_config = es_config or ES_CONFIG
        
        # Build connection parameters
        es_params = {"hosts": [es_config["host"]]}
        
        # Add optional auth parameters if present
        if "api_key" in es_config:
            es_params["api_key"] = es_config["api_key"]
        if "ca_certs" in es_config:
            es_params["ca_certs"] = es_config["ca_certs"]
        
        self.es = Elasticsearch(**es_params)
        self.index_name = es_config["index_name"]
        self.top_k = RETRIEVAL_CONFIG["top_k"]
        self.num_candidates = RETRIEVAL_CONFIG["num_candidates"]
        self.use_hybrid = RETRIEVAL_CONFIG["use_hybrid"]
        self.category_filter = RETRIEVAL_CONFIG["category_filter"]
    
    def vector_search(
        self,
        query_vector: List[float],
        category: Optional[str] = None,
        k: Optional[int] = None,
        num_candidates: Optional[int] = None,
        source_fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform vector similarity search using knn (ES 8.x optimized).
        
        Args:
            query_vector: Query embedding vector
            category: Optional category filter
            k: Number of results to return
            num_candidates: Number of candidates to consider
            source_fields: Fields to return in results
            
        Returns:
            List of search results
        """
        if source_fields is None:
            source_fields = ["id", "category", "source", "content"]
        
        k = k or self.top_k
        num_candidates = num_candidates or self.num_candidates
        
        # Build filters
        filters = []
        if category and self.category_filter:
            category = normalize_category(category)
            filters.append({"term": {"category": category}})
        
        # Build KNN query (ES 8.x)
        knn_query = {
            "field": "embedding",
            "query_vector": query_vector,
            "k": k,
            "num_candidates": num_candidates
        }
        
        if filters:
            knn_query["filter"] = {"bool": {"filter": filters}}
        
        # Execute search
        resp = self.es.search(
            index=self.index_name,
            size=k,
            knn=knn_query,
            _source=source_fields
        )
        
        return resp["hits"]["hits"]
    
    def hybrid_search(
        self,
        query_vector: List[float],
        query_text: str,
        category: Optional[str] = None,
        k: Optional[int] = None,
        num_candidates: Optional[int] = None,
        source_fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search (vector + BM25 keyword search) for ES 8.x.
        Uses native knn with query combination for optimal performance.
        
        Args:
            query_vector: Query embedding vector
            query_text: Query text for keyword search
            category: Optional category filter
            k: Number of results to return
            num_candidates: Number of candidates to consider
            source_fields: Fields to return in results
            
        Returns:
            List of search results with combined scores
        """
        if source_fields is None:
            source_fields = ["id", "category", "source", "content"]
        
        k = k or self.top_k
        num_candidates = num_candidates or self.num_candidates
        
        # Build keyword query
        keyword_query = {
            "multi_match": {
                "query": query_text,
                "fields": ["content^1.0"],
                "type": "best_fields"
            }
        }
        
        # Build filters
        filters = []
        if category and self.category_filter:
            category = normalize_category(category)
            filters.append({"term": {"category": category}})
        
        # Build combined query
        es_query = {"bool": {"must": [keyword_query]}}
        if filters:
            es_query["bool"]["filter"] = filters
        
        # Build KNN query
        knn_query = {
            "field": "embedding",
            "query_vector": query_vector,
            "k": k,
            "num_candidates": num_candidates
        }
        
        # Execute hybrid search (ES 8.x native support)
        resp = self.es.search(
            index=self.index_name,
            size=k,
            knn=knn_query,
            query=es_query,
            _source=source_fields,
            highlight={"fields": {"content": {}}}
        )
        
        return resp["hits"]["hits"]
    
    def search(
        self,
        query_vector: List[float],
        query_text: str,
        category: Optional[str] = None,
        k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Main search method that chooses between vector and hybrid search.
        
        Args:
            query_vector: Query embedding vector
            query_text: Query text
            category: Optional category filter
            k: Number of results to return
            
        Returns:
            List of search results
        """
        if self.use_hybrid:
            return self.hybrid_search(query_vector, query_text, category, k)
        else:
            return self.vector_search(query_vector, category, k)
    
    def format_results(self, hits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format search results into a cleaner structure.
        
        Args:
            hits: Raw search results from Elasticsearch
            
        Returns:
            Formatted results
        """
        formatted = []
        for hit in hits:
            source = hit["_source"]
            formatted.append({
                "id": source.get("id"),
                "category": source.get("category"),
                "source": source.get("source"),
                "content": source.get("content"),
                "score": hit["_score"],
                "highlight": hit.get("highlight", {}).get("content", [])
            })
        return formatted

