"""
Standalone evaluation script for RAG generation results using RAGAS.

This script evaluates the quality of generated responses using RAGAS metrics.
By default, only computes:
- faithfulness: Measures if the answer is grounded in the provided context
- answer_relevancy: Measures how relevant the answer is to the question

Optional metrics (not used by default):
- context_precision: Measures precision of the retrieved context
- context_recall: Measures recall of the retrieved context (requires ground truth)

Usage:
    python evaluate_generation.py <results_file> [--ground-truth <gt_file>] [--output <output_file>]
    
Examples:
    # Basic evaluation (default: faithfulness and answer_relevancy only)
    python evaluate_generation.py rag_results.json
    
    # Save results to file
    python evaluate_generation.py rag_results.json --output generation_evaluation.json
    
    # Specify metrics to compute (if you want to include context_precision/context_recall)
    python evaluate_generation.py rag_results.json --metrics faithfulness answer_relevancy context_precision
"""

import json
import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from src.validation.generation_evaluation import evaluate_generation_results
    RAGAS_AVAILABLE = True
except ImportError as e:
    RAGAS_AVAILABLE = False
    print(f"⚠️  RAGAS not available: {e}")
    print("   Install with: pip install ragas")


def main():
    """Main function for command-line usage"""
    
    if not RAGAS_AVAILABLE:
        print("❌ RAGAS evaluation is not available. Please install ragas first:")
        print("   pip install ragas")
        sys.exit(1)
    
    parser = argparse.ArgumentParser(
        description="Evaluate RAG generation results using RAGAS metrics"
    )
    
    parser.add_argument(
        "results_file",
        type=str,
        help="Path to RAG results JSON file"
    )
    
    parser.add_argument(
        "--ground-truth",
        type=str,
        default=None,
        help="Path to ground truth JSON file (optional, only needed if using context_recall metric)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Path to save evaluation results JSON (default: generation_evaluation.json)"
    )
    
    parser.add_argument(
        "--metrics",
        nargs="+",
        choices=["faithfulness", "answer_relevancy", "context_precision", "context_recall"],
        default=None,
        help="Metrics to compute (default: faithfulness and answer_relevancy only)"
    )
    
    parser.add_argument(
        "--use-ground-truth",
        action="store_true",
        help="Use ground truth for context_recall metric (requires --ground-truth)"
    )
    
    args = parser.parse_args()
    
    # Validate input file
    results_path = Path(args.results_file)
    if not results_path.exists():
        print(f"❌ Error: Results file not found: {results_path}")
        sys.exit(1)
    
    # Set default output file
    output_file = args.output or "generation_evaluation.json"
    
    # Validate ground truth file if provided
    ground_truth_file = args.ground_truth
    if args.use_ground_truth and not ground_truth_file:
        print("❌ Error: --use-ground-truth requires --ground-truth")
        sys.exit(1)
    
    if ground_truth_file:
        gt_path = Path(ground_truth_file)
        if not gt_path.exists():
            print(f"⚠️  Warning: Ground truth file not found: {gt_path}")
            print("   Continuing without ground truth...")
            ground_truth_file = None
            args.use_ground_truth = False
    
    try:
        # Run evaluation
        print(f"📂 Loading results from: {results_path}")
        if ground_truth_file:
            print(f"📂 Loading ground truth from: {ground_truth_file}")
        
        print(f"\n⏳ Running RAGAS evaluation...\n")
        
        eval_result = evaluate_generation_results(
            results_file=str(results_path),
            output_file=output_file,
            ground_truth_file=ground_truth_file,
            metrics=args.metrics,
            use_ground_truth=args.use_ground_truth
        )
        
        print(f"\n✅ Evaluation completed successfully!")
        print(f"💾 Results saved to: {output_file}")
        
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
        import traceback
        print(f"❌ Unexpected error: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()


