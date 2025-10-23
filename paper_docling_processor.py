"""
STANDALONE PDF Vectorization Tool for Sports Papers
====================================================

🎯 Purpose:
    - Uses INDEPENDENT database (new_vector_db)
    - Does NOT affect existing striv_backend database
    - Processes PDFs from rag_papers directory
    - Category based on folder: badminton, cycling, running, soccer, swimming
    - Exports vectors as SQL dump

📁 Directory Structure:
    rag_papers/
        ├── badminton/  -> category: badminton
        ├── cycling/    -> category: cycling
        ├── running/    -> category: running
        ├── soccer/     -> category: soccer
        └── swimming/   -> category: swimming

🔧 Setup:
    1. Install dependencies:
       pip install docling openai psycopg2-binary pgvector sqlalchemy langchain-text-splitters python-dotenv

    2. Configure environment variables in .env:
       DB_USER=postgres
       DB_PASSWORD=your_password
       DB_HOST=localhost
       DB_PORT=5432
       OPENAI_API_KEY=your_openai_key

    3. Make sure PostgreSQL is running

🚀 Usage:
    python "paper_docling_processor copy.py"

    This will:
    1. Create new_vector_db database (if not exists)
    2. Enable pgvector extension
    3. Process all PDFs in rag_papers/*/
    4. Generate embeddings using OpenAI
    5. Export to new_vector_db_dump.sql

📊 Output:
    - rag_papers_md/           : Markdown files by category
    - new_vector_db_dump.sql   : SQL dump with all vectors
    - Database: new_vector_db with knowledge_base table

💾 Database Schema:
    knowledge_base:
        - id: auto-increment primary key
        - category: sport type (badminton/cycling/running/soccer/swimming)
        - content: original text content
        - embedding: 1536-dim vector from OpenAI
        - source: PDF filename

⚠️  Note: This is completely isolated from your existing striv_backend database!
"""

import os
import re
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode, TableStructureOptions
from docling.datamodel.base_models import InputFormat
from sqlalchemy import create_engine, Column, Integer, String, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from pgvector.sqlalchemy import Vector
from openai import OpenAI
import asyncio
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# STANDALONE DATABASE CONFIGURATION
# ==========================================
# This creates a NEW database, completely separate from striv_backend
STANDALONE_DB_NAME = "new_vector_db"
STANDALONE_DB_USER = os.getenv("DB_USER", "postgres")
STANDALONE_DB_PASSWORD = os.getenv("DB_PASSWORD", "")
STANDALONE_DB_HOST = os.getenv("DB_HOST", "localhost")
STANDALONE_DB_PORT = os.getenv("DB_PORT", "5432")

# Build connection URL for the new database
STANDALONE_DATABASE_URL = f"postgresql://{STANDALONE_DB_USER}:{STANDALONE_DB_PASSWORD}@{STANDALONE_DB_HOST}:{STANDALONE_DB_PORT}/{STANDALONE_DB_NAME}"

print(f"🔧 Standalone Database URL: {STANDALONE_DATABASE_URL}")

# Create standalone database engine and session
standalone_engine = create_engine(STANDALONE_DATABASE_URL)
StandaloneSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=standalone_engine)

# Define base for models
StandaloneBase = declarative_base()

# ==========================================
# STANDALONE KNOWLEDGE BASE MODEL
# ==========================================
class KnowledgeBase(StandaloneBase):
    """
    Standalone knowledge base table - does NOT interfere with existing database

    Schema:
        - id: Primary key
        - category: Sport type (badminton/cycling/running/soccer/swimming) based on folder
        - content: Original text content
        - embedding: 1536-dim vector from OpenAI
        - source: PDF filename
    """
    __tablename__ = "knowledge_base"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), nullable=False)  # Sport type from folder name
    content = Column(Text, nullable=False)          # Original text
    embedding = Column(Vector(1536), nullable=True) # OpenAI embedding vector
    source = Column(String(200), index=True)        # PDF filename


@dataclass
class PaperChunk:
    """Represents a chunk of paper for sports documents"""
    content: str  # Original text content
    source: str  # PDF filename
    category: str  # Sport type: badminton/cycling/running/soccer/swimming
    embedding: Optional[List[float]] = None


class PaperDoclingProcessor:
    """
    Simplified paper processor using docling
    Focused on clean content extraction for our minimal KnowledgeBase table
    """
    
    def __init__(self, db_session: Session, sport_category: str, output_dir: str = "rag_papers_md"):
        """
        Initialize the processor with enhanced Docling configuration

        Args:
            db_session: Database session (connected to new_vector_db)
            sport_category: Sport type (badminton/cycling/running/soccer/swimming)
            output_dir: Directory to save markdown files
        """
        self.db = db_session
        self.sport_category = sport_category  # Category based on folder
        self.output_dir = Path(output_dir) / sport_category
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.openai_client = OpenAI()

        # Enhanced Docling configuration for better table and text extraction
        self.converter = self._setup_enhanced_converter()
    
    def _setup_enhanced_converter(self) -> DocumentConverter:
        """
        Setup DocumentConverter with enhanced table and OCR processing
        Focus on extracting maximum text information without storing images
        
        Returns:
            Configured DocumentConverter instance
        """
        # Configure pipeline for better text extraction
        pipeline_options = PdfPipelineOptions(
            # Enhanced table processing
            do_table_structure=True,  # Enable advanced table structure recognition
            
            # OCR configuration - disabled for now due to tesserocr installation complexity
            do_ocr=False,  # Temporarily disabled - requires tesserocr installation
            
            # Disable image extraction (we only want text)
            generate_page_images=False,  # Don't extract full page images
            generate_picture_images=False,  # Don't extract figures/charts as images
            generate_table_images=False,  # Don't save tables as images
            
            # Performance settings
            artifacts_path=None,  # Use default model cache
            enable_remote_services=False  # Keep everything local for security
        )
        
        # Configure advanced table structure options for better accuracy
        pipeline_options.table_structure_options = TableStructureOptions(
            mode=TableFormerMode.ACCURATE,  # Use most accurate mode for complex tables
            do_cell_matching=True  # Enable cell matching for better table structure
        )
        
        # Create converter with enhanced configuration
        return DocumentConverter(
            allowed_formats=[InputFormat.PDF],  # Only process PDF files
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )
    
    def process_paper(self, pdf_path: str) -> Tuple[str, List[PaperChunk]]:
        """
        Process a PDF paper into markdown and chunks

        Args:
            pdf_path: Path to PDF file

        Returns:
            Tuple of (markdown_content, list_of_chunks)
        """
        pdf_path = Path(pdf_path)
        print(f"\n📄 Processing: {pdf_path.name}")

        # Convert PDF using enhanced Docling
        print("  Converting PDF to markdown...")
        result = self.converter.convert(str(pdf_path))

        # Get markdown output
        markdown_content = result.document.export_to_markdown()

        # Save markdown file
        md_filename = pdf_path.stem + ".md"
        md_path = self.output_dir / md_filename
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print(f"  ✅ Saved markdown to: {md_path}")

        # Create chunks (simplified - just filename and content)
        chunks = self._create_chunks(markdown_content, pdf_path.name)

        print(f"  📊 Created {len(chunks)} chunks")
        return markdown_content, chunks
    
    
    def _create_chunks(self, markdown: str, pdf_filename: str) -> List[PaperChunk]:
        """
        Create chunks from markdown content

        Args:
            markdown: Markdown content
            pdf_filename: Original PDF filename

        Returns:
            List of PaperChunk objects
        """
        chunks = []

        # Split markdown into sections
        sections = self._split_into_sections(markdown)

        for section_name, section_content in sections.items():
            # Skip references section
            if 'reference' in section_name.lower() or 'bibliography' in section_name.lower():
                continue

            # Skip empty sections
            if not section_content.strip():
                continue

            # Chunk the section (default max_size=2048)
            section_chunks = self._chunk_text(section_content)

            for chunk_text in section_chunks:
                # Clean the text
                chunk_text = self._clean_text(chunk_text)

                if len(chunk_text) < 100:  # Skip very short chunks
                    continue

                # Create chunk object with simplified schema
                chunk = PaperChunk(
                    content=chunk_text,
                    source=pdf_filename,  # Just the PDF filename
                    category=self.sport_category,  # Sport type from folder
                    embedding=None  # Will be filled later
                )
                chunks.append(chunk)

        return chunks
    
    def _split_into_sections(self, markdown: str) -> Dict[str, str]:
        """
        Split markdown into sections based on headings
        
        Args:
            markdown: Markdown content
            
        Returns:
            Dictionary mapping section names to content
        """
        sections = {}
        current_section = None
        current_content = []
        
        lines = markdown.split('\n')
        
        for line in lines:
            # Check if line is a heading
            if re.match(r'^#+\s+', line):
                # Save previous section if exists
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content)
                elif not current_section and current_content:
                    # Content before first heading - save as "Preamble" or detect common first sections
                    content_text = '\n'.join(current_content).strip()
                    if content_text:
                        # Try to detect if it's abstract based on content
                        if 'abstract' in content_text[:500].lower():
                            sections["Abstract"] = content_text
                        else:
                            sections["Preamble"] = content_text
                
                # Start new section
                current_section = re.sub(r'^#+\s+', '', line).strip()
                current_content = []
            else:
                current_content.append(line)
        
        # Save last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)
        elif not current_section and current_content:
            # Only content without any headings - treat as general content
            content_text = '\n'.join(current_content).strip()
            if content_text:
                sections["Content"] = content_text
        
        return sections
    
    def _chunk_text(self, text: str, max_size: int = 2048, chunk_overlap: int = 256) -> List[str]:
        """
        Text chunking using LangChain's RecursiveCharacterTextSplitter
        This provides better handling of document structure and context preservation
        
        Args:
            text: Text to chunk
            max_size: Maximum chunk size in characters
            chunk_overlap: Number of characters to overlap between chunks for context
            
        Returns:
            List of text chunks
        """
        if len(text) <= max_size:
            return [text]
        
        # Initialize the text splitter with smart defaults for academic papers
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=max_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
            separators=[
                "\n\n",  # Paragraph breaks (highest priority)
                "\n",    # Line breaks
                ". ",    # Sentence endings
                "! ",
                "? ",
                "; ",    # Clause separators
                ", ",    # Commas
                " ",     # Spaces
                ""       # Characters (last resort)
            ]
        )
        
        # Split the text
        chunks = text_splitter.split_text(text)
        
        return chunks
    
    def _clean_text(self, text: str) -> str:
        """
        Clean text by removing citations, formatting, and Unicode artifacts
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        # Remove problematic Unicode characters (corrupted superscripts/symbols)
        # These appear as ͷ, ͸, ͹, etc. in malformed PDFs
        unicode_mappings = {
            'ͷ': '1', '͸': '2', '͹': '3', 'ͺ': '4', 'ͻ': '5',
            'ͼ': '6', 'ͽ': '7', 'Ͷ': '0', 'Ϳ': '9',
            'ȋ': '(', 'Ȍ': ')', 'ʹ': "'", '͵': ',',
            'ͬ': '', 'ͭ': '', 'ͮ': '', 'ͯ': '', 'Ͱ': '', 'ͱ': '', 'Ͳ': '', 'ͳ': ''
        }
        
        for old_char, new_char in unicode_mappings.items():
            text = text.replace(old_char, new_char)
        
        # Remove other non-ASCII characters that are likely artifacts
        # Keep common accented characters and symbols
        import unicodedata
        cleaned_chars = []
        for char in text:
            # Keep ASCII, common Latin extensions, and important symbols
            if ord(char) < 128:  # ASCII
                cleaned_chars.append(char)
            elif unicodedata.category(char) in ['Ll', 'Lu', 'Lt', 'Lm', 'Lo', 'Nd', 'Pc', 'Pd', 'Ps', 'Pe', 'Pi', 'Pf', 'Po']:
                # Letters, numbers, and punctuation
                normalized = unicodedata.normalize('NFKD', char)
                ascii_char = normalized.encode('ascii', 'ignore').decode('ascii')
                if ascii_char:
                    cleaned_chars.append(ascii_char)
                elif char in 'àáäâèéëêìíïîòóöôùúüûñçÀÁÄÂÈÉËÊÌÍÏÎÒÓÖÔÙÚÜÛÑÇ':
                    # Keep common accented characters
                    cleaned_chars.append(char)
            elif char in ' \t\n\r':
                cleaned_chars.append(char)
        
        text = ''.join(cleaned_chars)
        
        # Remove citations like [1], [2,3], etc.
        text = re.sub(r'\[\d+(?:[-,]\d+)*\]', '', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove markdown formatting
        text = re.sub(r'\*+', '', text)  # Remove bold/italic
        text = re.sub(r'`+', '', text)  # Remove code formatting
        
        # Clean up common PDF artifacts
        text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)  # Add space between camelCase
        text = re.sub(r'\s*-\s*\n\s*', '', text)  # Remove hyphenation at line breaks
        
        return text.strip()
    
    
    async def create_embeddings_and_save(self, chunks: List[PaperChunk]):
        """
        Create embeddings for chunks and save to database

        Args:
            chunks: List of PaperChunk objects
        """
        print(f"\n💾 Creating embeddings and saving {len(chunks)} chunks to database...")

        # Batch processing for efficiency
        batch_size = 100
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]
            print(f"  Processing batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1}...")

            # Prepare texts for batch embedding
            texts = [chunk.content for chunk in batch]

            try:
                # Batch create embeddings
                response = self.openai_client.embeddings.create(
                    model="text-embedding-3-small",
                    input=texts
                )

                # Save each chunk with its embedding
                for chunk, emb_data in zip(batch, response.data):
                    kb_entry = KnowledgeBase(
                        category=chunk.category,
                        content=chunk.content,
                        embedding=emb_data.embedding,
                        source=chunk.source
                    )
                    self.db.add(kb_entry)

            except Exception as e:
                print(f"  ⚠️ Error in batch {i//batch_size + 1}: {e}")
                # Save without embeddings as fallback
                for chunk in batch:
                    kb_entry = KnowledgeBase(
                        category=chunk.category,
                        content=chunk.content,
                        embedding=None,
                        source=chunk.source
                    )
                    self.db.add(kb_entry)

        # Commit all chunks
        try:
            self.db.commit()
            print(f"  ✅ Successfully saved all chunks to database")
        except Exception as e:
            print(f"  ❌ Error saving to database: {e}")
            self.db.rollback()
            raise


async def process_single_paper(pdf_path: str, sport_category: str, db: Session):
    """
    Process a single paper

    Args:
        pdf_path: Path to PDF file
        sport_category: Sport type (badminton/cycling/running/soccer/swimming)
        db: Database session (connected to new_vector_db)

    Returns:
        Number of chunks created
    """
    # Initialize processor with sport category
    processor = PaperDoclingProcessor(db, sport_category)

    # Process the paper
    _, chunks = processor.process_paper(pdf_path)

    # Save to database with embeddings
    await processor.create_embeddings_and_save(chunks)

    return len(chunks)


async def process_all_rag_papers(base_dir: str = "rag_papers"):
    """
    Process all PDF papers from rag_papers directory structure

    Directory structure:
        rag_papers/
            ├── badminton/
            ├── cycling/
            ├── running/
            ├── soccer/
            └── swimming/

    Args:
        base_dir: Base directory containing sport folders
    """
    import time

    print("=" * 70)
    print("STANDALONE PDF VECTORIZATION FOR SPORTS PAPERS")
    print("=" * 70)
    print(f"Database: {STANDALONE_DB_NAME}")
    print(f"Source: {base_dir}/")
    print("=" * 70)

    base_path = Path(base_dir)

    if not base_path.exists():
        print(f"❌ Directory not found: {base_dir}")
        return

    # Sport categories (folder names)
    sport_categories = ["badminton", "cycling", "running", "soccer", "swimming"]

    # Create database session
    db = StandaloneSessionLocal()

    try:
        # Create tables if they don't exist
        print("\n📋 Creating database tables...")
        StandaloneBase.metadata.create_all(bind=standalone_engine)
        print("  ✅ Tables created/verified")

        total_chunks = 0
        total_papers = 0
        successful = 0
        failed = []

        # Process each sport category
        for category in sport_categories:
            category_path = base_path / category

            if not category_path.exists():
                print(f"\n⚠️  Skipping {category}: folder not found")
                continue

            # Get all PDF files in this category
            pdf_files = list(category_path.glob("*.pdf"))

            if not pdf_files:
                print(f"\n⚠️  No PDFs found in {category}/")
                continue

            print(f"\n{'='*70}")
            print(f"📁 Processing category: {category.upper()}")
            print(f"   Found {len(pdf_files)} PDF files")
            print(f"{'='*70}")

            for i, pdf_path in enumerate(pdf_files, 1):
                print(f"\n[{i}/{len(pdf_files)}] {pdf_path.name}")
                print("-" * 50)

                try:
                    start_time = time.time()
                    chunks_created = await process_single_paper(
                        str(pdf_path),
                        category,
                        db
                    )
                    elapsed = time.time() - start_time

                    total_chunks += chunks_created
                    total_papers += 1
                    successful += 1

                    print(f"  ✅ Success: {chunks_created} chunks in {elapsed:.1f}s")

                except Exception as e:
                    print(f"  ❌ Failed: {str(e)}")
                    failed.append(f"{category}/{pdf_path.name}")
                    continue

        # Print final summary
        print("\n" + "=" * 70)
        print("📊 PROCESSING SUMMARY")
        print("=" * 70)
        print(f"  Total papers processed: {successful}/{total_papers}")
        print(f"  Total chunks created: {total_chunks}")
        if successful > 0:
            print(f"  Average chunks per paper: {total_chunks/successful:.1f}")

        if failed:
            print(f"\n⚠️  Failed papers ({len(failed)}):")
            for name in failed:
                print(f"    - {name}")

    finally:
        db.close()

    print("\n✅ Processing complete!")
    return total_chunks


def export_sql_dump(output_file: str = "new_vector_db_dump.sql"):
    """
    Export the new_vector_db database to SQL dump file

    Args:
        output_file: Output SQL file name
    """
    print("\n" + "=" * 70)
    print("📦 EXPORTING SQL DUMP")
    print("=" * 70)

    try:
        # Build pg_dump command
        cmd = [
            "pg_dump",
            "-h", STANDALONE_DB_HOST,
            "-p", STANDALONE_DB_PORT,
            "-U", STANDALONE_DB_USER,
            "-d", STANDALONE_DB_NAME,
            "--column-inserts",  # Use INSERT statements
            "--no-owner",
            "--no-privileges",
            "-f", output_file
        ]

        # Set password env variable
        env = os.environ.copy()
        if STANDALONE_DB_PASSWORD:
            env["PGPASSWORD"] = STANDALONE_DB_PASSWORD

        print(f"  Exporting database: {STANDALONE_DB_NAME}")
        print(f"  Output file: {output_file}")

        # Execute pg_dump
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            # Get file size
            file_size = os.path.getsize(output_file)
            file_size_mb = file_size / (1024 * 1024)

            print(f"  ✅ Export successful!")
            print(f"     - Size: {file_size_mb:.2f} MB")

            # Count records
            db = StandaloneSessionLocal()
            count = db.query(KnowledgeBase).count()
            db.close()

            print(f"     - Records: {count}")
            print(f"\n📋 To import on another server:")
            print(f"   psql -U username -d target_db < {output_file}")

            return True
        else:
            print(f"  ❌ Export failed: {result.stderr}")
            return False

    except FileNotFoundError:
        print("  ❌ pg_dump not found. Install PostgreSQL client tools:")
        print("     macOS: brew install postgresql")
        return False
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        return False


def create_database():
    """
    Create the new_vector_db database if it doesn't exist
    """
    import psycopg2
    from psycopg2 import sql

    print("\n🔧 Creating database if not exists...")

    try:
        # Connect to postgres database to create new database
        conn = psycopg2.connect(
            dbname="postgres",
            user=STANDALONE_DB_USER,
            password=STANDALONE_DB_PASSWORD,
            host=STANDALONE_DB_HOST,
            port=STANDALONE_DB_PORT
        )
        conn.autocommit = True
        cur = conn.cursor()

        # Check if database exists
        cur.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (STANDALONE_DB_NAME,)
        )

        if not cur.fetchone():
            # Create database
            cur.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(STANDALONE_DB_NAME)
                )
            )
            print(f"  ✅ Created database: {STANDALONE_DB_NAME}")
        else:
            print(f"  ℹ️  Database already exists: {STANDALONE_DB_NAME}")

        # Create pgvector extension
        cur.close()
        conn.close()

        # Connect to the new database
        conn = psycopg2.connect(
            dbname=STANDALONE_DB_NAME,
            user=STANDALONE_DB_USER,
            password=STANDALONE_DB_PASSWORD,
            host=STANDALONE_DB_HOST,
            port=STANDALONE_DB_PORT
        )
        conn.autocommit = True
        cur = conn.cursor()

        # Create extension
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        print(f"  ✅ Enabled pgvector extension")

        cur.close()
        conn.close()

        return True

    except Exception as e:
        print(f"  ❌ Error creating database: {e}")
        return False


if __name__ == "__main__":
    import sys

    print("\n" + "=" * 70)
    print("STANDALONE PDF VECTORIZATION TOOL")
    print("=" * 70)

    # Step 1: Create database
    if not create_database():
        print("\n❌ Failed to create database. Exiting.")
        sys.exit(1)

    # Step 2: Process all papers
    print("\n")
    total_chunks = asyncio.run(process_all_rag_papers("rag_papers"))

    if total_chunks > 0:
        # Step 3: Export SQL dump
        print("\n")
        export_sql_dump("new_vector_db_dump.sql")

        print("\n" + "=" * 70)
        print("✨ ALL DONE!")
        print("=" * 70)
    else:
        print("\n⚠️  No chunks were created. Skipping export.")
        print("   Check if rag_papers directory exists and contains PDFs.")