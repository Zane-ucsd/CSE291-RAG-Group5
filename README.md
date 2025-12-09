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

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: Ensure you have Python 3.10+ installed. The project requires:
- PostgreSQL with pgvector extension
- Elasticsearch 8.x or 9.x
- OpenAI API key for embeddings
- Gemini API key for generation

### 2. Configuration

Edit `src/config.py` to set:
- PostgreSQL connection information
- Elasticsearch connection information
- OpenAI API Key
- Gemini API Key

### 3. Process New PDF Files

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

### 4. Run RAG Pipeline

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

### 5. Validate Ground Truth

```bash
python validate_ground_truth.py results/ground_truth_example.json --check-llm
```

## Evaluation System

The project provides a complete evaluation system, including generation result evaluation and retrieval quality evaluation.

### 1. Generation Result Evaluation (RAGAS)

Uses RAGAS (Retrieval-Augmented Generation Assessment) to evaluate the quality of generated responses.

#### Prerequisites

```bash
# Install RAGAS (if not already installed)
pip install ragas
```

#### Quick Usage

```bash
# Method 1: Automatic evaluation in main pipeline (recommended)
python main.py --evaluate

# Method 2: Use standalone evaluation script
python evaluate_generation.py results/rag_results.json

# Method 3: Use environment variable (for tests/main.py)
export EVALUATE_WITH_RAGAS=true  # Linux/Mac
# or
$env:EVALUATE_WITH_RAGAS="true"  # Windows PowerShell
python tests/main.py
```

#### Evaluation Metrics

- **Faithfulness**: Evaluates whether the answer is grounded in the provided context without fabrication (0-1, higher is better)
- **Answer Relevancy**: Evaluates how relevant the answer is to the question (0-1, higher is better)
- **Context Precision**: Evaluates the precision of retrieved context (requires ground truth)
- **Context Recall**: Evaluates the recall of retrieved context (requires ground truth)

#### Full Evaluation (All Metrics)

```bash
python evaluate_generation.py results/rag_results.json \
    --ground-truth results/ground_truth_example.json \
    --use-ground-truth \
    --output results/generation_evaluation.json
```

### 2. Retrieval Quality Evaluation

Evaluates the quality of the retrieval stage (ES retrieval and Reranking), including before/after reranking comparison.

#### Usage

```bash
# Automatic evaluation in main pipeline (recommended)
python main.py --evaluate

# Or use standalone script
python evaluate_retrieval.py results/rag_results.json \
    --ground-truth results/ground_truth_example.json \
    --output results/evaluation_report.json
```

#### Evaluation Metrics

- **Precision@K**: Proportion of relevant documents in top K results
- **Recall@K**: Proportion of retrieved relevant documents out of all relevant documents
- **NDCG@K**: Normalized Discounted Cumulative Gain, considering ranking quality
- **MRR**: Mean Reciprocal Rank, position of first relevant document

#### Reranking Effect Comparison

Evaluation automatically compares before/after reranking effects, showing:
- **Precision@1**: Relevance of first document (main improvement point of reranking)
- **MRR**: Average position of first relevant document
- **NDCG@10**: Ranking quality improvement

### 3. Evaluation Result Files

After running `python main.py --evaluate`, the following files are generated in the `results/` directory:

| File Name | Description | Content |
|-----------|-------------|---------|
| `rag_results.json` | Query results | Complete results for all queries (answers, sources, documents, etc.) |
| `evaluation_report_after_rerank.json` | Retrieval evaluation (after reranking) | Evaluation metrics for final retrieval results (Precision, Recall, NDCG, MRR, etc.) |
| `evaluation_report_before_rerank.json` | Retrieval evaluation (before reranking) | Evaluation metrics for initial ES retrieval results (if available) |
| `generation_evaluation.json` | RAGAS generation evaluation | Quality evaluation of generated answers (Faithfulness, Answer Relevancy, etc.) |

**Note**:
- `evaluation_report_before_rerank.json` is only generated if results contain `pre_rerank_documents` field
- `generation_evaluation.json` is only generated if `ragas` package is installed
- If `ground_truth_example.json` does not exist, retrieval evaluation will be skipped

### 4. Evaluation Configuration

#### Environment Variables

```bash
# Enable RAGAS evaluation
export EVALUATE_WITH_RAGAS=true

# Specify evaluation model (default: gpt-4o)
export RAGAS_EVAL_MODEL=gpt-4o
export OPENAI_API_KEY=your-api-key
```

#### Ground Truth Format

`ground_truth_example.json` format:

```json
[
  {
    "query": "What rehabilitation methods are most effective for treating knee injuries?",
    "relevant_ids": ["440", "356", "180"]
  }
]
```

### 5. Evaluation Result Interpretation

#### RAGAS Score Reference

- **0.9-1.0**: Excellent ✅
- **0.7-0.9**: Good ⚠️
- **0.5-0.7**: Needs Improvement ❌
- **< 0.5**: Critical Issues 🚨

#### Retrieval Metrics Explanation

- **Precision@10**: If 0.4, means 4 out of top 10 documents are relevant
- **Recall@10**: If 0.2, means 20% of relevant documents were retrieved
- **NDCG@10**: Ranking-aware metric, higher means relevant documents are ranked higher
- **MRR**: If 0.67, means average first relevant document is at position 1.5

For detailed evaluation methods, see the Evaluation System section above.

## 🔧 Core Module Description

| Module | Function | Technology Stack |
|--------|----------|------------------|
| **Preprocessing** | PDF to Markdown, text chunking, database initialization | docling, langchain-text-splitters |
| **Embedding** | Generate vector representations for documents and queries | OpenAI text-embedding-3-small |
| **Retrieval** | Elasticsearch hybrid search (vector + BM25) | Elasticsearch 8.x |
| **Reranking** | Cross-encoder reranking + domain filtering + score fusion | BAAI/bge-reranker-base |
| **Generation** | Answer generation based on retrieved results | Google Gemini 2.0 Flash |
| **Validation** | Ground truth data validation and consistency checking | - |
| **Evaluation** | Retrieval quality evaluation (Precision, Recall, NDCG, MRR, etc.) and RAGAS generation evaluation | ragas |

### Reranking Features

The system uses a two-stage reranking strategy:

1. **Domain Filtering** (optional): Based on query sport category, boost matching category documents by 1.25x
2. **Cross-Encoder Reranking**: Use deep semantic model for precise ranking
3. **Score Fusion**: Fuse cross-encoder scores with original retrieval scores (default: 70% CE + 30% original)

Reranking parameters can be configured in `RERANKING_CONFIG` in `src/config.py`.

## 💻 Usage Examples

### Python Code Example

```python
from src.pipeline import RAGPipeline

# Initialize Pipeline
pipeline = RAGPipeline()

# Execute query
result = pipeline.query(
    "What rehabilitation methods are most effective for treating knee injuries in badminton players?"
)

# View results
print("Answer:", result["response"])
print("Sources:", result["sources"])
print("Number of documents:", result["num_documents"])
print("Category:", result.get("category", "N/A"))

# View retrieved documents
for doc in result["documents"]:
    print(f"Document ID: {doc['id']}, Score: {doc.get('score', 'N/A')}")
```

### Command Line Examples

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

## 📊 Evaluation Metrics Explanation

### Retrieval Evaluation Metrics

- **Precision@K**: Proportion of relevant documents in top K results
- **Recall@K**: Proportion of retrieved relevant documents out of all relevant documents
- **NDCG@K**: Normalized Discounted Cumulative Gain, considering ranking quality (0-1, higher is better)
- **MRR**: Mean Reciprocal Rank, position of first relevant document (0-1, higher is better)
- **MAP**: Mean Average Precision, comprehensive consideration of ranking and relevance

### RAGAS Generation Evaluation Metrics

- **Faithfulness**: Whether answer is based on context without fabrication (0-1, higher is better)
- **Answer Relevancy**: How relevant the answer is to the question (0-1, higher is better)
- **Context Precision**: Proportion of relevant parts in retrieved context (requires ground truth)
- **Context Recall**: How well retrieved context covers ground truth (requires ground truth)

All metrics are explained in the Evaluation System section above.

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
   - Reranking stage significantly improves retrieval quality but increases latency
   - Reranking parameters can be adjusted in `RERANKING_CONFIG` in `src/config.py`
