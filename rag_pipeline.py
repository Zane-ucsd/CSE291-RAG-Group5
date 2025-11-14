"""
Main RAG Pipeline module.
Integrates all components for end-to-end RAG processing.
"""

from typing import Dict, Any, Optional, List
import config
import utils
from embedding import EmbeddingGenerator
from retrieval import Retriever
from reranking import Reranker
from generation import GeminiGenerator


class RAGPipeline:
    """
    Main RAG Pipeline that integrates all components.
    """
    
    def __init__(
        self,
        use_reranking: Optional[bool] = None,
        use_hybrid_search: Optional[bool] = None
    ):
        """
        Initialize RAG Pipeline with all components.
        
        Args:
            use_reranking: Whether to use reranking (defaults to config)
            use_hybrid_search: Whether to use hybrid search (defaults to config)
        """
        # Initialize components
        self.embedding_gen = EmbeddingGenerator()
        self.retriever = Retriever()
        self.reranker = Reranker(enabled=use_reranking)
        self.generator = GeminiGenerator()
        
        # Override config if specified
        if use_hybrid_search is not None:
            self.retriever.use_hybrid = use_hybrid_search
        
        print("✅ RAG Pipeline initialized")
        print(f"   - Reranking: {'Enabled' if self.reranker.enabled else 'Disabled'}")
        print(f"   - Hybrid Search: {'Enabled' if self.retriever.use_hybrid else 'Disabled'}")
    
    def query(
        self,
        query_text: str,
        top_k: Optional[int] = None,
        rerank_top_k: Optional[int] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a query through the complete RAG pipeline.
        
        Args:
            query_text: User query text
            top_k: Number of documents to retrieve
            rerank_top_k: Number of documents to return after reranking
            category: Optional category filter
            
        Returns:
            Dictionary with 'response', 'sources', 'documents', and metadata
        """
        # Step 1: Generate query embedding
        print(f"\n🔍 Processing query: {query_text[:100]}...")
        query_embedding = self.embedding_gen.generate_embedding(query_text)
        print("✅ Query embedding generated")
        
        # Step 2: Classify category if not provided
        if category is None and config.RETRIEVAL_CONFIG["category_filter"]:
            category = utils.classify_sport_category(query_text)
            print(f"📂 Detected category: {category}")
        
        # Step 3: Retrieve documents
        print("🔎 Retrieving documents...")
        hits = self.retriever.search(
            query_vector=query_embedding,
            query_text=query_text,
            category=category,
            k=top_k
        )
        documents = self.retriever.format_results(hits)
        print(f"✅ Retrieved {len(documents)} documents")
        
        # Step 4: Rerank documents (if enabled)
        if self.reranker.enabled and len(documents) > 0:
            print("🔄 Reranking documents...")
            documents = self.reranker.rerank(query_text, documents, top_k=rerank_top_k)
            print(f"✅ Reranked to top {len(documents)} documents")
        
        # Step 5: Generate response
        print("🤖 Generating response with Gemini...")
        result = self.generator.generate(query_text, documents)
        print("✅ Response generated")
        
        # Add metadata
        result["query"] = query_text
        result["category"] = category
        result["documents"] = documents[:5]  # Include top 5 documents in result
        
        return result
    
    def query_stream(
        self,
        query_text: str,
        top_k: Optional[int] = None,
        rerank_top_k: Optional[int] = None,
        category: Optional[str] = None
    ):
        """
        Process a query with streaming response.
        
        Args:
            query_text: User query text
            top_k: Number of documents to retrieve
            rerank_top_k: Number of documents to return after reranking
            category: Optional category filter
            
        Yields:
            Response chunks
        """
        # Steps 1-4: Same as query()
        query_embedding = self.embedding_gen.generate_embedding(query_text)
        
        if category is None and config.RETRIEVAL_CONFIG["category_filter"]:
            category = utils.classify_sport_category(query_text)
        
        hits = self.retriever.search(
            query_vector=query_embedding,
            query_text=query_text,
            category=category,
            k=top_k
        )
        documents = self.retriever.format_results(hits)
        
        if self.reranker.enabled and len(documents) > 0:
            documents = self.reranker.rerank(query_text, documents, top_k=rerank_top_k)
        
        # Step 5: Stream response
        for chunk in self.generator.generate_stream(query_text, documents):
            yield chunk
    
    def get_pipeline_info(self) -> Dict[str, Any]:
        """
        Get information about the pipeline configuration.
        
        Returns:
            Dictionary with pipeline configuration
        """
        return {
            "reranking_enabled": self.reranker.enabled,
            "hybrid_search_enabled": self.retriever.use_hybrid,
            "category_filter_enabled": self.retriever.category_filter,
            "default_top_k": config.RETRIEVAL_CONFIG["top_k"],
            "default_rerank_top_k": config.RERANKING_CONFIG["rerank_top_k"],
            "embedding_model": config.OPENAI_CONFIG["model"],
            "generation_model": config.GEMINI_CONFIG["model"]
        }

