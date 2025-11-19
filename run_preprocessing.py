"""
Main entry script for preprocessing pipeline.
Run from project root directory.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.preprocessing.run_preprocessing import main

if __name__ == "__main__":
    main()

