# RAG Pipeline 模块化实现

这是一个完整的实时 RAG (Retrieval-Augmented Generation) Pipeline，支持从查询到生成的端到端流程。

## 项目结构

```
project-phase2/
├── config.py              # 配置管理模块
├── utils.py               # 工具函数模块
├── embedding.py          # 向量化模块
├── retrieval.py          # 检索模块
├── reranking.py         # 重排序模块
├── generation.py        # 生成模块 (Gemini API)
├── preprocessing.py     # 数据预处理模块
├── rag_pipeline.py     # 主流程模块
├── main.py             # 入口文件
├── requirements.txt    # 依赖包
└── README.md          # 说明文档
```

## 功能特性

- ✅ **模块化设计**：每个功能独立模块，易于维护和扩展
- ✅ **实时查询**：支持实时输入 query，动态生成 embedding
- ✅ **混合检索**：向量检索 (KNN) + 关键词检索 (BM25)
- ✅ **智能重排序**：使用交叉编码器模型提升相关性
- ✅ **Gemini 集成**：调用 Google Gemini API 生成答案
- ✅ **类别过滤**：自动识别运动类别并过滤结果
- ✅ **流式输出**：支持流式生成响应

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

### 1. 设置 API Keys

在 `config.py` 中配置或使用环境变量：

```python
# OpenAI API Key (用于生成 embedding)
export OPENAI_API_KEY="your-openai-api-key"

# Gemini API Key (用于生成答案)
export GEMINI_API_KEY="your-gemini-api-key"
```

### 2. 检查配置

确保以下配置正确：
- Elasticsearch 连接信息
- PostgreSQL 数据库连接信息
- API Keys
- 检索参数 (top_k, num_candidates)
- 重排序参数

## 使用方式

### 方式 1: 使用主流程模块 (推荐)

```python
from rag_pipeline import RAGPipeline

# 初始化 pipeline
pipeline = RAGPipeline()

# 查询
query = "What rehabilitation methods are most effective for treating knee injuries in badminton players?"
result = pipeline.query(query)

# 查看结果
print(result["response"])
print(result["sources"])
```

### 方式 2: 使用命令行

```bash
# 批量处理示例查询
python main.py

# 交互式模式
python main.py interactive
```

### 方式 3: 单独使用各个模块

```python
# 1. 向量化
from embedding import EmbeddingGenerator
embedding_gen = EmbeddingGenerator()
query_embedding = embedding_gen.generate_embedding("your query")

# 2. 检索
from retrieval import Retriever
retriever = Retriever()
documents = retriever.search(query_embedding, "your query")

# 3. 重排序
from reranking import Reranker
reranker = Reranker()
reranked_docs = reranker.rerank("your query", documents)

# 4. 生成
from generation import GeminiGenerator
generator = GeminiGenerator()
result = generator.generate("your query", reranked_docs)
```

## 数据准备

### 从 PostgreSQL 导入到 Elasticsearch

```python
from preprocessing import DataPreprocessor

preprocessor = DataPreprocessor()

# 创建索引
preprocessor.create_es_index(force_recreate=True)

# 导入数据
preprocessor.import_from_postgres_to_elasticsearch()
```

## 配置说明

### 检索配置

```python
RETRIEVAL_CONFIG = {
    "top_k": 10,              # 检索返回的文档数量
    "num_candidates": 60,      # KNN 候选数量
    "use_hybrid": True,        # 是否使用混合检索
    "category_filter": True    # 是否启用类别过滤
}
```

### 重排序配置

```python
RERANKING_CONFIG = {
    "enabled": True,           # 是否启用重排序
    "rerank_top_k": 5,        # 重排序后返回的文档数量
    "model_name": "BAAI/bge-reranker-base",
    "device": "cpu"            # "cpu" 或 "cuda"
}
```

### Gemini 配置

```python
GEMINI_CONFIG = {
    "api_key": "...",
    "model": "gemini-pro",
    "temperature": 0.7,
    "max_output_tokens": 1000
}
```

## 工作流程

```
用户输入 Query
    ↓
[1. 向量化] → 使用 OpenAI 生成 Query Embedding
    ↓
[2. 检索] → Elasticsearch 向量检索 + 关键词检索
    ↓
[3. 重排序] → 使用交叉编码器模型重排序
    ↓
[4. 生成] → 构建 Prompt + 调用 Gemini API
    ↓
返回生成结果
```

## 示例输出

```python
{
    "response": "Based on the context documents, the most effective rehabilitation methods...",
    "sources": ["source1.pdf", "source2.pdf"],
    "num_documents": 5,
    "query": "What rehabilitation methods...",
    "category": "Badminton",
    "documents": [...]
}
```

## 注意事项

1. **Gemini API Key**: 需要设置 `GEMINI_API_KEY` 环境变量或在 `config.py` 中配置
2. **重排序模型**: 首次使用会自动下载模型，需要网络连接
3. **Elasticsearch**: 确保 Elasticsearch 服务正在运行
4. **PostgreSQL**: 数据导入需要 PostgreSQL 数据库连接

## 扩展功能

### 自定义 Prompt

```python
custom_prompt = "Your custom system instruction..."
result = pipeline.generator.generate(
    query="...",
    documents=documents,
    system_instruction=custom_prompt
)
```

### 流式输出

```python
for chunk in pipeline.query_stream("your query"):
    print(chunk, end="", flush=True)
```

### 禁用重排序

```python
pipeline = RAGPipeline(use_reranking=False)
```

### 仅使用向量检索

```python
pipeline = RAGPipeline(use_hybrid_search=False)
```

## 故障排除

1. **ImportError**: 确保安装了所有依赖 `pip install -r requirements.txt`
2. **API Key 错误**: 检查环境变量或 `config.py` 中的配置
3. **Elasticsearch 连接失败**: 检查 ES 服务是否运行，证书路径是否正确
4. **重排序模型加载失败**: 检查网络连接，或禁用重排序功能

## 许可证

本项目用于学术研究目的。

