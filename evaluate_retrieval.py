"""
Standalone evaluation script for RAG pipeline retrieval results

This script evaluates retrieval results against ground truth data.

Usage:
    python evaluate_retrieval.py <results_file> --ground-truth <gt_file> [--output <output_file>]
    
Examples:
    # Basic evaluation with default ground truth
    python evaluate_retrieval.py rag_results.json
    
    # With custom ground truth file
    python evaluate_retrieval.py rag_results.json --ground-truth ground_truth_example.json
    
    # Save results to file
    python evaluate_retrieval.py rag_results.json --output evaluation_report.json
    
    # Show detailed per-query report
    python evaluate_retrieval.py rag_results.json --show-per-query
"""

import json
import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.validation.retrieval_metrics import RetrievalEvaluator, RetrievalMetrics

# Optional ragas integration (import lazily)
try:
    from src.validation.ragas_integration import run_ragas_evaluation  # type: ignore
    RAGAS_AVAILABLE = True
except Exception:
    run_ragas_evaluation = None
    RAGAS_AVAILABLE = False


def main():
    """Main function for command-line usage"""
    
    parser = argparse.ArgumentParser(
        description="Evaluate RAG pipeline retrieval results against ground truth"
    )
    
    parser.add_argument(
        "results_file",
        type=str,
        help="Path to retrieval results JSON file"
    )
    
    parser.add_argument(
        "--ground-truth",
        type=str,
        default="ground_truth_example.json",
        help="Path to ground truth JSON file (default: ground_truth_example.json)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Path to save evaluation results JSON"
    )
    
    parser.add_argument(
        "--show-per-query",
        action="store_true",
        help="Show per-query detailed results"
    )
    
    parser.add_argument(
        "--top-n",
        type=int,
        default=5,
        help="Number of top/worst queries to show (default: 5)"
    )

    parser.add_argument(
        "--use-ragas",
        action="store_true",
        help="If set and ragas is installed, run Ragas evaluation as well"
    )
    
    args = parser.parse_args()
    
    # Validate input files
    results_path = Path(args.results_file)
    gt_path = Path(args.ground_truth)
    
    if not results_path.exists():
        print(f"❌ Error: Results file not found: {results_path}")
        sys.exit(1)
    
    if not gt_path.exists():
        print(f"❌ Error: Ground truth file not found: {gt_path}")
        sys.exit(1)
    
    try:
        # Initialize evaluator
        print(f"📂 Loading ground truth from: {gt_path}")
        evaluator = RetrievalEvaluator(ground_truth_file=str(gt_path))
        
        # Evaluate results
        print(f"📂 Loading retrieval results from: {results_path}")
        print(f"⏳ Evaluating retrieval results...\n")
        
        evaluation_result = evaluator.evaluate_retrieval_results(
            results_file=str(results_path),
            output_file=args.output
        )
        
        # Print report
        evaluator.print_evaluation_report(evaluation_result)
        
        # Print per-query report if requested
        if args.show_per_query:
            evaluator.print_per_query_report(evaluation_result, top_n=args.top_n)
        
        # Optionally run ragas evaluation
        if args.use_ragas:
            if not RAGAS_AVAILABLE:
                print("⚠️  Ragas integration not available. Install `ragas` to use this feature.")
            else:
                print("📦 Running Ragas evaluation (requires ragas package)...")
                try:
                    ragas_result = run_ragas_evaluation(
                        results_file=str(results_path),
                        ground_truth_file=str(gt_path),
                        output_file=args.output,
                    )
                    print("✅ Ragas evaluation completed. See output (if provided).")
                except Exception as e:
                    print(f"❌ Ragas evaluation failed: {e}")

        print("✅ Evaluation completed successfully!")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
