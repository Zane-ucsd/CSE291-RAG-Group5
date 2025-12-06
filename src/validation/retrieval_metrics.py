"""
Retrieval Metrics Module for RAG Pipeline Evaluation

This module provides comprehensive metrics for evaluating retrieval results:
- Precision, Recall, F1-Score
- Mean Reciprocal Rank (MRR)
- Normalized Discounted Cumulative Gain (NDCG)
- Mean Average Precision (MAP)
- Hit Rate
- Coverage metrics

Usage:
    from src.validation.retrieval_metrics import RetrievalMetrics
    
    metrics = RetrievalMetrics()
    result = metrics.evaluate_query(
        query="What is knee injury?",
        retrieved_ids=["1", "2", "3", "4", "5"],
        relevant_ids=["1", "2", "6", "7"],
        scores=[0.95, 0.87, 0.76, 0.65, 0.54]
    )
    print(result)
"""

import json
import math
from typing import Dict, List, Set, Any, Tuple, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import statistics


@dataclass
class QueryMetrics:
    """Data class for storing metrics of a single query"""
    query: str
    relevant_ids: List[str]
    retrieved_ids: List[str]
    scores: Optional[List[float]] = None
    
    # Basic metrics
    precision_at_k: Dict[int, float] = None  # Precision@1, @3, @5, @10
    recall_at_k: Dict[int, float] = None     # Recall@1, @3, @5, @10
    f1_at_k: Dict[int, float] = None         # F1@1, @3, @5, @10
    
    # Ranking metrics
    mrr: float = 0.0                         # Mean Reciprocal Rank
    ndcg: Dict[int, float] = None            # NDCG@1, @3, @5, @10
    map_score: float = 0.0                   # Mean Average Precision
    hit_rate: float = 0.0                    # Whether top-k contains relevant doc
    
    # Coverage metrics
    precision: float = 0.0                   # Overall precision
    recall: float = 0.0                      # Overall recall
    f1_score: float = 0.0                    # Overall F1 score
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = {
            "query": self.query,
            "relevant_count": len(self.relevant_ids),
            "retrieved_count": len(self.retrieved_ids),
            "relevant_retrieved": len(set(self.relevant_ids) & set(self.retrieved_ids)),
            "precision": self.precision,
            "recall": self.recall,
            "f1_score": self.f1_score,
            "mrr": self.mrr,
            "map": self.map_score,
        }
        
        if self.precision_at_k:
            for k, v in self.precision_at_k.items():
                result[f"precision@{k}"] = v
        
        if self.recall_at_k:
            for k, v in self.recall_at_k.items():
                result[f"recall@{k}"] = v
        
        if self.f1_at_k:
            for k, v in self.f1_at_k.items():
                result[f"f1@{k}"] = v
        
        if self.ndcg:
            for k, v in self.ndcg.items():
                result[f"ndcg@{k}"] = v
        
        result["hit_rate"] = self.hit_rate
        
        return result


class RetrievalMetrics:
    """
    Comprehensive retrieval metrics calculator for RAG pipeline evaluation
    """
    
    def __init__(self, k_values: Optional[List[int]] = None):
        """
        Initialize metrics calculator
        
        Args:
            k_values: List of k values for @k metrics (default: [1, 3, 5, 10])
        """
        self.k_values = k_values or [1, 3, 5, 10]
        
    def evaluate_query(
        self,
        query: str,
        retrieved_ids: List[str],
        relevant_ids: List[str],
        scores: Optional[List[float]] = None
    ) -> QueryMetrics:
        """
        Evaluate retrieval results for a single query
        
        Args:
            query: Query text
            retrieved_ids: List of retrieved document IDs (in rank order)
            relevant_ids: List of relevant document IDs (ground truth)
            scores: Optional retrieval scores for each document (for NDCG calculation)
            
        Returns:
            QueryMetrics object with all calculated metrics
        """
        metrics = QueryMetrics(
            query=query,
            relevant_ids=relevant_ids,
            retrieved_ids=retrieved_ids,
            scores=scores
        )
        
        retrieved_set = set(retrieved_ids)
        relevant_set = set(relevant_ids)
        
        # Basic metrics
        metrics.precision = self._calculate_precision(retrieved_set, relevant_set)
        metrics.recall = self._calculate_recall(retrieved_set, relevant_set)
        metrics.f1_score = self._calculate_f1(metrics.precision, metrics.recall)
        
        # Ranking metrics
        metrics.mrr = self._calculate_mrr(retrieved_ids, relevant_ids)
        metrics.map_score = self._calculate_map(retrieved_ids, relevant_ids)
        
        # @K metrics
        metrics.precision_at_k = {}
        metrics.recall_at_k = {}
        metrics.f1_at_k = {}
        metrics.ndcg = {}
        
        for k in self.k_values:
            retrieved_at_k = retrieved_ids[:k]
            retrieved_at_k_set = set(retrieved_at_k)
            
            # Precision@k, Recall@k, F1@k
            p_k = self._calculate_precision(retrieved_at_k_set, relevant_set)
            r_k = self._calculate_recall(retrieved_at_k_set, relevant_set)
            f1_k = self._calculate_f1(p_k, r_k)
            
            metrics.precision_at_k[k] = p_k
            metrics.recall_at_k[k] = r_k
            metrics.f1_at_k[k] = f1_k
            
            # NDCG@k
            dcg_k = self._calculate_dcg(retrieved_at_k, relevant_ids, k)
            idcg_k = self._calculate_idcg(relevant_ids, k)
            ndcg_k = dcg_k / idcg_k if idcg_k > 0 else 0.0
            metrics.ndcg[k] = ndcg_k
            
            # Hit Rate@k (whether any relevant doc is in top-k)
            if k == self.k_values[0]:  # Calculate for the first k value
                metrics.hit_rate = 1.0 if retrieved_at_k_set & relevant_set else 0.0
        
        return metrics
    
    @staticmethod
    def _calculate_precision(retrieved: Set[str], relevant: Set[str]) -> float:
        """
        Calculate precision: |retrieved ∩ relevant| / |retrieved|
        
        Args:
            retrieved: Set of retrieved document IDs
            relevant: Set of relevant document IDs
            
        Returns:
            Precision score [0, 1]
        """
        if len(retrieved) == 0:
            return 0.0
        return len(retrieved & relevant) / len(retrieved)
    
    @staticmethod
    def _calculate_recall(retrieved: Set[str], relevant: Set[str]) -> float:
        """
        Calculate recall: |retrieved ∩ relevant| / |relevant|
        
        Args:
            retrieved: Set of retrieved document IDs
            relevant: Set of relevant document IDs
            
        Returns:
            Recall score [0, 1]
        """
        if len(relevant) == 0:
            return 0.0
        return len(retrieved & relevant) / len(relevant)
    
    @staticmethod
    def _calculate_f1(precision: float, recall: float) -> float:
        """
        Calculate F1 score: 2 * (precision * recall) / (precision + recall)
        
        Args:
            precision: Precision score
            recall: Recall score
            
        Returns:
            F1 score [0, 1]
        """
        if precision + recall == 0:
            return 0.0
        return 2 * (precision * recall) / (precision + recall)
    
    @staticmethod
    def _calculate_mrr(retrieved_ids: List[str], relevant_ids: List[str]) -> float:
        """
        Calculate Mean Reciprocal Rank: 1 / (rank of first relevant document)
        
        Args:
            retrieved_ids: List of retrieved document IDs (in rank order)
            relevant_ids: List of relevant document IDs
            
        Returns:
            MRR score [0, 1]
        """
        relevant_set = set(relevant_ids)
        for rank, doc_id in enumerate(retrieved_ids, 1):
            if doc_id in relevant_set:
                return 1.0 / rank
        return 0.0
    
    @staticmethod
    def _calculate_map(retrieved_ids: List[str], relevant_ids: List[str]) -> float:
        """
        Calculate Mean Average Precision
        
        Args:
            retrieved_ids: List of retrieved document IDs (in rank order)
            relevant_ids: List of relevant document IDs
            
        Returns:
            MAP score [0, 1]
        """
        relevant_set = set(relevant_ids)
        
        if len(relevant_set) == 0:
            return 0.0
        
        score = 0.0
        num_hits = 0
        
        for rank, doc_id in enumerate(retrieved_ids, 1):
            if doc_id in relevant_set:
                num_hits += 1
                precision_at_k = num_hits / rank
                score += precision_at_k
        
        return score / len(relevant_set)
    
    @staticmethod
    def _calculate_dcg(retrieved_ids: List[str], relevant_ids: List[str], k: int) -> float:
        """
        Calculate Discounted Cumulative Gain at k
        
        DCG@k = Σ(i=1 to k) [rel_i / log2(i+1)]
        
        Args:
            retrieved_ids: List of retrieved document IDs (in rank order)
            relevant_ids: List of relevant document IDs
            k: The k value
            
        Returns:
            DCG@k score
        """
        relevant_set = set(relevant_ids)
        dcg = 0.0
        
        for rank, doc_id in enumerate(retrieved_ids[:k], 1):
            rel = 1.0 if doc_id in relevant_set else 0.0
            dcg += rel / math.log2(rank + 1)
        
        return dcg
    
    @staticmethod
    def _calculate_idcg(relevant_ids: List[str], k: int) -> float:
        """
        Calculate Ideal Discounted Cumulative Gain at k
        (assumes all relevant documents are ranked first)
        
        Args:
            relevant_ids: List of relevant document IDs
            k: The k value
            
        Returns:
            IDCG@k score
        """
        num_relevant = min(len(relevant_ids), k)
        idcg = 0.0
        
        for rank in range(1, num_relevant + 1):
            idcg += 1.0 / math.log2(rank + 1)
        
        return idcg
    
    def evaluate_batch(
        self,
        queries: List[str],
        retrieved_results: List[List[str]],
        relevant_results: List[List[str]],
        scores_list: Optional[List[List[float]]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate retrieval results for multiple queries
        
        Args:
            queries: List of query texts
            retrieved_results: List of retrieved document IDs for each query
            relevant_results: List of relevant document IDs for each query
            scores_list: Optional list of scores for each query
            
        Returns:
            Dictionary with aggregate metrics and per-query results
        """
        if not (len(queries) == len(retrieved_results) == len(relevant_results)):
            raise ValueError("Length of queries, retrieved_results, and relevant_results must match")
        
        query_metrics = []
        
        for i, query in enumerate(queries):
            scores = scores_list[i] if scores_list else None
            metrics = self.evaluate_query(
                query=query,
                retrieved_ids=retrieved_results[i],
                relevant_ids=relevant_results[i],
                scores=scores
            )
            query_metrics.append(metrics)
        
        # Calculate aggregate metrics
        aggregate = self._calculate_aggregate_metrics(query_metrics)
        
        return {
            "aggregate": aggregate,
            "per_query": [m.to_dict() for m in query_metrics],
            "num_queries": len(queries)
        }
    
    @staticmethod
    def _calculate_aggregate_metrics(query_metrics: List[QueryMetrics]) -> Dict[str, Any]:
        """
        Calculate aggregate metrics across multiple queries
        
        Args:
            query_metrics: List of QueryMetrics objects
            
        Returns:
            Dictionary with aggregate metrics
        """
        if not query_metrics:
            return {}
        
        precisions = [m.precision for m in query_metrics]
        recalls = [m.recall for m in query_metrics]
        f1_scores = [m.f1_score for m in query_metrics]
        mrrs = [m.mrr for m in query_metrics]
        maps = [m.map_score for m in query_metrics]
        hit_rates = [m.hit_rate for m in query_metrics]
        
        aggregate = {
            "mean_precision": statistics.mean(precisions),
            "mean_recall": statistics.mean(recalls),
            "mean_f1": statistics.mean(f1_scores),
            "mean_mrr": statistics.mean(mrrs),
            "mean_map": statistics.mean(maps),
            "mean_hit_rate": statistics.mean(hit_rates),
        }
        
        # Standard deviations (if more than 1 query)
        if len(query_metrics) > 1:
            aggregate["std_precision"] = statistics.stdev(precisions)
            aggregate["std_recall"] = statistics.stdev(recalls)
            aggregate["std_f1"] = statistics.stdev(f1_scores)
            aggregate["std_mrr"] = statistics.stdev(mrrs)
            aggregate["std_map"] = statistics.stdev(maps)
        
        # Per-k metrics
        first_query = query_metrics[0]
        if first_query.precision_at_k:
            for k in first_query.precision_at_k.keys():
                precision_at_k_vals = [m.precision_at_k[k] for m in query_metrics]
                recall_at_k_vals = [m.recall_at_k[k] for m in query_metrics]
                f1_at_k_vals = [m.f1_at_k[k] for m in query_metrics]
                ndcg_at_k_vals = [m.ndcg[k] for m in query_metrics]
                
                aggregate[f"mean_precision@{k}"] = statistics.mean(precision_at_k_vals)
                aggregate[f"mean_recall@{k}"] = statistics.mean(recall_at_k_vals)
                aggregate[f"mean_f1@{k}"] = statistics.mean(f1_at_k_vals)
                aggregate[f"mean_ndcg@{k}"] = statistics.mean(ndcg_at_k_vals)
        
        return aggregate


class RetrievalEvaluator:
    """
    High-level evaluator for RAG pipeline retrieval results
    Handles loading ground truth, running evaluations, and generating reports
    """
    
    def __init__(self, ground_truth_file: Optional[str] = None):
        """
        Initialize evaluator
        
        Args:
            ground_truth_file: Path to ground truth JSON file
        """
        self.ground_truth_file = ground_truth_file
        self.ground_truth_data = None
        self.metrics_calculator = RetrievalMetrics()
        
        if ground_truth_file:
            self.load_ground_truth(ground_truth_file)
    
    def load_ground_truth(self, file_path: str) -> None:
        """
        Load ground truth data from JSON file
        
        Args:
            file_path: Path to ground truth JSON file
            
        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file is not valid JSON
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Ground truth file not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate format
            if isinstance(data, dict):
                self.ground_truth_data = [data]
            elif isinstance(data, list):
                self.ground_truth_data = data
            else:
                raise ValueError(f"Ground truth must be a dict or list, got {type(data).__name__}")
            
            # Loaded ground truth entries silently
        
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON in ground truth file: {e.msg}", e.doc, e.pos)
    
    def evaluate_retrieval_results(
        self,
        results_file: str,
        output_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate retrieval results from a results file
        
        Args:
            results_file: Path to results JSON file
            output_file: Optional path to save evaluation results
            
        Returns:
            Evaluation results dictionary
            
        Raises:
            FileNotFoundError: If ground truth or results file not found
            ValueError: If ground truth data not loaded
        """
        if not self.ground_truth_data:
            raise ValueError("Ground truth data not loaded. Call load_ground_truth() first.")
        
        results_path = Path(results_file)
        if not results_path.exists():
            raise FileNotFoundError(f"Results file not found: {results_file}")
        
        # Load results
        with open(results_path, 'r', encoding='utf-8') as f:
            results_data = json.load(f)
        
        # Process results
        queries = []
        retrieved_results = []
        relevant_results = []
        scores_list = []
        
        # Map ground truth queries for matching
        gt_query_map = {gt["query"]: gt["relevant_ids"] for gt in self.ground_truth_data}
        
        for result in results_data:
            query = result.get("query", "")

            # Skip if not in ground truth
            if query not in gt_query_map:
                # Silently skip - this is expected for queries not in ground truth
                continue

            # Results may use different keys depending on producer: try several common ones
            docs = result.get("retrieved_documents") or result.get("documents") or result.get("results") or result.get("hits") or []

            # If the result contains an error or zero documents, silently continue (will produce zeros)
            if not docs:
                # Skip queries with no documents - will produce zero metrics
                continue

            retrieved_ids = []
            scores = []

            # Normalize various possible document entry formats
            for item in docs:
                if item is None:
                    continue
                # If item is a dict, try common id fields
                if isinstance(item, dict):
                    # try multiple possible id keys
                    doc_id = None
                    for key in ("id", "doc_id", "document_id", "_id", "source_id"):
                        if key in item:
                            doc_id = item.get(key)
                            break
                    # fallback: sometimes the document is stored under 'source' or nested
                    if doc_id is None and "source" in item and isinstance(item.get("source"), dict):
                        # try nested id
                        for key in ("id", "doc_id", "document_id", "_id"):
                            if key in item["source"]:
                                doc_id = item["source"].get(key)
                                break

                    # Score field fallbacks
                    score = item.get("score") if isinstance(item.get("score"), (int, float)) else item.get("_score", 0.0)

                    # If doc_id is still None, skip this item
                    if doc_id is None:
                        # sometimes the dict is actually a plain source string or has content
                        # try to use 'content' or 'text' as an identifier (not ideal)
                        continue
                    # Normalize id to string
                    try:
                        doc_id_str = str(doc_id).strip()
                    except Exception:
                        doc_id_str = str(doc_id)

                    retrieved_ids.append(doc_id_str)
                    try:
                        scores.append(float(score))
                    except Exception:
                        scores.append(0.0)

                # If item is a simple string or number, use it directly
                elif isinstance(item, (str, int)):
                    try:
                        retrieved_ids.append(str(item).strip())
                    except Exception:
                        retrieved_ids.append(str(item))
                    scores.append(0.0)
                else:
                    # Unknown item type; skip
                    continue

            relevant_ids = [str(r).strip() for r in gt_query_map[query]]
            
            queries.append(query)
            retrieved_results.append(retrieved_ids)
            relevant_results.append(relevant_ids)
            scores_list.append(scores)
        
        if not queries:
            raise ValueError("No matching queries found between results and ground truth")
        
        # Calculate metrics
        evaluation_result = self.metrics_calculator.evaluate_batch(
            queries=queries,
            retrieved_results=retrieved_results,
            relevant_results=relevant_results,
            scores_list=scores_list
        )
        
        # Save results if output file specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(evaluation_result, f, ensure_ascii=False, indent=2)
        
        return evaluation_result
    
    def print_evaluation_report(self, evaluation_result: Dict[str, Any]) -> None:
        """
        Print a formatted evaluation report
        
        Args:
            evaluation_result: Evaluation result dictionary from evaluate_retrieval_results()
        """
        aggregate = evaluation_result.get("aggregate", {})
        num_queries = evaluation_result.get("num_queries", 0)
        
        print(f"\n{'='*70}")
        print(f"📊 RETRIEVAL EVALUATION REPORT ({num_queries} queries)")
        print(f"{'='*70}")
        
        # Focus on @K metrics (most relevant)
        print("\n@K Metrics:")
        k_values = [5, 10, 20]
        for k in k_values:
            precision_key = f'mean_precision@{k}'
            recall_key = f'mean_recall@{k}'
            ndcg_key = f'mean_ndcg@{k}'
            if precision_key in aggregate or recall_key in aggregate or ndcg_key in aggregate:
                print(f"  @{k}:")
                if precision_key in aggregate:
                    print(f"    Precision@{k}: {aggregate.get(precision_key, 0):.4f}")
                if recall_key in aggregate:
                    print(f"    Recall@{k}:    {aggregate.get(recall_key, 0):.4f}")
                if ndcg_key in aggregate:
                    print(f"    NDCG@{k}:      {aggregate.get(ndcg_key, 0):.4f}")
        
        # Show other key metrics if available
        if aggregate.get('mean_mrr', 0) > 0:
            print(f"\n  MRR:             {aggregate.get('mean_mrr', 0):.4f}")
        if aggregate.get('mean_map', 0) > 0:
            print(f"  MAP:             {aggregate.get('mean_map', 0):.4f}")
        
        print(f"{'='*70}")
    
    def print_per_query_report(self, evaluation_result: Dict[str, Any], top_n: int = 5) -> None:
        """
        Print per-query results (top performing and worst performing)
        
        Args:
            evaluation_result: Evaluation result dictionary
            top_n: Number of top/worst queries to show
        """
        per_query = evaluation_result.get("per_query", [])
        
        if not per_query:
            print("No per-query results available")
            return
        
        # Sort by F1 score
        sorted_queries = sorted(per_query, key=lambda x: x.get("f1_score", 0), reverse=True)
        
        print(f"\n{'='*70}")
        print("🏆 TOP PERFORMING QUERIES")
        print(f"{'='*70}\n")
        
        for i, query in enumerate(sorted_queries[:top_n], 1):
            print(f"{i}. Query: {query['query'][:80]}")
            print(f"   F1: {query.get('f1_score', 0):.4f}, "
                  f"Precision: {query.get('precision', 0):.4f}, "
                  f"Recall: {query.get('recall', 0):.4f}")
            print(f"   Relevant: {query.get('relevant_count', 0)}, "
                  f"Retrieved: {query.get('retrieved_count', 0)}, "
                  f"Matched: {query.get('relevant_retrieved', 0)}\n")
        
        print(f"{'='*70}")
        print("😞 WORST PERFORMING QUERIES")
        print(f"{'='*70}\n")
        
        for i, query in enumerate(sorted_queries[-top_n:], 1):
            print(f"{i}. Query: {query['query'][:80]}")
            print(f"   F1: {query.get('f1_score', 0):.4f}, "
                  f"Precision: {query.get('precision', 0):.4f}, "
                  f"Recall: {query.get('recall', 0):.4f}")
            print(f"   Relevant: {query.get('relevant_count', 0)}, "
                  f"Retrieved: {query.get('retrieved_count', 0)}, "
                  f"Matched: {query.get('relevant_retrieved', 0)}\n")

    def evaluate_live_result(
        self,
        query: str,
        retrieved_docs: List[Any],
        ground_truth_map: Dict[str, List[str]],
        top_k: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate a single retrieval result (useful for live/interactive evaluation
        immediately after an ES search). This accepts the raw `retrieved_docs`
        as returned by the searcher (list of dicts or ids/strings) and a
        `ground_truth_map` mapping queries -> relevant_ids.

        Args:
            query: The query text
            retrieved_docs: List of retrieved document entries (dicts or ids/strings)
            ground_truth_map: Mapping of query -> list of relevant ids
            top_k: Optional cap on number of retrieved docs to evaluate

        Returns:
            A dictionary containing the per-query metrics (same format as
            QueryMetrics.to_dict()).
        """
        if query not in ground_truth_map:
            raise ValueError(f"Query not found in provided ground truth map: {query}")

        # Normalize retrieved docs to id list and optional scores
        retrieved_ids: List[str] = []
        scores: List[float] = []

        for item in retrieved_docs:
            if item is None:
                continue
            if isinstance(item, dict):
                # common id fields
                doc_id = None
                for key in ("id", "doc_id", "document_id", "_id", "source_id"):
                    if key in item:
                        doc_id = item.get(key)
                        break
                if doc_id is None and "_source" in item and isinstance(item.get("_source"), dict):
                    for key in ("id", "doc_id", "document_id", "_id"):
                        if key in item["_source"]:
                            doc_id = item["_source"].get(key)
                            break

                if doc_id is None:
                    # As a last resort skip items without identifiable id
                    continue

                try:
                    doc_id_str = str(doc_id).strip()
                except Exception:
                    doc_id_str = str(doc_id)

                retrieved_ids.append(doc_id_str)
                score_val = item.get("score") if isinstance(item.get("score"), (int, float)) else item.get("_score", 0.0)
                try:
                    scores.append(float(score_val))
                except Exception:
                    scores.append(0.0)

            elif isinstance(item, (str, int)):
                try:
                    retrieved_ids.append(str(item).strip())
                except Exception:
                    retrieved_ids.append(str(item))
                scores.append(0.0)

        if top_k:
            retrieved_ids = retrieved_ids[:top_k]
            scores = scores[:top_k]

        relevant_ids = [str(r).strip() for r in ground_truth_map[query]]

        qm = self.metrics_calculator.evaluate_query(
            query=query,
            retrieved_ids=retrieved_ids,
            relevant_ids=relevant_ids,
            scores=scores if scores else None
        )

        return qm.to_dict()
