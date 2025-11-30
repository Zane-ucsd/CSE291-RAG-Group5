"""
Preprocessing module for RAG Pipeline.
Handles data preprocessing and database operations.
Includes PDF processing, text chunking, and database/Elasticsearch operations.
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional, Tuple, TYPE_CHECKING
from pathlib import Path
import psycopg2
from psycopg2 import sql
from elasticsearch import Elasticsearch, helpers
import ujson
import numpy as np
import re
import unicodedata
from ..config import PG_CONFIG, ES_CONFIG, OPENAI_CONFIG, DATA_CONFIG
from ..embedding import EmbeddingGenerator

# Optional imports for PDF processing
try:
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode, TableStructureOptions
    from docling.datamodel.base_models import InputFormat
    from docling.exceptions import ConversionError
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False
    DocumentConverter = None  # Placeholder for type hints
    PdfFormatOption = None
    PdfPipelineOptions = None
    TableFormerMode = None
    TableStructureOptions = None
    InputFormat = None
    ConversionError = Exception  # Fallback exception type
    print("Warning: Docling not available. PDF processing will be disabled.")

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("Warning: LangChain not available. Using simple text splitting.")


class DataPreprocessor:
    """
    Preprocess data and import into PostgreSQL and Elasticsearch.
    """
    
    def __init__(self):
        """
        Initialize preprocessor with database connections.
        """
        self.pg_config = PG_CONFIG
        self.es_config = ES_CONFIG
        self.embedding_gen = EmbeddingGenerator()
    
    def get_pg_connection(self):
        """
        Get PostgreSQL connection.
        
        Returns:
            PostgreSQL connection object
        """
        return psycopg2.connect(
            dbname=self.pg_config["dbname"],
            user=self.pg_config["user"],
            password=self.pg_config["password"],
            host=self.pg_config["host"],
            port=self.pg_config["port"]
        )
    
    def get_es_connection(self):
        """
        Get Elasticsearch connection.
        
        Returns:
            Elasticsearch client
        """
        # Build connection parameters
        es_params = {"hosts": [self.es_config["host"]]}
        
        # Add optional auth parameters if present
        if "api_key" in self.es_config:
            es_params["api_key"] = self.es_config["api_key"]
        if "ca_certs" in self.es_config:
            es_params["ca_certs"] = self.es_config["ca_certs"]
        
        return Elasticsearch(**es_params)
    
    def create_es_index(self, index_name: Optional[str] = None, force_recreate: bool = False):
        """
        Create Elasticsearch index with proper mappings.
        
        Args:
            index_name: Index name (defaults to config)
            force_recreate: Whether to delete existing index
        """
        index_name = index_name or self.es_config["index_name"]
        es = self.get_es_connection()
        
        # Delete existing index if needed
        if force_recreate and es.indices.exists(index=index_name):
            es.indices.delete(index=index_name)
            print(f"Deleted existing index: {index_name}")
        
        # Create index
        if not es.indices.exists(index=index_name):
            es.indices.create(
                index=index_name,
                mappings={
                    "properties": {
                        "id": {"type": "keyword"},
                        "category": {"type": "keyword"},
                        "source": {"type": "keyword"},
                        "content": {"type": "text"},
                        "embedding": {
                            "type": "dense_vector",
                            "dims": OPENAI_CONFIG["embedding_dim"],
                            "index": True,
                            "similarity": "cosine"
                        }
                    }
                }
            )
            print(f"Created index: {index_name}")
        else:
            print(f"Index already exists: {index_name}")
    
    def import_from_postgres_to_elasticsearch(
        self,
        batch_size: int = 1000,
        index_name: Optional[str] = None
    ):
        """
        Import data from PostgreSQL to Elasticsearch with embeddings.
        
        Args:
            batch_size: Batch size for bulk operations
            index_name: Index name (defaults to config)
        """
        index_name = index_name or self.es_config["index_name"]
        es = self.get_es_connection()
        
        # Get PostgreSQL connection
        pg_conn = self.get_pg_connection()
        pg_cur = pg_conn.cursor(name="kb_cursor")
        pg_cur.itersize = batch_size
        pg_cur.execute("SELECT id, category, content, embedding, source FROM knowledge_base;")
        
        actions = []
        count = 0
        
        print("Starting data import...")
        
        for row in pg_cur:
            _id, category, content, embedding_data, source = row
            
            # Skip if no embedding
            if embedding_data is None:
                continue
            
            # Parse embedding from PostgreSQL vector type
            # Vector type returns as string array format: "[-0.042, 0.123, ...]"
            if isinstance(embedding_data, str):
                # Parse array string format: "[-0.042, 0.123, ...]"
                import ast
                try:
                    emb = ast.literal_eval(embedding_data)
                except:
                    # Try JSON format as fallback
                    emb = ujson.loads(embedding_data)
            else:
                # Already a list/array
                emb = embedding_data
                
            # Convert to float array
            v = np.array(emb, dtype=np.float32)
            
            # Note: Vectors are already L2 normalized in database
            # No need to normalize again
            
            # Prepare action
            actions.append({
                "_op_type": "index",
                "_index": index_name,
                "_id": str(_id),
                "id": str(_id),
                "category": category.lower() if category else None,
                "content": content,
                "source": source,
                "embedding": v.tolist()
            })
            
            # Bulk insert when batch is full
            if len(actions) >= batch_size:
                helpers.bulk(es, actions)
                count += len(actions)
                print(f"Imported {count} documents")
                actions.clear()
        
        # Process remaining
        if actions:
            helpers.bulk(es, actions)
            count += len(actions)
        
        pg_cur.close()
        pg_conn.close()
        
        print(f"Import completed. Total: {count} documents")


class PDFProcessor:
    """
    Process PDF files into text chunks using Docling.
    """
    
    def __init__(self, output_dir: str = "rag_papers_md"):
        """
        Initialize PDF processor.
        
        Args:
            output_dir: Directory to save markdown files
        """
        if not DOCLING_AVAILABLE:
            raise ImportError("Docling is required for PDF processing. Install with: pip install docling")
        
        self.output_dir = Path(output_dir)
        self.converter = self._setup_converter()
    
    def _setup_converter(self):
        """
        Setup DocumentConverter with enhanced configuration.
        Uses more tolerant settings to handle various PDF formats.
        
        Returns:
            Configured DocumentConverter instance
        """
        # Use more tolerant pipeline options for problematic PDFs
        pipeline_options = PdfPipelineOptions(
            do_table_structure=True,
            do_ocr=False,  # Can enable if needed for scanned PDFs
            generate_page_images=False,
            generate_picture_images=False,
            generate_table_images=False,
            artifacts_path=None,
            enable_remote_services=False
        )
        
        # Use FAST mode instead of ACCURATE for better compatibility
        # ACCURATE mode may be too strict for some PDFs
        pipeline_options.table_structure_options = TableStructureOptions(
            mode=TableFormerMode.FAST,  # Changed from ACCURATE for better compatibility
            do_cell_matching=False  # Disable for faster, more tolerant processing
        )
        
        return DocumentConverter(
            allowed_formats=[InputFormat.PDF],
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )
    
    def process_pdf(self, pdf_path: str, category: str) -> Tuple[str, List[str]]:
        """
        Process a PDF file into markdown and text chunks.
        
        Args:
            pdf_path: Path to PDF file
            category: Sport category (badminton/cycling/running/soccer/swimming)
            
        Returns:
            Tuple of (markdown_content, list_of_text_chunks)
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            ValueError: If file is not a valid PDF or cannot be processed
        """
        pdf_path = Path(pdf_path)
        
        # Validate file exists
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        if not pdf_path.suffix.lower() == '.pdf':
            raise ValueError(f"Not a PDF file: {pdf_path}")
        
        print(f"Processing: {pdf_path.name}")
        
        # Convert PDF to markdown with error handling
        try:
            # Try convert_all first (may be more tolerant)
            try:
                results = list(self.converter.convert_all([str(pdf_path)]))
                if results and hasattr(results[0], 'document'):
                    result = results[0]
                else:
                    # Fall back to regular convert
                    result = self.converter.convert(str(pdf_path))
            except (ConversionError, AttributeError, IndexError):
                # Fall back to regular convert method
                result = self.converter.convert(str(pdf_path))
        except ConversionError as e:
            # Handle docling conversion errors with detailed messages
            error_msg = str(e)
            
            if "could not find the page-dimensions" in error_msg:
                raise ValueError(
                    f"PDF format error in {pdf_path.name}: Unable to parse page dimensions. "
                    f"This usually indicates:\n"
                    f"  - Corrupted PDF file\n"
                    f"  - Non-standard PDF format\n"
                    f"  - PDF created with incompatible software\n"
                    f"\nTry re-saving the PDF with a different tool or check if the file is corrupted."
                ) from e
            elif "could not find" in error_msg.lower():
                raise ValueError(
                    f"PDF parsing error in {pdf_path.name}: Missing required PDF structure. "
                    f"This may indicate a corrupted or incomplete PDF file."
                ) from e
            else:
                # Generic conversion error
                raise ValueError(
                    f"PDF conversion failed for {pdf_path.name}. "
                    f"Error: {error_msg[:300]}"
                ) from e
        except Exception as e:
            # Handle other unexpected errors
            raise RuntimeError(
                f"Unexpected error processing PDF {pdf_path.name}: {str(e)}"
            ) from e
        
        markdown_content = result.document.export_to_markdown()
        
        # Save markdown file
        output_category_dir = self.output_dir / category
        output_category_dir.mkdir(parents=True, exist_ok=True)
        
        md_filename = pdf_path.stem + ".md"
        md_path = output_category_dir / md_filename
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print(f"  Saved markdown to: {md_path}")
        
        # Create text chunks
        chunks = self._create_chunks(markdown_content)
        print(f"  Created {len(chunks)} chunks")
        
        return markdown_content, chunks
    
    def _create_chunks(self, markdown: str) -> List[str]:
        """
        Create text chunks from markdown content.
        
        Args:
            markdown: Markdown content
            
        Returns:
            List of text chunks
        """
        # Split into sections
        sections = self._split_into_sections(markdown)
        all_chunks = []
        
        for section_name, section_content in sections.items():
            # Skip references
            if 'reference' in section_name.lower() or 'bibliography' in section_name.lower():
                continue
            
            if not section_content.strip():
                continue
            
            # Chunk the section
            section_chunks = self._chunk_text(section_content)
            
            for chunk_text in section_chunks:
                # Clean the text
                chunk_text = self._clean_text(chunk_text)
                
                if len(chunk_text) >= 100:  # Skip very short chunks
                    all_chunks.append(chunk_text)
        
        return all_chunks
    
    def _split_into_sections(self, markdown: str) -> Dict[str, str]:
        """
        Split markdown into sections based on headings.
        
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
            if re.match(r'^#+\s+', line):
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content)
                elif not current_section and current_content:
                    content_text = '\n'.join(current_content).strip()
                    if content_text:
                        if 'abstract' in content_text[:500].lower():
                            sections["Abstract"] = content_text
                        else:
                            sections["Preamble"] = content_text
                
                current_section = re.sub(r'^#+\s+', '', line).strip()
                current_content = []
            else:
                current_content.append(line)
        
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)
        elif not current_section and current_content:
            content_text = '\n'.join(current_content).strip()
            if content_text:
                sections["Content"] = content_text
        
        return sections
    
    def _chunk_text(self, text: str, max_size: int = 2048, chunk_overlap: int = 256) -> List[str]:
        """
        Chunk text using LangChain or simple splitting.
        
        Args:
            text: Text to chunk
            max_size: Maximum chunk size
            chunk_overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        if len(text) <= max_size:
            return [text]
        
        if LANGCHAIN_AVAILABLE:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=max_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
                is_separator_regex=False,
                separators=["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " ", ""]
            )
            return text_splitter.split_text(text)
        else:
            # Simple splitting fallback
            chunks = []
            for i in range(0, len(text), max_size - chunk_overlap):
                chunks.append(text[i:i + max_size])
            return chunks
    
    def _clean_text(self, text: str) -> str:
        """
        Clean text by removing artifacts and formatting.
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        # Remove problematic Unicode characters
        unicode_mappings = {
            'ͷ': '1', '͸': '2', '͹': '3', 'ͺ': '4', 'ͻ': '5',
            'ͼ': '6', 'ͽ': '7', 'Ͷ': '0', 'Ϳ': '9',
            'ȋ': '(', 'Ȍ': ')', 'ʹ': "'", '͵': ',',
        }
        
        for old_char, new_char in unicode_mappings.items():
            text = text.replace(old_char, new_char)
        
        # Remove citations
        text = re.sub(r'\[\d+(?:[-,]\d+)*\]', '', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove markdown formatting
        text = re.sub(r'\*+', '', text)
        text = re.sub(r'`+', '', text)
        
        return text.strip()


class DatabaseInitializer:
    """
    Initialize PostgreSQL database and pgvector extension.
    """
    
    def __init__(self):
        """
        Initialize database initializer.
        """
        self.pg_config = PG_CONFIG
    
    def create_database(self, db_name: Optional[str] = None) -> bool:
        """
        Create database if it doesn't exist.
        
        Args:
            db_name: Database name (defaults to config)
            
        Returns:
            True if successful
        """
        db_name = db_name or self.pg_config["dbname"]
        
        try:
            # Connect to postgres database
            conn = psycopg2.connect(
                dbname="postgres",
                user=self.pg_config["user"],
                password=self.pg_config["password"],
                host=self.pg_config["host"],
                port=self.pg_config["port"]
            )
            conn.autocommit = True
            cur = conn.cursor()
            
            # Check if database exists
            cur.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (db_name,)
            )
            
            if not cur.fetchone():
                cur.execute(
                    sql.SQL("CREATE DATABASE {}").format(
                        sql.Identifier(db_name)
                    )
                )
                print(f"  Created database: {db_name}")
            else:
                print(f"  Database already exists: {db_name}")
            
            cur.close()
            conn.close()
            
            # Enable pgvector extension
            conn = psycopg2.connect(
                dbname=db_name,
                user=self.pg_config["user"],
                password=self.pg_config["password"],
                host=self.pg_config["host"],
                port=self.pg_config["port"]
            )
            conn.autocommit = True
            cur = conn.cursor()
            
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            print(f"  Enabled pgvector extension")
            
            cur.close()
            conn.close()
            
            return True
        
        except Exception as e:
            print(f"  Error creating database: {e}")
            return False
    
    def create_tables(self, db_name: Optional[str] = None) -> bool:
        """
        Create knowledge_base table if it doesn't exist.
        
        Args:
            db_name: Database name (defaults to config)
            
        Returns:
            True if successful
        """
        db_name = db_name or self.pg_config["dbname"]
        
        try:
            conn = psycopg2.connect(
                dbname=db_name,
                user=self.pg_config["user"],
                password=self.pg_config["password"],
                host=self.pg_config["host"],
                port=self.pg_config["port"]
            )
            cur = conn.cursor()
            
            # Create knowledge_base table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_base (
                    id SERIAL PRIMARY KEY,
                    category VARCHAR(50),
                    content TEXT NOT NULL,
                    embedding vector(1536),
                    source VARCHAR(200)
                )
            """)
            
            # Create index on category and source
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_knowledge_base_category 
                ON knowledge_base(category)
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_knowledge_base_source 
                ON knowledge_base(source)
            """)
            
            conn.commit()
            cur.close()
            conn.close()
            
            print(f"  Created/verified knowledge_base table")
            return True
        
        except Exception as e:
            print(f"  Error creating tables: {e}")
            return False


class PreprocessingPipeline:
    """
    Complete preprocessing pipeline that integrates all steps:
    1. Database initialization
    2. PDF processing and chunking
    3. Embedding generation
    4. Saving to PostgreSQL
    5. Automatic import to Elasticsearch
    """
    
    def __init__(self, auto_import_to_es: bool = True):
        """
        Initialize preprocessing pipeline.
        
        Args:
            auto_import_to_es: Whether to automatically import to Elasticsearch after processing
        """
        self.db_init = DatabaseInitializer()
        self.pdf_processor = PDFProcessor()
        self.embedding_gen = EmbeddingGenerator()
        self.data_preprocessor = DataPreprocessor()
        self.pg_config = PG_CONFIG
        self.auto_import_to_es = auto_import_to_es
    
    def process_and_save_chunks(
        self,
        chunks: List[str],
        category: Optional[str],
        source: str,
        batch_size: int = 100
    ) -> int:
        """
        Generate embeddings for chunks and save to PostgreSQL.
        
        Args:
            chunks: List of text chunks
            category: Sport category (can be None for new PDFs)
            source: PDF source filename
            batch_size: Batch size for embedding generation
            
        Returns:
            Number of chunks saved
        """
        db_name = self.pg_config["dbname"]
        conn = psycopg2.connect(
            dbname=db_name,
            user=self.pg_config["user"],
            password=self.pg_config["password"],
            host=self.pg_config["host"],
            port=self.pg_config["port"]
        )
        cur = conn.cursor()
        
        try:
            print(f"\nGenerating embeddings and saving {len(chunks)} chunks...")
            
            # Process in batches
            total_saved = 0
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                batch_num = i // batch_size + 1
                total_batches = (len(chunks) - 1) // batch_size + 1
                
                print(f"  Processing batch {batch_num}/{total_batches}...")
                
                try:
                    # Generate embeddings for batch
                    embeddings = self.embedding_gen.batch_generate(
                        batch,
                        batch_size=batch_size,
                        normalize=DATA_CONFIG["embedding_normalize"]
                    )
                    
                    # Save to database (with duplicate check)
                    batch_saved = 0
                    for chunk_text, embedding in zip(batch, embeddings):
                        # Check if this chunk already exists (same source and content)
                        cur.execute("""
                            SELECT COUNT(*) FROM knowledge_base 
                            WHERE source = %s AND content = %s
                        """, (source, chunk_text))
                        
                        exists = cur.fetchone()[0] > 0
                        
                        if exists:
                            continue  # Skip duplicate chunk
                        
                        # Convert embedding to PostgreSQL vector format: '[1,2,3]'
                        embedding_str = '[' + ','.join(map(str, embedding)) + ']'
                        
                        cur.execute("""
                            INSERT INTO knowledge_base (category, content, embedding, source)
                            VALUES (%s, %s, %s::vector, %s)
                        """, (category, chunk_text, embedding_str, source))
                        batch_saved += 1
                    
                    conn.commit()
                    total_saved += batch_saved
                    skipped = len(batch) - batch_saved
                    if skipped > 0:
                        print(f"  Saved batch {batch_num}: {batch_saved} new chunks, {skipped} duplicates skipped")
                    else:
                        print(f"  Saved batch {batch_num}: {batch_saved} chunks")
                
                except Exception as e:
                    print(f"  Warning: Error in batch {batch_num}: {e}")
                    conn.rollback()
                    # Try to save without embeddings as fallback (with duplicate check)
                    for chunk_text in batch:
                        try:
                            # Check if this chunk already exists
                            cur.execute("""
                                SELECT COUNT(*) FROM knowledge_base 
                                WHERE source = %s AND content = %s
                            """, (source, chunk_text))
                            
                            exists = cur.fetchone()[0] > 0
                            if exists:
                                continue  # Skip duplicate chunk
                            
                            cur.execute("""
                                INSERT INTO knowledge_base (category, content, source)
                                VALUES (%s, %s, %s)
                            """, (category, chunk_text, source))
                        except Exception as e2:
                            print(f"    Warning: Failed to save chunk: {e2}")
                    conn.commit()
            
            print(f"  Successfully saved {total_saved} chunks to database")
            return total_saved
        
        except Exception as e:
            print(f"  Error saving chunks: {e}")
            conn.rollback()
            raise
        
        finally:
            cur.close()
            conn.close()
    
    def process_single_pdf(
        self,
        pdf_path: str,
        category: Optional[str] = None
    ) -> int:
        """
        Process a single PDF file through the complete pipeline.
        
        Args:
            pdf_path: Path to PDF file
            category: Sport category (optional, defaults to None for new PDFs)
            
        Returns:
            Number of chunks created and saved
        """
        print(f"\n{'='*70}")
        print(f"Processing: {Path(pdf_path).name}")
        if category:
            print(f"   Category: {category}")
        else:
            print(f"   Category: None (new PDF)")
        print(f"{'='*70}")
        
        # Ensure database and tables exist
        self.db_init.create_database()
        self.db_init.create_tables()
        
        # Use "general" as default category for PDF processing (folder structure)
        # But save as None in database for new PDFs
        pdf_category = category or "general"
        
        # Step 1: Process PDF to markdown and chunks
        _, chunks = self.pdf_processor.process_pdf(pdf_path, pdf_category)
        
        if not chunks:
            print("  Warning: No chunks created from PDF")
            return 0
        
        # Step 2: Generate embeddings and save to database
        source = Path(pdf_path).name
        num_saved = self.process_and_save_chunks(chunks, category, source)
        
        # Step 3: Auto-import to Elasticsearch if enabled
        if self.auto_import_to_es and num_saved > 0:
            print(f"\nAuto-importing new chunks to Elasticsearch...")
            try:
                # Import only the newly added chunks (by source)
                self._import_new_chunks_to_es(source)
                print(f"  Successfully imported to Elasticsearch")
            except Exception as e:
                print(f"  Warning: Error importing to Elasticsearch: {e}")
                import traceback
                traceback.print_exc()
        
        return num_saved
    
    def process_single_pdf_new(
        self,
        pdf_path: str
    ) -> int:
        """
        Process a single new PDF file (no category).
        This is the main method for processing new PDFs during evaluation.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Number of chunks created and saved
        """
        return self.process_single_pdf(pdf_path, category=None)
    
    def process_pdf_directory(
        self,
        directory_path: str
    ) -> Dict[str, Any]:
        """
        Process all PDF files in a directory (no category structure).
        This is the main method for processing new PDF folders during evaluation.
        
        Args:
            directory_path: Path to directory containing PDF files
            
        Returns:
            Dictionary with processing statistics
        """
        dir_path = Path(directory_path)
        
        if not dir_path.exists():
            print(f"Error: Directory not found: {directory_path}")
            return {"success": False, "error": f"Directory not found: {directory_path}"}
        
        if not dir_path.is_dir():
            print(f"Error: Not a directory: {directory_path}")
            return {"success": False, "error": f"Not a directory: {directory_path}"}
        
        # Find all PDF files in directory
        pdf_files = list(dir_path.glob("*.pdf"))
        
        if not pdf_files:
            print(f"Warning: No PDF files found in: {directory_path}")
            return {"success": False, "error": "No PDF files found"}
        
        print("\n" + "="*70)
        print("PROCESSING PDF DIRECTORY")
        print("="*70)
        print(f"Directory: {directory_path}")
        print(f"Found {len(pdf_files)} PDF files")
        print("="*70)
        
        # Ensure database and tables exist
        print("\nEnsuring database is initialized...")
        self.db_init.create_database()
        self.db_init.create_tables()
        
        # Ensure Elasticsearch index exists
        if self.auto_import_to_es:
            print("\nEnsuring Elasticsearch index exists...")
            try:
                self.data_preprocessor.create_es_index(force_recreate=False)
            except Exception as e:
                print(f"  Warning: Could not create ES index: {e}")
        
        total_chunks = 0
        successful = 0
        failed = []
        
        for i, pdf_path in enumerate(pdf_files, 1):
            print(f"\n[{i}/{len(pdf_files)}] {pdf_path.name}")
            print("-" * 50)
            
            try:
                chunks_created = self.process_single_pdf_new(str(pdf_path))
                total_chunks += chunks_created
                successful += 1
                print(f"  Success: {chunks_created} chunks")
            
            except Exception as e:
                print(f"  Failed: {str(e)}")
                failed.append(pdf_path.name)
                import traceback
                traceback.print_exc()
                continue
        
        # Summary
        print("\n" + "="*70)
        print("PROCESSING SUMMARY")
        print("="*70)
        print(f"  Total PDFs processed: {successful}/{len(pdf_files)}")
        print(f"  Total chunks created: {total_chunks}")
        if successful > 0:
            print(f"  Average chunks per PDF: {total_chunks/successful:.1f}")
        
        if failed:
            print(f"\nWarning: Failed PDFs ({len(failed)}):")
            for name in failed:
                print(f"    - {name}")
        
        return {
            "success": True,
            "total_pdfs": len(pdf_files),
            "successful": successful,
            "failed": len(failed),
            "total_chunks": total_chunks,
            "failed_pdfs": failed
        }
    
    def _import_new_chunks_to_es(self, source: str):
        """
        Import newly added chunks (by source) to Elasticsearch.
        This is more efficient than importing all data.
        
        Args:
            source: Source filename to import
        """
        # Get ES connection
        es = self.data_preprocessor.get_es_connection()
        index_name = self.data_preprocessor.es_config["index_name"]
        
        # Get PostgreSQL connection
        pg_conn = self.get_pg_connection()
        pg_cur = pg_conn.cursor(name="new_chunks_cursor")
        pg_cur.itersize = 100
        
        # Query only chunks from this source
        pg_cur.execute(
            "SELECT id, category, content, embedding, source FROM knowledge_base WHERE source = %s",
            (source,)
        )
        
        actions = []
        count = 0
        
        for row in pg_cur:
            _id, category, content, embedding_data, source_file = row
            
            if embedding_data is None:
                continue
            
            # Parse embedding
            if isinstance(embedding_data, str):
                import ast
                try:
                    emb = ast.literal_eval(embedding_data)
                except:
                    emb = ujson.loads(embedding_data)
            else:
                emb = embedding_data
            
            v = np.array(emb, dtype=np.float32)
            
            # Check if document already exists in ES
            # Note: PostgreSQL handles duplicate inserts, but ES may have been imported before
            # So we still need to check ES existence to avoid re-importing
            if es.exists(index=index_name, id=str(_id)):
                continue  # Skip if already exists in ES
            
            actions.append({
                "_op_type": "index",
                "_index": index_name,
                "_id": str(_id),
                "id": str(_id),
                "category": category.lower() if category else None,
                "content": content,
                "source": source_file,
                "embedding": v.tolist()
            })
            
            if len(actions) >= 100:
                helpers.bulk(es, actions)
                count += len(actions)
                actions.clear()
        
        if actions:
            helpers.bulk(es, actions)
            count += len(actions)
        
        pg_cur.close()
        pg_conn.close()
        
        if count > 0:
            print(f"  Imported {count} new chunks to Elasticsearch")
    
    def get_pg_connection(self):
        """Get PostgreSQL connection."""
        return psycopg2.connect(
            dbname=self.pg_config["dbname"],
            user=self.pg_config["user"],
            password=self.pg_config["password"],
            host=self.pg_config["host"],
            port=self.pg_config["port"]
        )
    
    def process_all_pdfs(
        self,
        base_dir: str = "rag_papers",
        categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Process all PDFs from directory structure.
        
        Args:
            base_dir: Base directory containing category folders
            categories: List of categories to process (defaults to all)
            
        Returns:
            Dictionary with processing statistics
        """
        if categories is None:
            categories = ["badminton", "cycling", "running", "soccer", "swimming"]
        
        base_path = Path(base_dir)
        
        if not base_path.exists():
            print(f"Error: Directory not found: {base_dir}")
            return {"success": False, "error": f"Directory not found: {base_dir}"}
        
        # Step 1: Initialize database
        print("\n" + "="*70)
        print("STEP 1: Database Initialization")
        print("="*70)
        if not self.db_init.create_database():
            return {"success": False, "error": "Failed to create database"}
        
        if not self.db_init.create_tables():
            return {"success": False, "error": "Failed to create tables"}
        
        # Step 2: Process PDFs
        print("\n" + "="*70)
        print("STEP 2: PDF Processing and Chunking")
        print("="*70)
        
        total_chunks = 0
        total_papers = 0
        successful = 0
        failed = []
        
        for category in categories:
            category_path = base_path / category
            
            if not category_path.exists():
                print(f"\nWarning: Skipping {category}: folder not found")
                continue
            
            pdf_files = list(category_path.glob("*.pdf"))
            
            if not pdf_files:
                print(f"\nWarning: No PDFs found in {category}/")
                continue
            
            print(f"\n{'='*70}")
            print(f"Processing category: {category.upper()}")
            print(f"   Found {len(pdf_files)} PDF files")
            print(f"{'='*70}")
            
            for i, pdf_path in enumerate(pdf_files, 1):
                print(f"\n[{i}/{len(pdf_files)}] {pdf_path.name}")
                print("-" * 50)
                
                try:
                    chunks_created = self.process_single_pdf(str(pdf_path), category)
                    total_chunks += chunks_created
                    total_papers += 1
                    successful += 1
                    print(f"  Success: {chunks_created} chunks")
                
                except Exception as e:
                    print(f"  Failed: {str(e)}")
                    failed.append(f"{category}/{pdf_path.name}")
                    continue
        
        # Summary
        print("\n" + "="*70)
        print("PROCESSING SUMMARY")
        print("="*70)
        print(f"  Total papers processed: {successful}/{total_papers}")
        print(f"  Total chunks created: {total_chunks}")
        if successful > 0:
            print(f"  Average chunks per paper: {total_chunks/successful:.1f}")
        
        if failed:
            print(f"\nWarning: Failed papers ({len(failed)}):")
            for name in failed:
                print(f"    - {name}")
        
        return {
            "success": True,
            "total_papers": total_papers,
            "successful": successful,
            "failed": len(failed),
            "total_chunks": total_chunks,
            "failed_papers": failed
        }


def process_single_pdf_file(pdf_path: str, auto_import_to_es: bool = True) -> int:
    """
    Process a single PDF file and add to knowledge base.
    
    Args:
        pdf_path: Path to PDF file
        auto_import_to_es: Whether to automatically import to Elasticsearch
        
    Returns:
        Number of chunks created
        
    Raises:
        FileNotFoundError: If PDF file doesn't exist
        ValueError: If file is not a PDF
    """
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    if not pdf_file.suffix.lower() == '.pdf':
        raise ValueError(f"Not a PDF file: {pdf_path}")
    
    pipeline = PreprocessingPipeline(auto_import_to_es=auto_import_to_es)
    num_chunks = pipeline.process_single_pdf_new(str(pdf_file))
    
    return num_chunks


def process_pdf_directory_files(directory_path: str, auto_import_to_es: bool = True) -> Dict[str, Any]:
    """
    Process all PDF files in a directory and add to knowledge base.
    
    Args:
        directory_path: Path to directory containing PDF files
        auto_import_to_es: Whether to automatically import to Elasticsearch
        
    Returns:
        Dictionary with processing statistics
        
    Raises:
        FileNotFoundError: If directory doesn't exist
        ValueError: If path is not a directory
    """
    dir_path = Path(directory_path)
    if not dir_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory_path}")
    
    if not dir_path.is_dir():
        raise ValueError(f"Not a directory: {directory_path}")
    
    pipeline = PreprocessingPipeline(auto_import_to_es=auto_import_to_es)
    result = pipeline.process_pdf_directory(str(dir_path))
    
    return result
