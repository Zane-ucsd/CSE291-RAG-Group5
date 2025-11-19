# 项目结构说明

## 目录结构

```
project-phase2/
├── src/                          # 源代码模块
│   ├── __init__.py
│   ├── config.py                 # 配置管理
│   ├── preprocessing/            # 预处理模块
│   │   ├── __init__.py
│   │   ├── preprocessing.py      # 数据预处理和数据库操作
│   │   ├── run_preprocessing.py  # 预处理运行脚本
│   │   └── paper_docling_processor.py  # PDF处理工具
│   ├── embedding/                # 向量化模块
│   │   ├── __init__.py
│   │   └── embedding.py         # OpenAI embeddings
│   ├── retrieval/                # 检索模块
│   │   ├── __init__.py
│   │   └── retrieval.py          # Elasticsearch检索
│   ├── reranking/                # 重排序模块
│   │   ├── __init__.py
│   │   └── reranking.py          # 交叉编码器重排序
│   ├── generation/               # 生成模块
│   │   ├── __init__.py
│   │   └── generation.py         # Gemini API生成
│   ├── pipeline/                 # 主流程模块
│   │   ├── __init__.py
│   │   └── rag_pipeline.py       # RAG Pipeline整合
│   ├── utils/                    # 工具模块
│   │   ├── __init__.py
│   │   └── utils.py              # 工具函数
│   └── validation/               # 验证模块
│       ├── __init__.py
│       └── validate_ground_truth.py  # Ground truth验证
│
├── tests/                        # 测试文件
│   ├── main.py                   # 主测试脚本
│   └── example_usage.py          # 使用示例
│
├── docs/                         # 文档
│   └── README.md                 # 项目说明
│
├── data/                         # 数据文件
│   └── new_vector_db_dump_clean.sql
│
├── run_preprocessing.py          # 预处理入口（根目录）
├── validate_ground_truth.py      # 验证入口（根目录）
├── requirements.txt              # 依赖包
│
└── [测试文件]                    # 测试用JSON等文件保留在根目录
    ├── ground_truth_example.json
    ├── ground_truth_example_llm_results.json
    ├── rag_results.json
    └── ...
```

## 模块说明

### 1. 预处理模块 (`src/preprocessing/`)
- **preprocessing.py**: 数据预处理、PDF处理、数据库操作
- **run_preprocessing.py**: 预处理流程运行脚本
- **paper_docling_processor.py**: PDF转Markdown工具

### 2. 向量化模块 (`src/embedding/`)
- **embedding.py**: OpenAI embeddings生成

### 3. 检索模块 (`src/retrieval/`)
- **retrieval.py**: Elasticsearch向量检索和混合检索

### 4. 重排序模块 (`src/reranking/`)
- **reranking.py**: 交叉编码器重排序

### 5. 生成模块 (`src/generation/`)
- **generation.py**: Gemini API响应生成

### 6. 主流程模块 (`src/pipeline/`)
- **rag_pipeline.py**: 整合所有模块的RAG Pipeline

### 7. 工具模块 (`src/utils/`)
- **utils.py**: 文本分类、格式化等工具函数

### 8. 验证模块 (`src/validation/`)
- **validate_ground_truth.py**: Ground truth数据验证

## 使用方法

### 从根目录运行

```bash
# 运行预处理
python run_preprocessing.py --base-dir rag_papers

# 验证ground truth
python validate_ground_truth.py ground_truth_example.json --check-llm

# 运行测试
python tests/main.py
```

### 在代码中使用

```python
# 从src模块导入
from src.pipeline import RAGPipeline
from src.preprocessing import PreprocessingPipeline
from src.validation import GroundTruthValidator

# 使用
pipeline = RAGPipeline()
result = pipeline.query("your query")
```

## 导入路径说明

所有模块使用相对导入（`from ..module import ...`），确保模块化结构。

测试文件通过添加 `src` 到 `sys.path` 来导入模块。

