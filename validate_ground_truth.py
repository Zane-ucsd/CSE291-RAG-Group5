"""
Main entry script for ground truth validation.
Run from project root directory.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.validation.validate_ground_truth import main

if __name__ == "__main__":
    main()

