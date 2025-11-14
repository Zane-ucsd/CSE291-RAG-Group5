"""
Main entry point for RAG Pipeline.
Example usage and testing.
"""

from rag_pipeline import RAGPipeline
import json


def main():
    """
    Main function demonstrating RAG Pipeline usage.
    """
    # Initialize pipeline
    print("🚀 Initializing RAG Pipeline...")
    pipeline = RAGPipeline()
    
    # Example queries
    queries = [
        "An amateur footballer experienced sudden sharp pain in the back of the thigh while sprinting and could not continue running. Based on on-field signs and typical mechanisms, how to recognize a hamstring strain and decide if it’s mild or severe?",
    ]
    
    # Process queries
    results = []
    for i, query in enumerate(queries, 1):
        print(f"\n{'='*80}")
        print(f"Query {i}/{len(queries)}")
        print(f"{'='*80}")
        
        result = pipeline.query(query)
        results.append(result)
        
        # Print results
        print(f"\n📝 Response:")
        print(result["response"])
        print(f"\n📚 Sources: {', '.join(set(result['sources']))}")
        print(f"📊 Retrieved {result['num_documents']} documents")
    
    # Save results
    output_file = "rag_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Results saved to {output_file}")


def interactive_mode():
    """
    Interactive mode for real-time queries.
    """
    print("🚀 Initializing RAG Pipeline...")
    pipeline = RAGPipeline()
    
    print("\n" + "="*80)
    print("Interactive RAG Query Mode")
    print("Type 'exit' or 'quit' to exit")
    print("="*80 + "\n")
    
    while True:
        query = input("Enter your query: ").strip()
        
        if query.lower() in ['exit', 'quit', 'q']:
            print("👋 Goodbye!")
            break
        
        if not query:
            continue
        
        try:
            result = pipeline.query(query)
            
            print("\n" + "-"*80)
            print("Response:")
            print("-"*80)
            print(result["response"])
            print("\n" + "-"*80)
            print(f"Sources: {', '.join(set(result['sources']))}")
            print(f"Category: {result.get('category', 'N/A')}")
            print("-"*80 + "\n")
        
        except Exception as e:
            print(f"❌ Error: {e}\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_mode()
    else:
        main()

