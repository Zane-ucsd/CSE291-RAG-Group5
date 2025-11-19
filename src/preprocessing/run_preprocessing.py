"""
Main script to run the complete preprocessing pipeline (Step 2).

This script runs the full preprocessing workflow:
1. Database initialization (create database and tables)
2. PDF processing (convert PDFs to markdown and chunks)
3. Embedding generation (create vector embeddings)
4. Save to PostgreSQL database

Usage:
    python run_preprocessing.py [--base-dir rag_papers] [--categories badminton cycling]
"""

import argparse
import sys
from pathlib import Path
from .preprocessing import PreprocessingPipeline


def main():
    """
    Main function to run preprocessing pipeline.
    """
    parser = argparse.ArgumentParser(
        description="Run complete preprocessing pipeline (Step 2)"
    )
    parser.add_argument(
        "--base-dir",
        type=str,
        default="rag_papers",
        help="Base directory containing category folders (default: rag_papers)"
    )
    parser.add_argument(
        "--categories",
        nargs="+",
        default=None,
        help="Categories to process (default: all categories)"
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("🚀 PREPROCESSING PIPELINE - STEP 2")
    print("="*70)
    print(f"Base directory: {args.base_dir}")
    if args.categories:
        print(f"Categories: {', '.join(args.categories)}")
    else:
        print("Categories: all (badminton, cycling, running, soccer, swimming)")
    print("="*70)
    
    # Check if base directory exists
    base_path = Path(args.base_dir)
    if not base_path.exists():
        print(f"\n❌ Error: Directory not found: {args.base_dir}")
        print(f"   Please create the directory and add PDF files in category subfolders:")
        print(f"   {args.base_dir}/")
        print(f"     ├── badminton/")
        print(f"     ├── cycling/")
        print(f"     ├── running/")
        print(f"     ├── soccer/")
        print(f"     └── swimming/")
        sys.exit(1)
    
    # Initialize pipeline
    try:
        pipeline = PreprocessingPipeline()
    except Exception as e:
        print(f"\n❌ Error initializing pipeline: {e}")
        print("   Please check:")
        print("   1. All dependencies are installed (docling, openai, psycopg2-binary, etc.)")
        print("   2. PostgreSQL is running")
        print("   3. Configuration in config.py is correct")
        sys.exit(1)
    
    # Run preprocessing
    try:
        result = pipeline.process_all_pdfs(
            base_dir=args.base_dir,
            categories=args.categories
        )
        
        if result["success"]:
            print("\n" + "="*70)
            print("✅ PREPROCESSING COMPLETED SUCCESSFULLY!")
            print("="*70)
            print(f"  Total papers: {result['total_papers']}")
            print(f"  Successful: {result['successful']}")
            print(f"  Failed: {result['failed']}")
            print(f"  Total chunks: {result['total_chunks']}")
            print("\n📋 Next steps:")
            print("   1. Verify data in PostgreSQL database")
            print("   2. Run Elasticsearch import (optional)")
            print("   3. Test retrieval pipeline")
            sys.exit(0)
        else:
            print(f"\n❌ Preprocessing failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

