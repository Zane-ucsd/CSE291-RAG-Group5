"""
Main entry point for RAG Pipeline.
Example usage and testing.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pipeline import RAGPipeline
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
        "What rehabilitation methods are most effective for treating knee injuries in badminton players?",
        "What preventive strategies are most effective in reducing the incidence of common injuries among badminton players, and how can these be tailored to different player levels and playing styles?",
        "What are the key factors that influence the recovery time and long-term performance of badminton players after common musculoskeletal injuries?",
        "Summarize the risk factors for low-back pain in professional cyclists and preventive core exercises supported by evidence.",
        "What is runner's knee?",
        "How do different types of running shoes (minimalist vs. cushioned) affect tibial stress and injury risk?",
        "An amateur footballer experienced sudden sharp pain in the back of the thigh while sprinting and could not continue running. Based on on-field signs and typical mechanisms, how to recognize a hamstring strain and decide if it's mild or severe?",
        "I want to reduce injury risk through warm-up routines. What are the most effective warm-up exercises or programs I can implement each week?",
        "Our team increased training intensity recently. How can I monitor whether players are at higher risk of injury?",
        "Why do breaststroke and freestyle put stress on different body parts, and what drills help protect the knees and lower back?",
        "What are the best rehab or strengthening exercises for swimmers coming back from shoulder or back injuries?",
        "Why do female swimmers get injured more often, and what can they do in training or nutrition to lower that risk?"
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

