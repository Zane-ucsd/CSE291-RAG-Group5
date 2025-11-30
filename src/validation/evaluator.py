"""
Evaluator for RAG Pipeline.
Evaluates retrieval quality against ground truth annotations.
"""

from typing import List, Dict, Any, Optional
import json
from pathlib import Path
from datetime import datetime

from ..pipeline import RAGPipeline
from ..config import RETRIEVAL_CONFIG, RERANKING_CONFIG
from .metrics import calculate_all_metrics, aggregate_metrics


class RAGEvaluator:
    """
    Evaluate RAG pipeline against ground truth.
    Measures retrieval quality before and after reranking.
    """
    
    def __init__(
        self, 
        ground_truth_path: str, 
        pipeline: Optional[RAGPipeline] = None
    ):
        """
        Initialize evaluator with ground truth.
        
        Args:
            ground_truth_path: Path to ground truth JSON file
            pipeline: Optional pre-initialized RAGPipeline (will create one if not provided)
        """
        self.ground_truth_path = ground_truth_path
        self.ground_truth = self.load_ground_truth(ground_truth_path)
        self.pipeline = pipeline or RAGPipeline()
        
        print(f"✅ Loaded {len(self.ground_truth)} queries from ground truth")
    
    def load_ground_truth(self, path: str) -> List[Dict[str, Any]]:
        """
        Load ground truth from JSON file.
        
        Args:
            path: Path to ground truth JSON
            
        Returns:
            List of ground truth entries
        """
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    
    def evaluate_query(
        self, 
        query: str, 
        relevant_ids: List[str],
        evaluate_pre_rerank: bool = True
    ) -> Dict[str, Any]:
        """
        Evaluate a single query.
        
        Args:
            query: Query text
            relevant_ids: Ground truth relevant document IDs
            evaluate_pre_rerank: Whether to also evaluate pre-rerank results
            
        Returns:
            Dictionary with evaluation results:
            {
                "query": str,
                "relevant_count": int,
                "retrieved_count_after": int,
                "retrieved_count_before": int,  # If evaluate_pre_rerank=True
                "found_count_after": int,
                "found_count_before": int,      # If evaluate_pre_rerank=True
                "metrics_after_rerank": {...},
                "metrics_before_rerank": {...}  # If evaluate_pre_rerank=True
            }
        """
        # Run pipeline
        result = self.pipeline.query(
            query_text=query,
            return_pre_rerank=evaluate_pre_rerank
        )
        
        # Extract retrieved IDs
        retrieved_ids_after = [doc["id"] for doc in result["documents"]]
        relevant_ids_set = set(relevant_ids)
        
        # Calculate metrics after reranking
        metrics_after = calculate_all_metrics(
            retrieved_ids=retrieved_ids_after,
            relevant_ids=relevant_ids_set,
            k_values=[5, 10] if len(retrieved_ids_after) >= 10 else [len(retrieved_ids_after)]
        )
        
        # Count found documents
        found_count_after = len(set(retrieved_ids_after) & relevant_ids_set)
        
        # Build result
        eval_result = {
            "query": query,
            "category": result.get("category"),
            "relevant_count": len(relevant_ids),
            "retrieved_count_after": len(retrieved_ids_after),
            "found_count_after": found_count_after,
            "metrics_after_rerank": metrics_after
        }
        
        # Evaluate pre-rerank if requested
        if evaluate_pre_rerank and "pre_rerank_documents" in result:
            retrieved_ids_before = [doc["id"] for doc in result["pre_rerank_documents"]]
            
            metrics_before = calculate_all_metrics(
                retrieved_ids=retrieved_ids_before,
                relevant_ids=relevant_ids_set,
                k_values=[10, 20, 60] if len(retrieved_ids_before) >= 60 else [len(retrieved_ids_before)]
            )
            
            found_count_before = len(set(retrieved_ids_before) & relevant_ids_set)
            
            eval_result["retrieved_count_before"] = len(retrieved_ids_before)
            eval_result["found_count_before"] = found_count_before
            eval_result["metrics_before_rerank"] = metrics_before
        
        return eval_result
    
    def evaluate_all(
        self, 
        evaluate_pre_rerank: bool = True,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Evaluate all queries in ground truth.
        
        Args:
            evaluate_pre_rerank: Whether to also evaluate pre-rerank results
            limit: Optional limit on number of queries to evaluate (for testing)
            
        Returns:
            Dictionary with:
            {
                "overall_metrics": {
                    "after_rerank": {...},
                    "before_rerank": {...}  # If evaluate_pre_rerank=True
                },
                "per_query_results": [...],
                "config": {...},
                "timestamp": str,
                "num_queries": int
            }
        """
        print("\n" + "="*80)
        print("Starting RAG Pipeline Evaluation")
        print("="*80)
        
        per_query_results = []
        all_metrics_after = []
        all_metrics_before = []
        
        # Limit queries if specified
        queries_to_eval = self.ground_truth[:limit] if limit else self.ground_truth
        
        for i, gt_entry in enumerate(queries_to_eval, 1):
            query = gt_entry["query"]
            relevant_ids = gt_entry["relevant_ids"]
            
            print(f"\n[{i}/{len(queries_to_eval)}] Evaluating: {query[:60]}...")
            
            try:
                eval_result = self.evaluate_query(
                    query=query,
                    relevant_ids=relevant_ids,
                    evaluate_pre_rerank=evaluate_pre_rerank
                )
                
                per_query_results.append(eval_result)
                all_metrics_after.append(eval_result["metrics_after_rerank"])
                
                if "metrics_before_rerank" in eval_result:
                    all_metrics_before.append(eval_result["metrics_before_rerank"])
                
                # Print quick summary
                recall_after = eval_result["metrics_after_rerank"].get("recall@10", 0.0)
                precision_after = eval_result["metrics_after_rerank"].get("precision@10", 0.0)
                print(f"  ✅ After rerank: Recall@10={recall_after:.3f}, Precision@10={precision_after:.3f}")
                
                if "metrics_before_rerank" in eval_result:
                    recall_before = eval_result["metrics_before_rerank"].get("recall@60", 0.0)
                    print(f"  📊 Before rerank: Recall@60={recall_before:.3f}")
            
            except Exception as e:
                print(f"  ❌ Error: {e}")
                continue
        
        # Aggregate metrics
        overall_metrics = {
            "after_rerank": aggregate_metrics(all_metrics_after)
        }
        
        if all_metrics_before:
            overall_metrics["before_rerank"] = aggregate_metrics(all_metrics_before)
        
        # Compile results
        results = {
            "overall_metrics": overall_metrics,
            "per_query_results": per_query_results,
            "config": {
                "reranking_enabled": self.pipeline.reranker.enabled,
                "use_domain_filter": RERANKING_CONFIG.get("use_domain_filter", False),
                "alpha": RERANKING_CONFIG.get("alpha", 1.0),
                "top_k": RETRIEVAL_CONFIG["top_k"],
                "num_candidates": RETRIEVAL_CONFIG.get("num_candidates", 60),
                "hybrid_search": RETRIEVAL_CONFIG.get("use_hybrid", False),
                "category_filter": RETRIEVAL_CONFIG.get("category_filter", False)
            },
            "timestamp": datetime.now().isoformat(),
            "num_queries": len(per_query_results),
            "ground_truth_file": self.ground_truth_path
        }
        
        return results
    
    def save_results(self, results: Dict[str, Any], output_path: str):
        """
        Save evaluation results to JSON file.
        
        Args:
            results: Evaluation results dictionary
            output_path: Path to save results
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Results saved to {output_path}")
    
    def print_summary(self, results: Dict[str, Any]):
        """
        Print a formatted summary of evaluation results.
        
        Args:
            results: Evaluation results dictionary
        """
        print("\n" + "="*80)
        print("EVALUATION SUMMARY")
        print("="*80)
        
        print(f"\n📊 Evaluated {results['num_queries']} queries")
        print(f"📁 Ground truth: {results['ground_truth_file']}")
        print(f"🕒 Timestamp: {results['timestamp']}")
        
        print("\n🔧 Configuration:")
        for key, value in results['config'].items():
            print(f"  {key}: {value}")
        
        print("\n" + "-"*80)
        print("Overall Metrics (After Reranking)")
        print("-"*80)
        for metric, value in sorted(results['overall_metrics']['after_rerank'].items()):
            print(f"  {metric:20s}: {value:6.4f}")
        
        if 'before_rerank' in results['overall_metrics']:
            print("\n" + "-"*80)
            print("Overall Metrics (Before Reranking)")
            print("-"*80)
            for metric, value in sorted(results['overall_metrics']['before_rerank'].items()):
                print(f"  {metric:20s}: {value:6.4f}")
        
        print("\n" + "="*80)

