"""
RAGAS-based evaluation module for RAG generation results.

This module evaluates the quality of generated responses using RAGAS metrics:
- faithfulness: Measures if the answer is grounded in the provided context
- answer_relevancy: Measures how relevant the answer is to the question
- context_precision: Measures precision of the retrieved context
- context_recall: Measures recall of the retrieved context (requires ground truth)

Usage:
    from src.validation.generation_evaluation import evaluate_generation_results
    
    results = evaluate_generation_results(
        results_file="rag_results.json",
        output_file="generation_evaluation.json"
    )
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import os
import sys
import logging
import warnings

# Add src to path to import config
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.config import OPENAI_CONFIG

# Suppress ALL verbose logging from RAGAS and dependencies
logging.getLogger("ragas").setLevel(logging.CRITICAL)  # Only show critical errors
logging.getLogger("ragas.jobs").setLevel(logging.CRITICAL)  # Suppress job errors
logging.getLogger("openai").setLevel(logging.CRITICAL)
logging.getLogger("httpx").setLevel(logging.CRITICAL)
logging.getLogger("httpcore").setLevel(logging.CRITICAL)
logging.getLogger("elasticsearch").setLevel(logging.CRITICAL)  # Suppress ES INFO logs
logging.getLogger("urllib3").setLevel(logging.CRITICAL)
logging.getLogger("urllib3.connectionpool").setLevel(logging.CRITICAL)
logging.getLogger("requests").setLevel(logging.CRITICAL)
# Suppress all warnings
warnings.filterwarnings("ignore")


def _ensure_ragas_available():
    """Check if ragas is available and import necessary components."""
    try:
        from ragas import evaluate  # type: ignore
        from ragas.metrics import (  # type: ignore
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
        )
        from ragas.dataset_schema import EvaluationDataset  # type: ignore
        
        return {
            'evaluate': evaluate,
            'faithfulness': faithfulness,
            'answer_relevancy': answer_relevancy,
            'context_precision': context_precision,
            'context_recall': context_recall,
            'EvaluationDataset': EvaluationDataset,
        }
    except ImportError as e:
        raise ImportError(
            "Ragas is not installed or could not be imported.\n"
            "Install it with: pip install ragas\n"
            f"Import error: {e}"
        )


def prepare_evaluation_dataset(
    results_data: List[Dict[str, Any]],
    ground_truth_data: Optional[List[Dict[str, Any]]] = None,
    fetch_gt_content: bool = True
) -> List[Dict[str, Any]]:
    """
    Prepare evaluation dataset from RAG results.
    
    Args:
        results_data: List of RAG results, each containing:
            - query: User query
            - response: Generated response
            - documents: List of retrieved documents with 'content' field
        ground_truth_data: Optional ground truth data (not used by default metrics)
        fetch_gt_content: Whether to fetch actual content for ground truth documents
            (not needed for default metrics: faithfulness and answer_relevancy)
        
    Returns:
        List of samples formatted for RAGAS evaluation
    """
    # Build ground truth map if available
    gt_map = {}
    if ground_truth_data:
        gt_list = ground_truth_data if isinstance(ground_truth_data, list) else [ground_truth_data]
        
        # Try to fetch ground truth document content if requested
        gtv = None
        if fetch_gt_content:
            try:
                from .validate_ground_truth import GroundTruthValidator
                # Suppress logging before creating validator
                logging.getLogger("elasticsearch").setLevel(logging.CRITICAL)
                logging.getLogger("urllib3").setLevel(logging.CRITICAL)
                gtv = GroundTruthValidator(check_database=True, check_elasticsearch=False, check_llm=False)
            except Exception:
                gtv = None
        
        for entry in gt_list:
            query = entry.get('query')
            if query:
                relevant_ids = entry.get('relevant_ids', [])
                reference_text = ''
                
                # Try to fetch actual content
                if gtv and relevant_ids:
                    try:
                        docs = gtv.get_documents_by_ids(relevant_ids)
                        texts = [d.get('content', '') for d in docs if d.get('content')]
                        reference_text = '\n\n'.join(texts) if texts else ' '.join(str(id) for id in relevant_ids)
                    except Exception:
                        reference_text = ' '.join(str(id) for id in relevant_ids)
                else:
                    reference_text = ' '.join(str(id) for id in relevant_ids)
                
                gt_map[query] = {
                    'relevant_ids': relevant_ids,
                    'reference': reference_text
                }
    
    samples = []
    
    for item in results_data:
        query = item.get('query', '')
        response = item.get('response', '')
        documents = item.get('documents', [])
        
        if not query or not response:
            continue
        
        # Extract contexts from documents
        contexts = []
        for doc in documents:
            if isinstance(doc, dict):
                content = doc.get('content', '')
                if content:
                    contexts.append(content)
            elif isinstance(doc, str):
                contexts.append(doc)
        
        # Prepare sample - RAGAS expects specific column names
        sample = {
            'user_input': query,  # RAGAS expects 'user_input', not 'question'
            'response': response,  # RAGAS expects 'response', not 'answer'
            'retrieved_contexts': contexts,  # RAGAS expects 'retrieved_contexts', not 'contexts'
        }
        
        # Add reference (ground truth) if available
        # Note: RAGAS uses 'reference' not 'ground_truth' for context_precision and context_recall
        if query in gt_map:
            sample['reference'] = gt_map[query]['reference']
        
        samples.append(sample)
    
    return samples


def evaluate_generation_results(
    results_file: str,
    output_file: Optional[str] = None,
    ground_truth_file: Optional[str] = None,
    metrics: Optional[List[str]] = None,
    use_ground_truth: bool = False
) -> Dict[str, Any]:
    """
    Evaluate RAG generation results using RAGAS metrics.
    
    Args:
        results_file: Path to RAG results JSON file
        output_file: Optional path to save evaluation results
        ground_truth_file: Optional path to ground truth JSON file (not used by default metrics)
        metrics: List of metrics to compute. Options:
            - 'faithfulness': Answer grounded in context (default)
            - 'answer_relevancy': Answer relevance to question (default)
            - 'context_precision': Precision of retrieved context (not used by default)
            - 'context_recall': Recall of retrieved context (not used by default, requires ground truth)
            If None, defaults to ['faithfulness', 'answer_relevancy'] only
        use_ground_truth: Whether to use ground truth (not used by default metrics)
        
    Returns:
        Dictionary containing evaluation results
    """
    # Import ragas components
    ragas_components = _ensure_ragas_available()
    evaluate_fn = ragas_components['evaluate']
    EvaluationDataset = ragas_components['EvaluationDataset']
    
    # Load results
    results_path = Path(results_file)
    if not results_path.exists():
        raise FileNotFoundError(f"Results file not found: {results_path}")
    
    with open(results_path, 'r', encoding='utf-8') as f:
        results_data = json.load(f)
    
    if not isinstance(results_data, list):
        results_data = [results_data]
    
    # Load ground truth if provided
    ground_truth_data = None
    if ground_truth_file:
        gt_path = Path(ground_truth_file)
        if gt_path.exists():
            with open(gt_path, 'r', encoding='utf-8') as f:
                ground_truth_data = json.load(f)
        # Ground truth file not found, continuing without it
    
    # Prepare evaluation dataset
    samples = prepare_evaluation_dataset(
        results_data, 
        ground_truth_data,
        fetch_gt_content=use_ground_truth
    )
    
    if not samples:
        raise ValueError("No valid samples found in results data")
    
    # Determine metrics to use
    # Note: We only use faithfulness and answer_relevancy by default
    # context_precision and context_recall are not used to reduce evaluation cost and time
    if metrics is None:
        # Default metrics: only faithfulness and answer_relevancy
        # These metrics don't require ground truth and are sufficient for quality assessment
        metrics = ['faithfulness', 'answer_relevancy']
    
    # Map metric names to ragas metric objects
    # Only support faithfulness and answer_relevancy by default
    metric_objects = []
    for metric_name in metrics:
        if metric_name == 'faithfulness':
            metric_objects.append(ragas_components['faithfulness'])
        elif metric_name == 'answer_relevancy':
            metric_objects.append(ragas_components['answer_relevancy'])
        elif metric_name == 'context_precision':
            # context_precision is not used by default (can be enabled explicitly if needed)
            print(f"⚠️  Warning: context_precision is not enabled by default. Skipping.")
            continue
        elif metric_name == 'context_recall':
            # context_recall is not used by default (can be enabled explicitly if needed)
            print(f"⚠️  Warning: context_recall is not enabled by default. Skipping.")
            continue
    
    if not metric_objects:
        raise ValueError("No valid metrics selected")
    
    # Create evaluation dataset
    try:
        eval_dataset = EvaluationDataset.from_list(samples)
    except Exception as e:
        # Fallback to samples directly
        eval_dataset = samples
    
    # Configure evaluator LLM
    # Explicitly create an OpenAI LLM to avoid InstructorLLM compatibility issues
    # First, ensure API key is available (from env or config)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        # Try to get from project config
        api_key = OPENAI_CONFIG.get("api_key")
        if api_key:
            # Set environment variable so RAGAS can also use it
            os.environ["OPENAI_API_KEY"] = api_key
    
    evaluator_llm = None
    if api_key:
        try:
            from openai import OpenAI  # type: ignore
            from langchain_openai import ChatOpenAI  # type: ignore
            
            try:
                # Create OpenAI client
                client = OpenAI(api_key=api_key)
                
                # Create LangChain OpenAI LLM (RAGAS prefers this format)
                eval_model = os.getenv("RAGAS_EVAL_MODEL") or os.getenv("OPENAI_MODEL") or "gpt-4o-mini"
                evaluator_llm = ChatOpenAI(
                    model=eval_model,
                    api_key=api_key,
                    temperature=0
                )
            except ImportError:
                # langchain_openai not available, try ragas llm_factory
                try:
                    from ragas.llms import llm_factory  # type: ignore
                    eval_model = os.getenv("RAGAS_EVAL_MODEL") or os.getenv("OPENAI_MODEL") or "gpt-4o-mini"
                    evaluator_llm = llm_factory(eval_model, client=client)
                except Exception:
                    evaluator_llm = None
            except Exception:
                evaluator_llm = None
        except ImportError:
            # openai or langchain_openai not available
            evaluator_llm = None
    
    # Run evaluation (RAGAS will show progress bar automatically)
    # Only print minimal info
    print(f"\n   📊 Evaluating {len(samples)} samples with {len(metrics)} metrics...")
    
    try:
        # Use explicit LLM if available, otherwise let RAGAS handle it
        if evaluator_llm is not None:
            result = evaluate_fn(eval_dataset, metrics=metric_objects, llm=evaluator_llm)
        else:
            # Don't pass llm parameter - let RAGAS use its defaults
            # This should avoid InstructorLLM issues
            result = evaluate_fn(eval_dataset, metrics=metric_objects)
        
        # Convert result to dict if needed
        # RAGAS returns a Dataset with scores, we need to extract the metrics
        result_dict = {}
        
        try:
            # RAGAS typically returns a Dataset or pandas DataFrame
            # Try to convert to pandas DataFrame first (common RAGAS output format)
            df = None
            if hasattr(result, 'to_pandas'):
                df = result.to_pandas()
            elif hasattr(result, 'columns') and hasattr(result, '__iter__'):
                # It's already a pandas DataFrame
                import pandas as pd
                if isinstance(result, pd.DataFrame):
                    df = result
            
            if df is not None:
                # Extract metric scores (columns are metric names)
                data_columns = ['user_input', 'response', 'retrieved_contexts', 'reference', 'ground_truth']
                for col in df.columns:
                    if col not in data_columns:
                        # This is a metric column
                        scores = df[col].tolist()
                        # Calculate average, filtering out NaN and None
                        valid_scores = [
                            s for s in scores 
                            if s is not None and isinstance(s, (int, float)) 
                            and not (isinstance(s, float) and (s != s))  # Filter NaN
                        ]
                        if valid_scores:
                            result_dict[col] = {
                                'mean': float(sum(valid_scores) / len(valid_scores)),
                                'min': float(min(valid_scores)),
                                'max': float(max(valid_scores)),
                                'scores': [float(s) for s in valid_scores]
                            }
                        else:
                            result_dict[col] = {'mean': None, 'scores': []}
            # Try to_dict method
            elif hasattr(result, 'to_dict'):
                try:
                    result_dict = result.to_dict()
                except Exception:
                    pass
            # Try to access as dict
            elif isinstance(result, dict):
                result_dict = result
            # Try __dict__
            elif hasattr(result, '__dict__'):
                result_dict = result.__dict__
            
            # If still empty, try to extract from string representation
            if not result_dict:
                # Try to get metric names from the metrics list
                for metric_obj in metric_objects:
                    metric_name = getattr(metric_obj, 'name', None) or str(metric_obj)
                    result_dict[metric_name] = {'note': 'Could not extract score automatically'}
        except Exception as e:
            # Try to extract what we can
            result_dict = {'error': str(e), 'result_type': str(type(result))}
        
        # Clean up result_dict to ensure JSON serializability
        def make_serializable(obj):
            """Recursively make object JSON serializable"""
            if isinstance(obj, dict):
                return {k: make_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [make_serializable(item) for item in obj]
            elif isinstance(obj, (int, float, str, bool, type(None))):
                return obj
            elif hasattr(obj, '__dict__'):
                return make_serializable(obj.__dict__)
            else:
                return str(obj)
        
        result_dict = make_serializable(result_dict)
        
        # Save results
        if output_file:
            output_path = Path(output_file)
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(result_dict, f, ensure_ascii=False, indent=2)
            except Exception as e:
                # Try saving as text
                with open(output_path + '.txt', 'w', encoding='utf-8') as f:
                    f.write(str(result))
        
        # Print concise summary only
        print_evaluation_summary(result_dict, metrics, concise=True)
        
        return result_dict
        
    except Exception as e:
        import traceback
        print(f"❌ RAGAS evaluation failed: {e}")
        # Only print full traceback in verbose mode
        if os.getenv("RAGAS_VERBOSE", "false").lower() == "true":
            traceback.print_exc()
        raise


def print_evaluation_summary(result_dict: Dict[str, Any], metrics: List[str], concise: bool = False):
    """Print a summary of evaluation results."""
    if concise:
        print("\n" + "="*70)
        print("📊 RAGAS Evaluation Results")
        print("="*70)
    else:
        print("\n" + "-"*70)
        print("📊 RAGAS Evaluation Summary")
        print("-"*70)
    
    # Extract scores
    if isinstance(result_dict, dict):
        scores = {}
        
        # Check for direct metric keys with 'mean' field
        for metric in metrics:
            if metric in result_dict:
                value = result_dict[metric]
                if isinstance(value, (int, float)):
                    scores[metric] = value
                elif isinstance(value, dict):
                    # Try 'mean' first, then 'score'
                    if 'mean' in value and value['mean'] is not None:
                        scores[metric] = value['mean']
                    elif 'score' in value:
                        scores[metric] = value['score']
        
        # Print scores with emoji indicators
        if scores:
            for metric, score in scores.items():
                # Add emoji based on score
                if score >= 0.9:
                    emoji = "✅"
                elif score >= 0.7:
                    emoji = "⚠️"
                else:
                    emoji = "❌"
                print(f"  {emoji} {metric:23s}: {score:.4f}")
        else:
            # Fallback: print any numeric values
            for key, value in result_dict.items():
                if isinstance(value, (int, float)):
                    score = value
                    if score >= 0.9:
                        emoji = "✅"
                    elif score >= 0.7:
                        emoji = "⚠️"
                    else:
                        emoji = "❌"
                    print(f"  {emoji} {key:23s}: {score:.4f}")
                elif isinstance(value, dict) and 'mean' in value and value['mean'] is not None:
                    score = value['mean']
                    if score >= 0.9:
                        emoji = "✅"
                    elif score >= 0.7:
                        emoji = "⚠️"
                    else:
                        emoji = "❌"
                    print(f"  {emoji} {key:23s}: {score:.4f}")
    
    if concise:
        print("="*70)
    else:
        print("-"*70)

