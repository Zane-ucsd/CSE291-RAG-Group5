"""
Main entry point for RAG Pipeline.
Example usage and testing.
"""

import sys
from pathlib import Path
import json
import os
import argparse # 导入 argparse 库

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pipeline import RAGPipeline


def main(evaluate=False):
    """
    Main function demonstrating RAG Pipeline usage.
    
    Args:
        evaluate: Whether to run evaluation (default: False, controlled by CLI or env var).
    """
    
    # -------------------------------------------------------------
    # 优化 1: 将 evaluate_enabled 的计算提前
    # Check both command-line argument, function argument, and environment variable
    evaluate_enabled = evaluate or os.getenv("EVALUATE_WITH_RAGAS", "false").lower() == "true"
    # -------------------------------------------------------------

    # Initialize pipeline
    print("🚀 Initializing RAG Pipeline...")
    pipeline = RAGPipeline()
    
    # Example queries
    queries = [
        "What rehabilitation methods are most effective for treating knee injuries in badminton players?",
        "What preventive strategies are most effective in reducing the incidence of common injuries among badminton players, and how can these be tailored to different player levels and playing styles?",
        "What are the key factors that influence the recovery time and long-term performance of badminton players after common musculoskeletal injuries?",
        "Explain how improper saddle height and reach contribute to knee and hip overuse injuries.",
        "What is runner's knee?",
        "How do different types of running shoes (minimalist vs. cushioned) affect tibial stress and injury risk?",
        "An amateur footballer experienced sudden sharp pain in the back of the thigh while sprinting and could not continue running. Based on on-field signs and typical mechanisms, how to recognize a hamstring strain and decide if it's mild or severe?",
        "I want to reduce injury risk through warm-up routines. What are the most effective warm-up exercises or programs I can implement each week?",
        "Our team increased training intensity recently. How can I monitor whether players are at higher risk of injury?",
        "Why do breaststroke and freestyle put stress on different body parts?",
        "What are the best rehab or strengthening exercises for swimmers coming back from shoulder or back injuries?",
        "Why do female swimmers get injured more often, and what can they do in training or nutrition to lower that risk?"
    ]
    
    # Process queries
    # If evaluation is enabled, also return pre-rerank documents for comparison
    return_pre_rerank = evaluate_enabled
    
    results = []
    all_latencies = {
        "embedding": [],
        "category_classification": [],
        "retrieval": [],
        "reranking": [],
        "generation": [],
        "total": []
    }
    
    # Add token tracking
    all_tokens = {
        "input_tokens": [],
        "output_tokens": [],
        "total_tokens": []
    }
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'='*80}")
        print(f"Query {i}/{len(queries)}")
        print(f"{'='*80}")
        
        try:
            # 确保 return_pre_rerank 在 evaluate_enabled 为 True 时生效
            result = pipeline.query(query, return_pre_rerank=return_pre_rerank) 
            results.append(result)
            
            # Collect latency data (only if query succeeded)
            if "latency" in result and "error" not in result:
                for key in all_latencies.keys():
                    if key in result["latency"]:
                        all_latencies[key].append(result["latency"][key])
            
            # Collect token data (only if query succeeded)
            if "error" not in result:
                if "input_tokens" in result:
                    all_tokens["input_tokens"].append(result["input_tokens"])
                if "output_tokens" in result:
                    all_tokens["output_tokens"].append(result["output_tokens"])
                if "total_tokens" in result:
                    all_tokens["total_tokens"].append(result["total_tokens"])
            
            # Print results
            if "error" in result:
                print(f"\n❌ Error processing query:")
                print(f"   {result.get('error_message', 'Unknown error')}")
            else:
                print(f"\n📝 Response:")
                print(result["response"])
                print(f"\n📚 Sources: {', '.join(set(result.get('sources', [])))}")
                print(f"📊 Retrieved {result.get('num_documents', 0)} documents")
                
                # Print latency for this query
                if "latency" in result:
                    lat = result["latency"]
                    print(f"\n⏱️  Latency Breakdown:")
                    print(f"   - Embedding: {lat.get('embedding', 0):.3f}s")
                    print(f"   - Category Classification: {lat.get('category_classification', 0):.3f}s")
                    print(f"   - Retrieval: {lat.get('retrieval', 0):.3f}s")
                    print(f"   - Reranking: {lat.get('reranking', 0):.3f}s")
                    print(f"   - Generation: {lat.get('generation', 0):.3f}s")
                    print(f"   - Total: {lat.get('total', 0):.3f}s")
                
                # Print token information for this query
                if "input_tokens" in result or "output_tokens" in result:
                    print(f"\n🔢 Token Usage:")
                    print(f"   - Input Tokens: {result.get('input_tokens', 0)}")
                    print(f"   - Output Tokens: {result.get('output_tokens', 0)}")
                    print(f"   - Total Tokens: {result.get('total_tokens', result.get('input_tokens', 0) + result.get('output_tokens', 0))}")
        
        except Exception as e:
            print(f"\n❌ Unexpected error processing query:")
            print(f"   {str(e)}")
            import traceback
            traceback.print_exc()
            # Add error result
            results.append({
                "query": query,
                "response": f"Error: {str(e)}",
                "sources": [],
                "num_documents": 0,
                "error": "unexpected_error",
                "error_message": str(e)
            })
    
    # Save results
    # Ensure results directory exists
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)
    
    output_file = "results/rag_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Results saved to {output_file}")
    
    # Print aggregate latency statistics (only if we have successful queries)
    if any("latency" in r and "error" not in r for r in results):
        print("\n" + "="*80)
        print("⏱️  AGGREGATE LATENCY STATISTICS")
        print("="*80)
        
        def print_latency_stats(name, values):
            """Print latency statistics for a given stage."""
            if values:
                avg = sum(values) / len(values)
                min_val = min(values)
                max_val = max(values)
                print(f"   {name:25s}: Avg={avg:.3f}s, Min={min_val:.3f}s, Max={max_val:.3f}s")
        
        print_latency_stats("Embedding", all_latencies["embedding"])
        print_latency_stats("Category Classification", all_latencies["category_classification"])
        print_latency_stats("Retrieval", all_latencies["retrieval"])
        print_latency_stats("Reranking", all_latencies["reranking"])
        print_latency_stats("Generation", all_latencies["generation"])
        print_latency_stats("Total Pipeline", all_latencies["total"])
        
        # Calculate percentage breakdown
        if all_latencies["total"]:
            avg_total = sum(all_latencies["total"]) / len(all_latencies["total"])
            print(f"\n📊 Time Distribution (Average):")
            if avg_total > 0:
                stages = [
                    ("Embedding", all_latencies["embedding"]),
                    ("Category Classification", all_latencies["category_classification"]),
                    ("Retrieval", all_latencies["retrieval"]),
                    ("Reranking", all_latencies["reranking"]),
                    ("Generation", all_latencies["generation"])
                ]
                for name, values in stages:
                    if values:
                        avg_stage = sum(values) / len(values)
                        percentage = (avg_stage / avg_total) * 100
                        print(f"   - {name:25s}: {percentage:5.1f}% ({avg_stage:.3f}s)")
        
        print("="*80)
    
    # Print aggregate token statistics
    if any("input_tokens" in r and "error" not in r for r in results):
        print("\n" + "="*80)
        print("🔢 AGGREGATE TOKEN STATISTICS")
        print("="*80)
        
        def print_token_stats(name, values):
            """Print token statistics."""
            if values:
                avg = sum(values) / len(values)
                min_val = min(values)
                max_val = max(values)
                total = sum(values)
                print(f"   {name:25s}: Avg={avg:.1f}, Min={min_val}, Max={max_val}, Total={total}")
        
        print_token_stats("Input Tokens", all_tokens["input_tokens"])
        print_token_stats("Output Tokens", all_tokens["output_tokens"])
        print_token_stats("Total Tokens", all_tokens["total_tokens"])
        
        # Calculate token ratio
        if all_tokens["input_tokens"] and all_tokens["output_tokens"]:
            avg_input = sum(all_tokens["input_tokens"]) / len(all_tokens["input_tokens"])
            avg_output = sum(all_tokens["output_tokens"]) / len(all_tokens["output_tokens"])
            if avg_input > 0:
                ratio = avg_output / avg_input
                print(f"\n📊 Token Ratio (Output/Input): {ratio:.2f}")
        
        print("="*80)
    
    # Evaluate results if enabled
    # -------------------------------------------------------------
    # 优化 2: 移除重复的 evaluate_enabled 计算
    # -------------------------------------------------------------
    
    if evaluate_enabled:
        ground_truth_file = "results/ground_truth_example.json"
        use_ground_truth = os.path.exists(ground_truth_file)
        
        print("\n" + "="*80)
        print("📊 EVALUATION MODE ENABLED")
        print("="*80)
        
        # 1. Evaluate retrieval results (ES retrieval and reranking)
        if use_ground_truth:
            try:
                from src.validation.retrieval_metrics import RetrievalEvaluator
                
                print("\n[1/2] Evaluating retrieval results (ES + Reranking)...")
                evaluator = RetrievalEvaluator(ground_truth_file=ground_truth_file)
                
                # Evaluate after reranking (final results)
                evaluation_result_after = evaluator.evaluate_retrieval_results(
                    results_file=output_file,
                    output_file="results/evaluation_report_after_rerank.json"
                )
                
                # Print summary report
                evaluator.print_evaluation_report(evaluation_result_after)
                
                # Evaluate before reranking if pre_rerank_documents are available
                with open(output_file, 'r', encoding='utf-8') as f:
                    results_data = json.load(f)
                
                has_pre_rerank = any('pre_rerank_documents' in r for r in results_data)
                
                if has_pre_rerank:
                    # Create a temporary results file with pre-rerank documents
                    pre_rerank_results = []
                    for result in results_data:
                        if 'pre_rerank_documents' in result:
                            pre_rerank_result = result.copy()
                            pre_rerank_result['documents'] = pre_rerank_result.pop('pre_rerank_documents')
                            pre_rerank_results.append(pre_rerank_result)
                    
                    if pre_rerank_results:
                        import tempfile
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
                            json.dump(pre_rerank_results, f, ensure_ascii=False, indent=2)
                            temp_file = f.name
                        
                        try:
                            evaluation_result_before = evaluator.evaluate_retrieval_results(
                                results_file=temp_file,
                                output_file="results/evaluation_report_before_rerank.json"
                            )
                            
                            # Compare key metrics
                            metrics_after = evaluation_result_after['aggregate']
                            metrics_before = evaluation_result_before['aggregate']
                            
                            print("\n" + "-"*80)
                            print("📊 Reranking Impact Comparison")
                            print("-"*80)
                            # Ranking quality metrics (most important for reranking)
                            print("Ranking Quality (most improved):")
                            print(f"  Precision@1:  {metrics_before.get('mean_precision@1', 0):.4f} → {metrics_after.get('mean_precision@1', 0):.4f} (Δ{metrics_after.get('mean_precision@1', 0) - metrics_before.get('mean_precision@1', 0):+.4f})")
                            print(f"  MRR:         {metrics_before.get('mean_mrr', 0):.4f} → {metrics_after.get('mean_mrr', 0):.4f} (Δ{metrics_after.get('mean_mrr', 0) - metrics_before.get('mean_mrr', 0):+.4f})")
                            print(f"  NDCG@10:     {metrics_before.get('mean_ndcg@10', 0):.4f} → {metrics_after.get('mean_ndcg@10', 0):.4f} (Δ{metrics_after.get('mean_ndcg@10', 0) - metrics_before.get('mean_ndcg@10', 0):+.4f})")
                            print("\nCoverage Metrics (unchanged - rerank only reorders, doesn't add docs):")
                            print(f"  Precision@10: {metrics_before.get('mean_precision@10', 0):.4f} → {metrics_after.get('mean_precision@10', 0):.4f} (Δ{metrics_after.get('mean_precision@10', 0) - metrics_before.get('mean_precision@10', 0):+.4f})")
                            print(f"  Recall@10:   {metrics_before.get('mean_recall@10', 0):.4f} → {metrics_after.get('mean_recall@10', 0):.4f} (Δ{metrics_after.get('mean_recall@10', 0) - metrics_before.get('mean_recall@10', 0):+.4f})")
                            print("-"*80)
                            
                        finally:
                            try:
                                os.unlink(temp_file)
                            except:
                                pass
                
                print(f"\n✅ Retrieval evaluation completed")
                print(f"   Files: results/evaluation_report_after_rerank.json, results/evaluation_report_before_rerank.json")
                
            except ImportError as e:
                print(f"⚠️  Retrieval evaluation skipped: {e}")
            except Exception as e:
                print(f"❌ Retrieval evaluation failed: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"⚠️  Ground truth file not found: {ground_truth_file}")
            print("   Skipping retrieval evaluation (requires ground truth)")
        
        # 2. Evaluate generation results with RAGAS
        try:
            from src.validation.generation_evaluation import evaluate_generation_results
            
            print("\n[2/2] Evaluating generation results with RAGAS...")
            eval_result = evaluate_generation_results(
                results_file=output_file,
                output_file="results/generation_evaluation.json",
                ground_truth_file=ground_truth_file if use_ground_truth else None,
                use_ground_truth=use_ground_truth
            )
            
            print(f"\n✅ RAGAS evaluation completed")
            print(f"   File: results/generation_evaluation.json")
            
        except ImportError as e:
            print(f"⚠️  RAGAS evaluation skipped: {e}")
            print("   Install ragas with: pip install ragas")
        except Exception as e:
            print(f"❌ RAGAS evaluation failed: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "="*80)
        print("✅ ALL EVALUATIONS COMPLETED")
        print("="*80)


def interactive_mode():
    """
    Interactive mode for real-time queries.
    """
    # ... (interactive_mode 代码不变)
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
    # -------------------------------------------------------------
    # 优化 3: 使用 argparse 处理命令行参数
    parser = argparse.ArgumentParser(description="Run the RAG Pipeline in standard or interactive mode, with optional evaluation.")
    parser.add_argument('mode', nargs='?', default='standard', choices=['interactive'], 
                        help="The mode to run the pipeline in. Defaults to 'standard'.")
    parser.add_argument('--evaluation', action='store_true', 
                        help="If set, enables evaluation mode for retrieval and generation metrics.")
    
    args = parser.parse_args()
    
    if args.mode == "interactive":
        interactive_mode()
    else:
        # 将 --evaluation 的结果传递给 main 函数
        main(evaluate=args.evaluation)
    # -------------------------------------------------------------