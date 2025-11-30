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
    for i, query in enumerate(queries, 1):
        print(f"\n{'='*80}")
        print(f"Query {i}/{len(queries)}")
        print(f"{'='*80}")
        
        # 确保 return_pre_rerank 在 evaluate_enabled 为 True 时生效
        result = pipeline.query(query, return_pre_rerank=return_pre_rerank) 
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
    
    # Evaluate results if enabled
    # -------------------------------------------------------------
    # 优化 2: 移除重复的 evaluate_enabled 计算
    # -------------------------------------------------------------
    
    if evaluate_enabled:
        ground_truth_file = "ground_truth_example.json"
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
                    output_file="evaluation_report_after_rerank.json"
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
                                output_file="evaluation_report_before_rerank.json"
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
                print(f"   Files: evaluation_report_after_rerank.json, evaluation_report_before_rerank.json")
                
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
                output_file="generation_evaluation.json",
                ground_truth_file=ground_truth_file if use_ground_truth else None,
                use_ground_truth=use_ground_truth
            )
            
            print(f"\n✅ RAGAS evaluation completed")
            print(f"   File: generation_evaluation.json")
            
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