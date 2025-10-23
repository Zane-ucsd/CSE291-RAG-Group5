# CSE291 RAG Sports Injury Prevention System

A Retrieval-Augmented Generation (RAG) system for sports injury prevention, containing research papers and processed data for five major sports: badminton, cycling, running, soccer, and swimming.

## 📁 Project Structure

```
├── rag_papers/           # Original PDF research papers
│   ├── badminton/        # Badminton injury prevention papers
│   ├── cycling/          # Cycling injury prevention papers
│   ├── running/          # Running injury prevention papers
│   ├── soccer/           # Soccer injury prevention papers
│   └── swimming/         # Swimming injury prevention papers
├── rag_papers_md/        # Converted Markdown files
│   ├── badminton/
│   ├── cycling/
│   ├── running/
│   ├── soccer/
│   └── swimming/
├── paper_docling_processor.py  # PDF to Markdown converter
├── new_vector_db_dump.sql      # Vector database dump
└── README.md
```

## 🚀 Quick Start

### 1. Database Setup

Import the vector database dump to set up your database:

```bash
# For PostgreSQL
psql -U your_username -d your_database -f new_vector_db_dump.sql

# For MySQL
mysql -u your_username -p your_database < new_vector_db_dump.sql
```

### 2. Environment Setup

```bash
# Install required dependencies
pip install docling
pip install psycopg2-binary  # for PostgreSQL
# or
pip install pymysql          # for MySQL
```

### 3. Process PDFs to Markdown

```bash
python paper_docling_processor.py
```

## 📊 Data Overview

- **Total Papers**: 119 research papers
- **Sports Covered**: 5 major sports
- **File Formats**: PDF (original) + Markdown (processed)
- **Database**: Vector embeddings for semantic search

## 🏃‍♂️ Sports Categories

1. **Badminton** (20 papers) - Injury prevention and rehabilitation
2. **Cycling** (26 papers) - Biomechanics and injury patterns
3. **Running** (25 papers) - Common running injuries and prevention
4. **Soccer** (24 papers) - Football-specific injury research
5. **Swimming** (24 papers) - Swimming-related overuse injuries

## 🔧 Usage

The processed Markdown files in `rag_papers_md/` can be used for:
- Text analysis
- RAG system implementation
- Semantic search
- Content extraction for AI models

## 📝 Database Import Instructions

### PostgreSQL
```bash
# Create database
createdb sports_injury_rag

# Import dump
psql -U postgres -d sports_injury_rag -f new_vector_db_dump.sql
```

### MySQL
```bash
# Create database
mysql -u root -p -e "CREATE DATABASE sports_injury_rag;"

# Import dump
mysql -u root -p sports_injury_rag < new_vector_db_dump.sql
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

This is a research project for CSE291. For questions or contributions, please contact the project maintainers.
