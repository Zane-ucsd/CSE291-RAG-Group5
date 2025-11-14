"""
Example usage of RAG Pipeline.
Demonstrates different ways to use the pipeline.
"""

from rag_pipeline import RAGPipeline


def example_basic_query():
    """
    Basic query example.
    """
    print("=" * 80)
    print("Example 1: Basic Query")
    print("=" * 80)
    
    # Initialize pipeline
    pipeline = RAGPipeline()
    
    # Query
    query = "What rehabilitation methods are most effective for treating knee injuries in badminton players?"
    result = pipeline.query(query)
    
    # Print results
    print(f"\nQuery: {query}")
    print(f"\nResponse:\n{result['response']}")
    print(f"\nSources: {', '.join(set(result['sources']))}")
    print(f"Category: {result.get('category', 'N/A')}")
    print(f"Documents used: {result['num_documents']}")


def example_custom_parameters():
    """
    Example with custom parameters.
    """
    print("\n" + "=" * 80)
    print("Example 2: Custom Parameters")
    print("=" * 80)
    
    pipeline = RAGPipeline()
    
    query = "What are the best rehab exercises for swimmers coming back from shoulder injuries?"
    
    # Custom retrieval and reranking parameters
    result = pipeline.query(
        query=query,
        top_k=15,          # Retrieve 15 documents
        rerank_top_k=8    # Rerank to top 8
    )
    
    print(f"\nQuery: {query}")
    print(f"\nResponse:\n{result['response']}")
    print(f"\nRetrieved {len(result.get('documents', []))} documents after reranking")


def example_without_reranking():
    """
    Example without reranking.
    """
    print("\n" + "=" * 80)
    print("Example 3: Without Reranking")
    print("=" * 80)
    
    # Initialize without reranking
    pipeline = RAGPipeline(use_reranking=False)
    
    query = "How should one design a progressive rehabilitation training plan for ITBS?"
    result = pipeline.query(query)
    
    print(f"\nQuery: {query}")
    print(f"\nResponse:\n{result['response']}")


def example_streaming():
    """
    Example with streaming response.
    """
    print("\n" + "=" * 80)
    print("Example 4: Streaming Response")
    print("=" * 80)
    
    pipeline = RAGPipeline()
    
    query = "What causes shoulder pain in swimmers?"
    
    print(f"\nQuery: {query}")
    print("\nResponse (streaming):\n")
    
    # Stream response
    for chunk in pipeline.query_stream(query):
        print(chunk, end="", flush=True)
    
    print("\n")


def example_pipeline_info():
    """
    Example: Get pipeline information.
    """
    print("\n" + "=" * 80)
    print("Example 5: Pipeline Information")
    print("=" * 80)
    
    pipeline = RAGPipeline()
    info = pipeline.get_pipeline_info()
    
    print("\nPipeline Configuration:")
    for key, value in info.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    # Run examples
    try:
        example_basic_query()
        example_custom_parameters()
        example_without_reranking()
        example_streaming()
        example_pipeline_info()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease check:")
        print("  1. API keys are set correctly")
        print("  2. Elasticsearch is running")
        print("  3. All dependencies are installed")

