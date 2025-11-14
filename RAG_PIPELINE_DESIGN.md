# RAG Pipeline 模块化设计方案

## 架构概览

```
用户输入 Query
    ↓
[1. 向量化模块] → 生成 Query Embedding
    ↓
[2. 查询模块] → 向量检索 (KNN/Hybrid)
    ↓
[3. 重排模块] → 对检索结果重排序
    ↓
[4. 生成模块] → 构建 Prompt + 调用 Gemini API
    ↓
返回生成结果
```

## 模块划分

### 1. 配置模块 (`config.py`)
- 统一管理所有配置参数
- 数据库连接配置
- Elasticsearch 配置
- API Keys (OpenAI, Gemini)
- 检索参数 (TOP_K, NUM_CANDIDATES)
- 重排参数
- Prompt 模板

### 2. 数据预处理模块 (`preprocessing.py`)
- 从原始数据源读取数据
- 数据清洗和格式化
- 写入 PostgreSQL 数据库
- 可选：数据验证和质量检查

### 3. 向量化模块 (`embedding.py`)
- 文本向量化功能
- 支持批量向量化（用于数据导入）
- 支持实时向量化（用于查询）
- Embedding 归一化处理
- 缓存机制（可选）

### 4. 查询模块 (`retrieval.py`)
- 向量检索 (KNN)
- 混合检索 (KNN + BM25)
- 类别过滤
- 结果格式化

### 5. 重排模块 (`reranking.py`)
- 基于交叉编码器的重排序
- 可选：基于规则的重排序
- 可选：多样性重排序
- 结果去重

### 6. 生成模块 (`generation.py`)
- Prompt 构建
- Gemini API 调用
- 错误处理和重试
- 响应解析

### 7. 主流程模块 (`rag_pipeline.py`)
- 整合所有模块
- 端到端流程控制
- 日志记录
- 性能监控

### 8. 工具模块 (`utils.py`)
- 文本分类（运动类别）
- 文本预处理
- 工具函数

## 数据流

### 离线阶段（数据准备）
```
原始数据 → preprocessing.py → PostgreSQL
PostgreSQL → embedding.py → Elasticsearch
```

### 在线阶段（实时查询）
```
User Query → embedding.py → retrieval.py → reranking.py → generation.py → Response
```

## 文件结构

```
project-phase2/
├── config.py              # 配置管理
├── preprocessing.py       # 数据预处理
├── embedding.py          # 向量化
├── retrieval.py          # 检索
├── reranking.py         # 重排序
├── generation.py        # 生成（Gemini API）
├── rag_pipeline.py      # 主流程
├── utils.py             # 工具函数
├── requirements.txt     # 依赖包
└── main.py             # 入口文件（可选）
```

## 关键技术点

### 1. 向量化
- 使用 OpenAI `text-embedding-3-small` 模型
- L2 归一化处理
- 实时查询时动态生成 embedding

### 2. 检索策略
- 向量检索 (KNN)
- 混合检索 (KNN + BM25)
- 类别过滤（基于查询文本分类）

### 3. 重排序
- 使用交叉编码器模型（如 bge-reranker-base）
- 计算 query 与每个候选文档的相关性分数
- 重新排序 Top-K 结果

### 4. Prompt 构建
- 包含用户查询
- 包含检索到的相关文档（Top-N）
- 包含系统指令
- 格式化输出

### 5. Gemini API 集成
- 使用 Google Gemini API
- 错误处理和重试机制
- 流式输出支持（可选）

## 配置示例

```python
# config.py
ES_CONFIG = {
    "host": "https://localhost:9200",
    "api_key": ("QnbREpoBx8vU1yItlmkz", "T4TzIbNwwlp_LsgNptb53g"),
    "ca_certs": "path/to/ca.crt",
    "index_name": "sports_kb"
}

RETRIEVAL_CONFIG = {
    "top_k": 10,
    "num_candidates": 60,
    "use_hybrid": True
}

RERANKING_CONFIG = {
    "rerank_top_k": 5,
    "model_name": "BAAI/bge-reranker-base"
}

GEMINI_CONFIG = {
    "api_key": "your-gemini-api-key",
    "model": "gemini-pro",
    "temperature": 0.7,
    "max_tokens": 1000
}
```

## 使用示例

```python
from rag_pipeline import RAGPipeline

# 初始化 pipeline
pipeline = RAGPipeline()

# 实时查询
query = "What rehabilitation methods are most effective for treating knee injuries in badminton players?"
response = pipeline.query(query)

print(response)
```

## 优势

1. **模块化**：每个模块职责单一，易于维护和测试
2. **可扩展**：易于添加新功能（如新的检索策略、重排模型）
3. **可配置**：所有参数集中管理
4. **实时性**：支持实时查询，无需预先计算
5. **灵活性**：可以单独使用某个模块，也可以组合使用

