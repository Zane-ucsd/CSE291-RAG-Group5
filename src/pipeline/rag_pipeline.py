"""
Main RAG Pipeline module.
Integrates all components for end-to-end RAG processing.
"""

from typing import Dict, Any, Optional, List
import time
from ..config import RETRIEVAL_CONFIG, RERANKING_CONFIG
from ..utils import classify_sport_category
from ..embedding import EmbeddingGenerator
from ..retrieval import Retriever
from ..reranking import Reranker
from ..generation import GeminiGenerator


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
        self.reranker = Reranker(
            enabled=use_reranking,
            use_domain_filter=RERANKING_CONFIG.get("use_domain_filter", False),
            alpha=RERANKING_CONFIG.get("alpha", 1.0)
        )
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
        category: Optional[str] = None,
        return_pre_rerank: bool = False
    ) -> Dict[str, Any]:
        """
        Process a query through the complete RAG pipeline.
        
        Args:
            query_text: User query text
            top_k: Number of documents to retrieve (defaults to RETRIEVAL_CONFIG["top_k"])
            rerank_top_k: Number of documents to return after reranking (defaults to RERANKING_CONFIG["rerank_top_k"])
            category: Optional category filter
            return_pre_rerank: Whether to include pre-rerank documents in result (for evaluation)
            
        Returns:
            Dictionary with 'response', 'sources', 'documents', and metadata
            If return_pre_rerank=True, also includes 'pre_rerank_documents'
            Includes 'latency' dictionary with timing information for each stage
        """
        # Use config defaults if not specified
        top_k = top_k or RETRIEVAL_CONFIG["top_k"]
        rerank_top_k = rerank_top_k or RERANKING_CONFIG["rerank_top_k"]
        
        # Initialize latency tracking
        latency = {}
        total_start = time.time()
        
        # Step 1: Generate query embedding
        print(f"\n🔍 Processing query: {query_text[:100]}...")
        embedding_start = time.time()
        try:
            query_embedding = self.embedding_gen.generate_embedding(query_text)
            latency["embedding"] = time.time() - embedding_start
            print(f"✅ Query embedding generated ({latency['embedding']:.3f}s)")
        except Exception as e:
            latency["embedding"] = time.time() - embedding_start
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower() or "RateLimit" in str(type(e)):
                print(f"❌ OpenAI API quota exceeded. Please check your billing and quota.")
                print(f"   Error: {error_msg}")
                # Return error result instead of crashing
                return {
                    "query": query_text,
                    "response": f"Error: OpenAI API quota exceeded. {error_msg}",
                    "sources": [],
                    "num_documents": 0,
                    "category": category,
                    "documents": [],
                    "latency": latency,
                    "error": "openai_quota_exceeded",
                    "error_message": error_msg
                }
            else:
                raise  # Re-raise other errors
        
        # Step 2: Classify category if not provided
        category_start = time.time()
        if category is None and RETRIEVAL_CONFIG["category_filter"]:
            category = classify_sport_category(query_text)
            if category:
                print(f"📂 Detected category: {category}")
        latency["category_classification"] = time.time() - category_start
        
        # Step 3: Retrieve documents
        print("🔎 Retrieving documents...")
        retrieval_start = time.time()
        hits = self.retriever.search(
            query_vector=query_embedding,
            query_text=query_text,
            category=category,
            k=top_k
        )
        documents = self.retriever.format_results(hits)
        latency["retrieval"] = time.time() - retrieval_start
        print(f"✅ Retrieved {len(documents)} documents ({latency['retrieval']:.3f}s)")
        
        # Step 4: Store pre-rerank documents if needed (for evaluation)
        pre_rerank_documents = None
        if return_pre_rerank:
            import copy
            pre_rerank_documents = copy.deepcopy(documents)
        
        # Step 5: Rerank documents (if enabled)
        latency["reranking"] = 0.0
        if self.reranker.enabled and len(documents) > 0:
            print("🔄 Reranking documents...")
            rerank_start = time.time()
            documents = self.reranker.rerank(query_text, documents, top_k=rerank_top_k)
            latency["reranking"] = time.time() - rerank_start
            print(f"✅ Reranked to top {len(documents)} documents ({latency['reranking']:.3f}s)")
        
        # Step 6: Generate response
        print("🤖 Generating response with Gemini...")
        generation_start = time.time()
        result = self.generator.generate(query_text, documents)
        generation_duration = time.time() - generation_start
        latency["generation"] = generation_duration
        
        # Warn if generation took too long (approaching timeout)
        from ..config import GEMINI_CONFIG
        generation_timeout = GEMINI_CONFIG.get("timeout", 60.0)
        if generation_duration > generation_timeout * 0.8:
            print(f"⚠️  Generation took {generation_duration:.2f}s (approaching timeout of {generation_timeout}s)")
        
        # Extract token information
        input_tokens = result.get("input_tokens", 0)
        output_tokens = result.get("output_tokens", 0)
        total_tokens = result.get("total_tokens", input_tokens + output_tokens)
        
        print(f"✅ Response generated ({latency['generation']:.3f}s)")
        print(f"   📊 Tokens: Input={input_tokens}, Output={output_tokens}, Total={total_tokens}")
        
        # Calculate total time
        latency["total"] = time.time() - total_start
        
        # Add metadata
        result["query"] = query_text
        result["category"] = category
        result["documents"] = documents  # Include all documents in result (not just top 5)
        result["latency"] = latency  # Add latency information
        
        # Token information is already in result from generator.generate()
        
        # Add pre-rerank data if requested
        if return_pre_rerank and pre_rerank_documents is not None:
            result["pre_rerank_documents"] = pre_rerank_documents
        
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
            top_k: Number of documents to retrieve (defaults to RETRIEVAL_CONFIG["top_k"])
            rerank_top_k: Number of documents to return after reranking (defaults to RERANKING_CONFIG["rerank_top_k"])
            category: Optional category filter
            
        Yields:
            Response chunks
        """
        # Use config defaults if not specified
        top_k = top_k or RETRIEVAL_CONFIG["top_k"]
        rerank_top_k = rerank_top_k or RERANKING_CONFIG["rerank_top_k"]
        
        # Steps 1-4: Same as query()
        query_embedding = self.embedding_gen.generate_embedding(query_text)
        
        if category is None and RETRIEVAL_CONFIG["category_filter"]:
            category = classify_sport_category(query_text)
        
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
            "default_top_k": RETRIEVAL_CONFIG["top_k"],
            "default_rerank_top_k": RERANKING_CONFIG["rerank_top_k"],
            "embedding_model": "text-embedding-3-small",  # From OPENAI_CONFIG
            "generation_model": "gemini-2.0-flash"  # From GEMINI_CONFIG
        }

