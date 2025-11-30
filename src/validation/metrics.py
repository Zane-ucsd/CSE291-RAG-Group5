"""
Evaluation metrics for retrieval systems.
Provides standard metrics for evaluating RAG pipeline performance.
"""

from typing import List, Set, Dict, Any
import math


def precision_at_k(retrieved_ids: List[str], relevant_ids: Set[str], k: int = None) -> float:
    """
    Precision@K: What fraction of retrieved docs are relevant?
    
    Formula: |retrieved ∩ relevant| / K
    
    Args:
        retrieved_ids: List of retrieved document IDs (in rank order)
        relevant_ids: Set of ground truth relevant document IDs
        k: Number of top results to consider (None = all)
        
    Returns:
        Precision score (0.0 to 1.0)
    """
    if not retrieved_ids:
        return 0.0
    
    k = k or len(retrieved_ids)
    top_k = retrieved_ids[:k]
    
    relevant_retrieved = len(set(top_k) & relevant_ids)
    return relevant_retrieved / len(top_k) if top_k else 0.0


def recall_at_k(retrieved_ids: List[str], relevant_ids: Set[str], k: int = None) -> float:
    """
    Recall@K: What fraction of relevant docs were retrieved?
    
    Formula: |retrieved ∩ relevant| / |relevant|
    
    Args:
        retrieved_ids: List of retrieved document IDs (in rank order)
        relevant_ids: Set of ground truth relevant document IDs
        k: Number of top results to consider (None = all)
        
    Returns:
        Recall score (0.0 to 1.0)
    """
    if not relevant_ids:
        return 0.0
    
    k = k or len(retrieved_ids)
    top_k = retrieved_ids[:k]
    
    relevant_retrieved = len(set(top_k) & relevant_ids)
    return relevant_retrieved / len(relevant_ids)


def f1_score(precision: float, recall: float) -> float:
    """
    F1 Score: Harmonic mean of precision and recall.
    
    Formula: 2 * (P * R) / (P + R)
    
    Args:
        precision: Precision score
        recall: Recall score
        
    Returns:
        F1 score (0.0 to 1.0)
    """
    if precision + recall == 0:
        return 0.0
    return 2 * (precision * recall) / (precision + recall)


def mean_reciprocal_rank(retrieved_ids: List[str], relevant_ids: Set[str]) -> float:
    """
    MRR: Reciprocal rank of the first relevant document.
    
    Formula: 1 / rank_of_first_relevant_doc
    
    Args:
        retrieved_ids: List of retrieved document IDs (in rank order)
        relevant_ids: Set of ground truth relevant document IDs
        
    Returns:
        MRR score (0.0 to 1.0)
    """
    for i, doc_id in enumerate(retrieved_ids, 1):
        if doc_id in relevant_ids:
            return 1.0 / i
    return 0.0


def average_precision(retrieved_ids: List[str], relevant_ids: Set[str]) -> float:
    """
    Average Precision: Precision averaged across all recall points.
    
    Args:
        retrieved_ids: List of retrieved document IDs (in rank order)
        relevant_ids: Set of ground truth relevant document IDs
        
    Returns:
        AP score (0.0 to 1.0)
    """
    if not relevant_ids:
        return 0.0
    
    score = 0.0
    num_relevant_seen = 0
    
    for i, doc_id in enumerate(retrieved_ids, 1):
        if doc_id in relevant_ids:
            num_relevant_seen += 1
            precision_at_i = num_relevant_seen / i
            score += precision_at_i
    
    return score / len(relevant_ids) if relevant_ids else 0.0


def ndcg_at_k(retrieved_ids: List[str], relevant_ids: Set[str], k: int = None) -> float:
    """
    NDCG@K: Normalized Discounted Cumulative Gain.
    Considers ranking position (earlier positions weighted more).
    
    Formula: DCG / IDCG
    DCG = sum(rel_i / log2(i+1))
    
    Args:
        retrieved_ids: List of retrieved document IDs (in rank order)
        relevant_ids: Set of ground truth relevant document IDs
        k: Number of top results to consider (None = all)
        
    Returns:
        NDCG score (0.0 to 1.0)
    """
    if not relevant_ids:
        return 0.0
    
    k = k or len(retrieved_ids)
    top_k = retrieved_ids[:k]
    
    # Calculate DCG
    dcg = 0.0
    for i, doc_id in enumerate(top_k, 1):
        relevance = 1.0 if doc_id in relevant_ids else 0.0
        dcg += relevance / math.log2(i + 1)
    
    # Calculate IDCG (perfect ranking)
    idcg = 0.0
    for i in range(1, min(len(relevant_ids), k) + 1):
        idcg += 1.0 / math.log2(i + 1)
    
    return dcg / idcg if idcg > 0 else 0.0


def hit_rate_at_k(retrieved_ids: List[str], relevant_ids: Set[str], k: int = None) -> float:
    """
    Hit Rate@K: Was at least one relevant doc retrieved?
    
    Args:
        retrieved_ids: List of retrieved document IDs (in rank order)
        relevant_ids: Set of ground truth relevant document IDs
        k: Number of top results to consider (None = all)
        
    Returns:
        1.0 if any relevant doc in top-k, else 0.0
    """
    k = k or len(retrieved_ids)
    top_k = retrieved_ids[:k]
    
    return 1.0 if any(doc_id in relevant_ids for doc_id in top_k) else 0.0


def calculate_all_metrics(
    retrieved_ids: List[str], 
    relevant_ids: Set[str],
    k_values: List[int] = None
) -> Dict[str, float]:
    """
    Calculate all metrics at multiple K values.
    
    Args:
        retrieved_ids: List of retrieved document IDs (in rank order)
        relevant_ids: Set of ground truth relevant document IDs
        k_values: List of K values to evaluate (default: [5, 10, 20])
        
    Returns:
        Dictionary of metric_name -> value
        Example: {"recall@5": 0.42, "precision@10": 0.68, ...}
    """
    if k_values is None:
        k_values = [5, 10, 20]
    
    # Ensure k_values don't exceed retrieved docs
    max_k = len(retrieved_ids) if retrieved_ids else 0
    k_values = [k for k in k_values if k <= max_k]
    
    if not k_values:
        k_values = [max_k] if max_k > 0 else [10]  # Default to at least one value
    
    metrics = {}
    
    # Metrics at each K
    for k in k_values:
        precision = precision_at_k(retrieved_ids, relevant_ids, k)
        recall = recall_at_k(retrieved_ids, relevant_ids, k)
        f1 = f1_score(precision, recall)
        ndcg = ndcg_at_k(retrieved_ids, relevant_ids, k)
        hit_rate = hit_rate_at_k(retrieved_ids, relevant_ids, k)
        
        metrics[f"precision@{k}"] = precision
        metrics[f"recall@{k}"] = recall
        metrics[f"f1@{k}"] = f1
        metrics[f"ndcg@{k}"] = ndcg
        metrics[f"hit_rate@{k}"] = hit_rate
    
    # Metrics independent of K
    metrics["mrr"] = mean_reciprocal_rank(retrieved_ids, relevant_ids)
    metrics["map"] = average_precision(retrieved_ids, relevant_ids)
    
    return metrics


def aggregate_metrics(all_metrics: List[Dict[str, float]]) -> Dict[str, float]:
    """
    Aggregate metrics across multiple queries (mean).
    
    Args:
        all_metrics: List of metric dictionaries from multiple queries
        
    Returns:
        Dictionary of averaged metrics
    """
    if not all_metrics:
        return {}
    
    aggregated = {}
    metric_names = all_metrics[0].keys()
    
    for metric_name in metric_names:
        values = [m[metric_name] for m in all_metrics if metric_name in m]
        aggregated[metric_name] = sum(values) / len(values) if values else 0.0
    
    return aggregated


def print_metrics(metrics: Dict[str, float], title: str = "Metrics"):
    """
    Pretty print metrics.
    
    Args:
        metrics: Dictionary of metric_name -> value
        title: Title to display
    """
    print(f"\n{'='*60}")
    print(f"{title:^60}")
    print(f"{'='*60}")
    
    # Group by metric type
    for metric_name in sorted(metrics.keys()):
        value = metrics[metric_name]
        print(f"  {metric_name:20s}: {value:6.4f}")
    
    print(f"{'='*60}\n")

