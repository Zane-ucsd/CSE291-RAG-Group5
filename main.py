"""
Main entry script for RAG Pipeline.
Run from project root directory.

Usage:
    python main.py                      # Run queries without evaluation
    python main.py --evaluate           # Run queries with evaluation
    python main.py interactive          # Interactive mode
"""

import sys
from pathlib import Path
import argparse

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from tests.main import main, interactive_mode

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RAG Pipeline - Main Entry Point")
    parser.add_argument(
        "mode",
        nargs="?",
        default="run",
        choices=["run", "interactive"],
        help="Mode: 'run' for batch queries, 'interactive' for interactive mode"
    )
    parser.add_argument(
        "--evaluate",
        action="store_true",
        help="Enable evaluation mode (calculate metrics against ground truth)"
    )
    
    args = parser.parse_args()
    
    if args.mode == "interactive":
        interactive_mode()
    else:
        main(evaluate=args.evaluate)

