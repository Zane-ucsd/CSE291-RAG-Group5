# FAISS Vector Retrieval System

## Overview

This folder contains a complete implementation of a FAISS-based vector retrieval system for a sports injuries knowledge base. The system uses Facebook's FAISS (Facebook AI Similarity Search) library to perform efficient similarity search over 3,117+ document chunks across 5 sports categories.

## Architecture

The system follows a standard retrieval-augmented generation (RAG) pipeline:

```
Query → OpenAI Embedding → FAISS Index Search → Top-K Retrieval → Results
```

### Key Components

1. **Vector Database**: Pre-computed embeddings (1536-dimensional) from `text-embedding-3-small` model
2. **FAISS Index**: `IndexFlatIP` (Inner Product) with L2-normalized vectors for cosine similarity
3. **Query Processing**: OpenAI API for generating query embeddings
4. **Retrieval**: Top-K similarity search with optional category filtering

### Data Specification

- **Total Records**: 3,117 document chunks
- **Categories**: 5 sports (soccer: 867, cycling: 696, swimming: 685, badminton: 538, running: 331)
- **Embedding Model**: OpenAI `text-embedding-3-small`
- **Embedding Dimensions**: 1536
- **Similarity Metric**: Cosine Similarity (via normalized Inner Product)

## Files Description

### 1. `faiss.ipynb`
**Main implementation notebook** containing the complete FAISS retrieval pipeline.

**Contents:**
- **Data Parsing**: Functions to parse PostgreSQL dump files and extract embeddings
- **Index Building**: FAISS index creation with L2 normalization for cosine similarity
- **Query Embedding**: OpenAI API integration for query vectorization
- **Search Functions**: Similarity search with top-K retrieval and category filtering
- **Batch Processing**: Automated query processing for multiple test queries

### 2. `requests.txt`
**Test query collection** containing 16 diverse queries across all sports categories.

**Query Coverage:**
- **Badminton** (Queries 1-3): Knee injuries, preventive strategies, recovery factors
- **Cycling** (Queries 4-6): Low-back pain, saddle positioning, crash first-aid
- **Running** (Queries 7-9): Runner's knee, shoe types, ITBS rehabilitation
- **Soccer** (Queries 10-12): Hamstring strains, warm-up routines, injury monitoring
- **Swimming** (Queries 13-16): Shoulder pain, stroke mechanics, rehabilitation, gender-specific risks

### 3. `faiss_retrieval_summary.txt`
**Retrieval results summary** listing the retrieved document IDs for each query.

**Format:**
```
Query [N]: [Query Text]
IDs: [comma-separated list of retrieved document IDs]
```

**Purpose:**
- Ground truth for retrieval evaluation
- Quick reference for retrieved documents (60 per query)
- Input for downstream RAG evaluation metrics (recall, precision, MRR)

### 4. `faiss_retrievals.txt`
**Full retrieval results** containing complete content for all retrieved documents.

**Format:**
- Query text and metadata
- 60 retrieved chunks per query (ranked by similarity score)
- Each result includes: Rank, Score, Category, ID, Source, Full Content

**Use Cases:**
- Manual inspection of retrieval quality
- Context for language model generation
- Analysis of category distribution in results

## Getting Started

### Prerequisites

```bash
pip install faiss-cpu numpy pandas openai
```

### Environment Setup

```bash
export OPENAI_API_KEY="your-api-key-here"
```

### Basic Usage

```python
# 1. Load the notebook
# Open faiss.ipynb in Jupyter

# 2. Parse SQL dump and build index
metadata, embeddings = parse_sql_dump('new_vector_db_dump_clean.sql')
index = build_faiss_index(embeddings)

# 3. Perform a search
query = "What are effective treatments for knee injuries?"
results = search_similar_chunks(query, index, metadata, top_k=10)

# 4. Display results
display_results(results)
```




