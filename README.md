# RAG Pipeline for Sports Injury Knowledge Base

A Retrieval-Augmented Generation (RAG) system for sports injury knowledge base, supporting multiple sport categories (badminton, cycling, running, soccer, swimming) for injury prevention, treatment, and rehabilitation knowledge retrieval and generation.

## 📁 Project Structure

```
CSE291-RAG-Group5/
├── src/                    # Source code modules
│   ├── config.py          # Configuration management (database, API keys, etc.)
│   ├── preprocessing/     # Preprocessing module (PDF processing, text chunking)
│   │   └── preprocessing.py
│   ├── embedding/         # Embedding module (OpenAI embeddings)
│   │   └── embedding.py
│   ├── retrieval/         # Retrieval module (Elasticsearch hybrid search)
│   │   └── retrieval.py
│   ├── reranking/         # Reranking module (cross-encoder + domain filtering)
│   │   ├── reranking.py
│   │   └── domain_filter.py
│   ├── generation/        # Generation module (Gemini API)
│   │   └── generation.py
│   ├── pipeline/          # Main pipeline module (RAG Pipeline integration)
│   │   └── rag_pipeline.py
│   ├── utils/             # Utility module (text classification, formatting, etc.)
│   │   └── utils.py
│   └── validation/        # Validation and evaluation module
│       ├── evaluator.py
│       ├── retrieval_metrics.py      # Retrieval evaluation metrics
│       ├── generation_evaluation.py  # RAGAS generation evaluation
│       ├── metrics.py                # Core metrics calculation
│       └── validate_ground_truth.py  # Ground truth validation
├── tests/                 # Tests and examples
│   ├── main.py            # Main test script (can be run directly)
│   └── example_usage.py   # Usage examples
├── results/               # Evaluation and result files
│   ├── rag_results.json  # Query results
│   ├── evaluation_report_after_rerank.json  # Retrieval evaluation (after reranking)
│   ├── evaluation_report_before_rerank.json  # Retrieval evaluation (before reranking)
│   ├── generation_evaluation.json  # RAGAS generation evaluation
│   └── ground_truth_example.json  # Ground truth data for evaluation
├── data/                  # Data files
│   └── new_vector_db_dump_clean.sql  # Database dump
├── main.py                # Main entry script (recommended)
├── evaluate_retrieval.py  # Standalone retrieval evaluation script
├── evaluate_generation.py # Standalone generation evaluation script
├── validate_ground_truth.py  # Ground Truth validation tool
└── requirements.txt       # Python dependencies
```

## 🔧 Core Module Description

| Module | Function | Technology Stack |
|--------|----------|------------------|
| **Preprocessing** | PDF to Markdown, text chunking, database initialization | docling, langchain-text-splitters |
| **Embedding** | Generate vector representations for documents and queries | OpenAI text-embedding-3-small |
| **Retrieval** | Elasticsearch hybrid search (vector + BM25) | Elasticsearch 8.x |
| **Reranking** | Two-stage reranking: domain filtering + cross-encoder + score fusion | BAAI/bge-reranker-base |
| **Generation** | Answer generation based on retrieved results | Google Gemini 2.0 Flash |
| **Validation** | Ground truth data validation and consistency checking | - |
| **Evaluation** | Retrieval quality evaluation (Precision, Recall, NDCG, MRR, etc.) and RAGAS generation evaluation | ragas |

## 📋 Prerequisites

Before starting, ensure you have the following services installed and running:

### PostgreSQL with pgvector Extension

**Installation:**

```bash
# macOS (using Homebrew)
brew install postgresql@16  # PostgreSQL 11+ required, 16 recommended
brew services start postgresql@16
brew install pgvector  # Install pgvector extension

# Linux (Ubuntu/Debian)
sudo apt-get install postgresql postgresql-contrib  # Install PostgreSQL
sudo apt-get install postgresql-16-pgvector  # Install pgvector extension for PostgreSQL 16
```

**Enable pgvector extension in PostgreSQL:**

```bash
# Connect to your database
psql -U your_username -d your_database

# Enable extension
CREATE EXTENSION IF NOT EXISTS vector;
```

**Verify installation:**

```bash
# Check PostgreSQL is running
pg_isready

# Verify pgvector extension
psql -U your_username -d your_database -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

### Elasticsearch 8.x or 9.x

**Installation:**

```bash
# macOS (using Homebrew)
brew install elasticsearch
brew services start elasticsearch

# Linux (Ubuntu/Debian)
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-8.11.0-amd64.deb
sudo dpkg -i elasticsearch-8.11.0-amd64.deb
sudo systemctl start elasticsearch
sudo systemctl enable elasticsearch
```

**Configure Elasticsearch Connection:**

The project uses HTTPS to connect to Elasticsearch. You need to configure the certificate path:

1. **Find your Elasticsearch certificate path:**
   - macOS (Homebrew): Usually in `/usr/local/var/lib/elasticsearch/config/certs/http_ca.crt` or your Elasticsearch installation directory
   - Linux: Usually in `/etc/elasticsearch/certs/http_ca.crt` or your Elasticsearch installation directory
   - Or check your Elasticsearch installation directory: `elasticsearch_directory/config/certs/http_ca.crt`

2. **Update `src/config.py`:**
   - Set `ES_CONFIG["ca_certs"]` to your certificate file path (e.g., `/path/to/elasticsearch/config/certs/http_ca.crt`)
   - Update `ES_CONFIG["api_key"]` with your Elasticsearch API key (if authentication is enabled)

**Verify installation:**

```bash
# Check Elasticsearch is running
curl -k https://localhost:9200 -u "elastic:your_password"  # If password enabled
# or
curl http://localhost:9200  # If no authentication

# Should return cluster information
```

**Note**: If Elasticsearch uses authentication, you'll need to:
1. Get the API key from Elasticsearch (or use username/password)
2. Update `ES_CONFIG` in `src/config.py` with your credentials
3. Update `ca_certs` path to your certificate file location

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: Ensure you have Python 3.10+ installed. The project requires:
- PostgreSQL with pgvector extension
- Elasticsearch 8.x or 9.x
- OpenAI API key for embeddings
- Gemini API key for generation

### 2. Setup Database and Import Data

#### 2.1 Configure Database Connections

Before importing data, configure basic database connection information in `src/config.py`:
- **PostgreSQL connection**: `dbname`, `user`, `password`, `host`, `port`
- **Elasticsearch connection**: `host`, `api_key`, `ca_certs`

#### 2.2 Import SQL Data to PostgreSQL

Ensure PostgreSQL is running and create the database (if it doesn't exist):

```bash
# Create database (if needed)
createdb new_vector_db

# Import the SQL dump file
psql -U your_username -d new_vector_db -f data/new_vector_db_dump_clean.sql
```

**Note**: 
- Replace `your_username` with your PostgreSQL username
- The SQL file includes database schema with `pgvector` extension, pre-processed knowledge base data with embeddings, and all necessary tables and indexes
- If you need to set a password, use: `psql -U your_username -d new_vector_db -W -f data/new_vector_db_dump_clean.sql`

#### 2.3 Import Data to Elasticsearch

After importing to PostgreSQL, import the data to Elasticsearch:

You can run this as a one-liner:

```bash
python -c "from src.preprocessing.preprocessing import DataPreprocessor; p = DataPreprocessor(); p.create_es_index(force_recreate=True); p.import_from_postgres_to_elasticsearch()"
```

**Note**: 
- Make sure Elasticsearch is running before importing
- The import process may take a few minutes
- Ensure your Elasticsearch connection settings in `src/config.py` are correct

### 3. Configuration

Edit `src/config.py` to set:
- **PostgreSQL connection information** (if not already set in step 2)
- **Elasticsearch connection information** (if not already set in step 2)
- **OpenAI API Key** (required for embeddings)
- **Gemini API Key** (required for generation)

### 4. Process New PDF Files (Optional)

The system supports processing single PDF files or entire directories, automatically completing the full pipeline: PDF → Markdown → Chunks → Embeddings → PostgreSQL → Elasticsearch.

```bash
# Process a single PDF file
python main.py --process-pdf /path/to/file.pdf

# Process all PDF files in a directory
python main.py --process-pdf-dir /path/to/folder
```

**Features**:
- Automatically detects and skips duplicate chunks (based on source + content)
- Automatically imports to PostgreSQL and Elasticsearch
- Supports processing PDFs without category (category set to None)
- Individual file failures do not affect processing of other files

### 5. Run RAG Pipeline

#### Method 1: Standard Mode (Run Preset Queries)

```bash
# Run queries without evaluation
python main.py

# Run queries with full evaluation
python main.py --evaluate
```

#### Method 2: Interactive Mode

```bash
# Real-time query input with immediate results
python main.py interactive
```

Type `exit`, `quit`, or `q` to exit interactive mode.

#### Method 3: Run Test Script Directly

```bash
# Run from tests directory (same functionality)
python tests/main.py                    # Standard mode
python tests/main.py --evaluation      # Evaluation mode
python tests/main.py interactive        # Interactive mode
```

#### Evaluation Mode

When using the `--evaluate` flag, the system will:

1. **Retrieval Evaluation** (requires `ground_truth_example.json`):
   - Evaluate final retrieval results after reranking (top 10)
   - Evaluate initial retrieval results before reranking (if available)
   - Calculate metrics: Precision@K, Recall@K, NDCG@K, MRR, MAP, etc.
   - Automatically generate comparison reports before/after reranking

2. **Generation Evaluation** (requires `ragas` package):
   - Use RAGAS to evaluate generated answer quality
   - Calculate metrics: Faithfulness, Answer Relevancy, Context Precision, Context Recall

3. **Output Files** (saved to `results/` directory):
   - `rag_results.json`: Complete results for all queries
   - `evaluation_report_after_rerank.json`: Retrieval evaluation (after reranking)
   - `evaluation_report_before_rerank.json`: Retrieval evaluation (before reranking)
   - `generation_evaluation.json`: RAGAS generation evaluation

### 6. Validate Ground Truth

```bash
python validate_ground_truth.py results/ground_truth_example.json --check-llm
```

## 🔄 Reranking System

The system uses a two-stage reranking strategy to improve retrieval quality:
1. **Domain Filtering** (optional): Boosts documents matching the query's sport category
2. **Cross-Encoder Reranking**: Uses deep semantic model (`BAAI/bge-reranker-base`) for precise ranking

**Configuration**: Reranking parameters can be adjusted in `RERANKING_CONFIG` in `src/config.py`. The reranking model will be automatically downloaded on first use (~1GB).

## 📊 Evaluation System

The project provides evaluation for both retrieval quality and generation quality.

### Running Evaluation

```bash
# Run full evaluation (retrieval + generation)
python main.py --evaluate
```

This will generate evaluation reports in the `results/` directory:
- `rag_results.json`: Complete query results
- `evaluation_report_after_rerank.json`: Retrieval metrics (Precision@K, Recall@K, NDCG@K, MRR)
- `generation_evaluation.json`: RAGAS metrics (Faithfulness, Answer Relevancy)

**Requirements**:
- `results/ground_truth_example.json` must exist for retrieval evaluation
- `ragas` package must be installed for generation evaluation (already in `requirements.txt`)

### Ground Truth Format

`results/ground_truth_example.json` should contain:

```json
[
  {
    "query": "What rehabilitation methods are most effective for treating knee injuries?",
    "relevant_ids": ["440", "356", "180"]
  }
]
```

### Evaluation Metrics

**Retrieval Metrics**: Precision@K, Recall@K, NDCG@K, MRR (higher is better, 0-1 scale)

**RAGAS Metrics**: Faithfulness, Answer Relevancy (higher is better, 0-1 scale)
- 0.9-1.0: Excellent ✅
- 0.7-0.9: Good ⚠️
- < 0.7: Needs Improvement ❌


## 💻 Command Line Examples

```bash
# 1. Process new PDF file
python main.py --process-pdf /path/to/your/file.pdf

# 2. Run standard queries (12 preset queries)
python main.py

# 3. Run evaluation mode
python main.py --evaluate

# 4. Interactive query
python main.py interactive

# 5. Standalone evaluation (with existing result files)
python evaluate_retrieval.py results/rag_results.json --ground-truth results/ground_truth_example.json
python evaluate_generation.py results/rag_results.json --ground-truth results/ground_truth_example.json
```

## ⚠️ Important Notes

1. **Configuration Requirements**:
   - Ensure Elasticsearch and PostgreSQL services are running
   - Configure correct API keys (OpenAI and Gemini)
   - Check connection information in `src/config.py`

2. **Evaluation Mode**:
   - Requires `ground_truth_example.json` file for retrieval evaluation
   - Requires `ragas` package for generation evaluation: `pip install ragas`
   - Evaluation increases runtime, especially RAGAS evaluation

3. **Output Files**:
   - All evaluation and result files are saved to the `results/` directory
   - Each run will overwrite files with the same name
   - It is recommended to backup important results before running

4. **Performance Optimization**:
   - Reranking stage significantly improves retrieval quality but increases latency (~100-500ms)
   - See the Reranking System section above for detailed configuration and performance tuning options
