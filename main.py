"""
Main entry script for RAG Pipeline.
Run from project root directory.

Usage:
    python main.py                      # Run queries without evaluation
    python main.py --evaluate           # Run queries with evaluation
    python main.py interactive          # Interactive mode
    python main.py --process-pdf /path/to/file.pdf      # Process single PDF
    python main.py --process-pdf-dir /path/to/folder   # Process all PDFs in folder
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from tests.main import main, interactive_mode
from src.preprocessing.preprocessing import process_single_pdf_file, process_pdf_directory_files


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="RAG Pipeline - Main Entry Point",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                           # Run normal RAG pipeline
  python main.py --evaluate                # Run with evaluation
  python main.py interactive               # Interactive mode
  python main.py --process-pdf file.pdf   # Process single PDF
  python main.py --process-pdf-dir folder # Process all PDFs in folder
        """
    )
    
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
    parser.add_argument(
        "--process-pdf",
        type=str,
        help="Process a single PDF file and add to knowledge base"
    )
    parser.add_argument(
        "--process-pdf-dir",
        type=str,
        help="Process all PDF files in a directory and add to knowledge base"
    )
    
    args = parser.parse_args()
    
    # Handle PDF processing options (priority)
    if args.process_pdf:
        try:
            print("\n" + "="*70)
            print("PROCESSING SINGLE PDF FILE")
            print("="*70)
            num_chunks = process_single_pdf_file(args.process_pdf, auto_import_to_es=True)
            print("\n" + "="*70)
            print("PDF PROCESSING COMPLETED")
            print("="*70)
            print(f"  PDF: {Path(args.process_pdf).name}")
            print(f"  Chunks created: {num_chunks}")
            print(f"  Status: Saved to PostgreSQL and Elasticsearch")
            print("="*70)
        except Exception as e:
            print(f"\nError processing PDF: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    elif args.process_pdf_dir:
        try:
            print("\n" + "="*70)
            print("PROCESSING PDF DIRECTORY")
            print("="*70)
            result = process_pdf_directory_files(args.process_pdf_dir, auto_import_to_es=True)
            if result["success"]:
                print("\n" + "="*70)
                print("DIRECTORY PROCESSING COMPLETED")
                print("="*70)
                print(f"  Directory: {args.process_pdf_dir}")
                print(f"  PDFs processed: {result['successful']}/{result['total_pdfs']}")
                print(f"  Total chunks: {result['total_chunks']}")
                print(f"  Status: Saved to PostgreSQL and Elasticsearch")
                print("="*70)
            else:
                print(f"\nProcessing failed: {result.get('error', 'Unknown error')}")
                sys.exit(1)
        except Exception as e:
            print(f"\nError processing directory: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        # Run normal RAG pipeline
        if args.mode == "interactive":
            interactive_mode()
        else:
            main(evaluate=args.evaluate)

