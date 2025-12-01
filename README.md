# RAG Pipeline for Sports Injury Knowledge Base

一个基于检索增强生成（RAG）的体育损伤知识库问答系统，支持多运动类别（羽毛球、跑步、足球、游泳、骑行）的损伤预防、治疗和康复知识检索与生成。

## 📁 项目结构

```
CSE291-RAG-Group5/
├── src/                    # 源代码模块
│   ├── config.py          # 配置管理（数据库、API密钥等）
│   ├── preprocessing/     # 预处理模块（PDF处理、文本分块）
│   ├── embedding/         # 向量化模块（OpenAI embeddings）
│   ├── retrieval/         # 检索模块（Elasticsearch混合检索）
│   ├── reranking/         # 重排序模块（交叉编码器+领域过滤）
│   ├── generation/        # 生成模块（Gemini API）
│   ├── pipeline/          # 主流程模块（RAG Pipeline整合）
│   ├── utils/             # 工具模块（文本分类、格式化等）
│   └── validation/        # 验证与评估模块
│       ├── retrieval_metrics.py      # 检索评估指标
│       ├── generation_evaluation.py  # RAGAS生成评估
│       └── ragas_integration.py       # RAGAS集成
├── tests/                 # 测试与示例
│   ├── main.py            # 主测试脚本（可直接运行）
│   └── example_usage.py   # 使用示例
├── scripts/               # 独立脚本
│   └── evaluate_live_retrieval.py  # 实时检索评估
├── docs/                  # 文档目录
│   ├── EVALUATION_METHODS.md        # 评估方法说明
│   ├── GENERATION_EVALUATION.md     # 生成评估指南
│   ├── METRICS_EXPLANATION.md       # 指标详解
│   └── RAGAS_PROGRESS_EXPLANATION.md # RAGAS进度说明
├── rag_papers/            # PDF源文件（按运动类别分类）
├── rag_papers_md/         # 转换后的Markdown文件
├── data/                  # 数据文件
├── main.py                # 主入口脚本（推荐使用）
├── evaluate_retrieval.py  # 独立检索评估脚本
├── evaluate_generation.py # 独立生成评估脚本
├── validate_ground_truth.py  # Ground Truth验证工具
├── requirements.txt       # Python依赖包
└── PROJECT_STRUCTURE.md   # 详细项目结构说明
```

详细结构说明请参考 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置

编辑 `src/config.py` 设置：
- PostgreSQL 连接信息
- Elasticsearch 连接信息
- OpenAI API Key
- Gemini API Key

### 3. 处理新的 PDF 文件

系统支持处理单个 PDF 文件或整个目录的 PDF 文件，自动完成 PDF → Markdown → Chunks → Embeddings → PostgreSQL → Elasticsearch 的完整流程。

```bash
# 处理单个 PDF 文件
python main.py --process-pdf /path/to/file.pdf

# 处理目录中的所有 PDF 文件
python main.py --process-pdf-dir /path/to/folder
```

**功能说明：**
- 自动检测并跳过重复的 chunks（基于 source + content）
- 自动导入到 PostgreSQL 和 Elasticsearch
- 支持处理无类别的 PDF 文件（category 为 None）
- 单个文件失败不影响其他文件处理

### 4. 运行RAG Pipeline

#### 方式1: 标准模式（运行预设查询）

```bash
# 仅运行查询，不进行评估
python main.py

# 运行查询并进行完整评估
python main.py --evaluate
```

#### 方式2: 交互式模式

```bash
# 实时输入查询，立即获得结果
python main.py interactive
```

输入 `exit`、`quit` 或 `q` 退出交互模式。

#### 方式3: 直接运行测试脚本

```bash
# 从 tests 目录直接运行（功能相同）
python tests/main.py                    # 标准模式
python tests/main.py --evaluation      # 评估模式
python tests/main.py interactive        # 交互模式
```

#### 评估模式说明

使用 `--evaluate` 标志时，系统会：

1. **检索评估**（需要 `ground_truth_example.json`）：
   - 评估重排序后的最终检索结果（top 10）
   - 评估重排序前的初始检索结果（如果可用）
   - 计算指标：Precision@K, Recall@K, NDCG@K, MRR, MAP 等
   - 自动生成重排序前后对比报告

2. **生成评估**（需要安装 `ragas`）：
   - 使用 RAGAS 评估生成答案质量
   - 计算指标：Faithfulness, Answer Relevancy, Context Precision, Context Recall

3. **输出文件**：
   - `rag_results.json`: 所有查询的完整结果
   - `evaluation_report_after_rerank.json`: 重排序后的检索评估报告
   - `evaluation_report_before_rerank.json`: 重排序前的检索评估报告
   - `generation_evaluation.json`: RAGAS生成评估报告

### 5. 验证Ground Truth

```bash
python validate_ground_truth.py ground_truth_example.json --check-llm
```

## 评估系统

项目提供了完整的评估系统，包括生成结果评估和检索质量评估。

### 1. 生成结果评估 (RAGAS)

使用 RAGAS (Retrieval-Augmented Generation Assessment) 评估最终生成结果的质量。

#### 前置要求

```bash
# 安装 RAGAS（如果尚未安装）
pip install ragas
```

#### 快速使用

```bash
# 方式1: 在主流程中自动评估（推荐）
python main.py --evaluate

# 方式2: 使用独立评估脚本
python evaluate_generation.py rag_results.json

# 方式3: 使用环境变量（适用于 tests/main.py）
export EVALUATE_WITH_RAGAS=true  # Linux/Mac
# 或
$env:EVALUATE_WITH_RAGAS="true"  # Windows PowerShell
python tests/main.py
```

#### 评估指标

- **Faithfulness (忠实度)**: 评估答案是否基于提供的上下文，没有编造信息 (0-1，越高越好)
- **Answer Relevancy (答案相关性)**: 评估答案与问题的相关性 (0-1，越高越好)
- **Context Precision (上下文精确度)**: 评估检索到的上下文的精确度 (需要 ground truth)
- **Context Recall (上下文召回率)**: 评估检索到的上下文的召回率 (需要 ground truth)

#### 完整评估（包含所有指标）

```bash
python evaluate_generation.py rag_results.json \
    --ground-truth ground_truth_example.json \
    --use-ground-truth \
    --output generation_evaluation.json
```

### 2. 检索质量评估

评估检索阶段（ES检索和Reranking）的质量，包括rerank前后的对比。

#### 使用方法

```bash
# 在主流程中自动评估（推荐）
python main.py --evaluate

# 或使用独立脚本
python evaluate_retrieval.py rag_results.json \
    --ground-truth ground_truth_example.json \
    --output evaluation_report.json
```

#### 评估指标

- **Precision@K**: 前K个检索结果中相关文档的比例
- **Recall@K**: 检索到的相关文档占所有相关文档的比例
- **NDCG@K**: 归一化折损累积增益，考虑排序质量
- **MRR**: 平均倒数排名，第一个相关文档的位置

#### Reranking效果对比

评估会自动对比rerank前后的效果，显示：
- **Precision@1**: 第一个文档的相关性（rerank的主要改进点）
- **MRR**: 第一个相关文档的平均位置
- **NDCG@10**: 排序质量改进

### 3. 评估结果文件

运行 `python main.py --evaluate` 后会生成以下文件：

| 文件名 | 说明 | 内容 |
|--------|------|------|
| `rag_results.json` | 查询结果 | 包含所有查询的完整结果（答案、来源、文档等） |
| `evaluation_report_after_rerank.json` | 检索评估（重排序后） | 最终检索结果的评估指标（Precision, Recall, NDCG, MRR等） |
| `evaluation_report_before_rerank.json` | 检索评估（重排序前） | 初始ES检索结果的评估指标（如果可用） |
| `generation_evaluation.json` | RAGAS生成评估 | 生成答案的质量评估（Faithfulness, Answer Relevancy等） |

**注意**：
- `evaluation_report_before_rerank.json` 仅在结果包含 `pre_rerank_documents` 字段时生成
- `generation_evaluation.json` 仅在安装 `ragas` 包后生成
- 如果 `ground_truth_example.json` 不存在，检索评估会被跳过

### 4. 评估配置

#### 环境变量

```bash
# 启用RAGAS评估
export EVALUATE_WITH_RAGAS=true

# 指定评估模型（默认: gpt-4o）
export RAGAS_EVAL_MODEL=gpt-4o
export OPENAI_API_KEY=your-api-key
```

#### Ground Truth格式

`ground_truth_example.json` 格式：

```json
[
  {
    "query": "What rehabilitation methods are most effective for treating knee injuries?",
    "relevant_ids": ["440", "356", "180"]
  }
]
```

### 5. 评估结果解读

#### RAGAS分数参考

- **0.9-1.0**: 优秀 ✅
- **0.7-0.9**: 良好 ⚠️
- **0.5-0.7**: 需要改进 ❌
- **< 0.5**: 严重问题 🚨

#### 检索指标说明

- **Precision@10**: 如果为0.4，表示前10个文档中有4个相关
- **Recall@10**: 如果为0.2，表示检索到了20%的相关文档
- **NDCG@10**: 考虑排序的指标，越高表示相关文档排得越靠前
- **MRR**: 如果为0.67，表示平均第一个相关文档在第1.5位

详细评估方法说明请参考：
- [生成结果评估文档](docs/GENERATION_EVALUATION.md)
- [评估方法指南](docs/EVALUATION_METHODS.md)

## 🔧 核心模块说明

| 模块 | 功能 | 技术栈 |
|------|------|--------|
| **预处理** | PDF转Markdown、文本分块、数据库初始化 | docling, langchain-text-splitters |
| **向量化** | 生成文档和查询的向量表示 | OpenAI text-embedding-3-small |
| **检索** | Elasticsearch混合检索（向量+BM25） | Elasticsearch 8.x |
| **重排序** | 交叉编码器重排序 + 领域过滤 + 分数融合 | BAAI/bge-reranker-base |
| **生成** | 基于检索结果的答案生成 | Google Gemini 2.0 Flash |
| **验证** | Ground truth数据验证和一致性检查 | - |
| **评估** | 检索质量评估（Precision, Recall, NDCG, MRR等）和RAGAS生成评估 | ragas |

### 重排序特性

系统采用两阶段重排序策略：

1. **领域过滤**（可选）：基于查询的运动类别，对匹配类别的文档进行1.25倍提升
2. **交叉编码器重排序**：使用深度语义模型进行精确排序
3. **分数融合**：融合交叉编码器分数和原始检索分数（默认比例：70% CE + 30% 原始）

详细说明请参考 [RERANKING_INTEGRATION.md](RERANKING_INTEGRATION.md)

## 💻 使用示例

### Python代码示例

```python
from src.pipeline import RAGPipeline

# 初始化Pipeline
pipeline = RAGPipeline()

# 执行查询
result = pipeline.query(
    "What rehabilitation methods are most effective for treating knee injuries in badminton players?"
)

# 查看结果
print("答案:", result["response"])
print("来源:", result["sources"])
print("文档数:", result["num_documents"])
print("类别:", result.get("category", "N/A"))

# 查看检索到的文档
for doc in result["documents"]:
    print(f"文档ID: {doc['id']}, 分数: {doc.get('score', 'N/A')}")
```

### 命令行示例

```bash
# 1. 处理新PDF文件
python main.py --process-pdf rag_papers/badminton/new_paper.pdf

# 2. 运行标准查询（12个预设查询）
python main.py

# 3. 运行评估模式
python main.py --evaluate

# 4. 交互式查询
python main.py interactive

# 5. 独立评估（已有结果文件）
python evaluate_retrieval.py rag_results.json --ground-truth ground_truth_example.json
python evaluate_generation.py rag_results.json --ground-truth ground_truth_example.json
```

## 📊 评估指标说明

### 检索评估指标

- **Precision@K**: 前K个结果中相关文档的比例
- **Recall@K**: 检索到的相关文档占所有相关文档的比例
- **NDCG@K**: 归一化折损累积增益，考虑排序质量（0-1，越高越好）
- **MRR**: 平均倒数排名，第一个相关文档的位置（0-1，越高越好）
- **MAP**: 平均平均精度，综合考虑排序和相关性

### RAGAS生成评估指标

- **Faithfulness (忠实度)**: 答案是否基于上下文，无编造信息（0-1，越高越好）
- **Answer Relevancy (答案相关性)**: 答案与问题的相关程度（0-1，越高越好）
- **Context Precision (上下文精确度)**: 检索到的上下文中相关部分的比例（需要ground truth）
- **Context Recall (上下文召回率)**: 检索到的上下文覆盖ground truth的程度（需要ground truth）

详细指标说明请参考：
- [指标详解](docs/METRICS_EXPLANATION.md)
- [生成评估指南](docs/GENERATION_EVALUATION.md)
- [评估方法说明](docs/EVALUATION_METHODS.md)

## ⚠️ 注意事项

1. **配置要求**：
   - 确保 Elasticsearch 和 PostgreSQL 服务已启动
   - 配置正确的 API 密钥（OpenAI 和 Gemini）
   - 检查 `src/config.py` 中的连接信息

2. **评估模式**：
   - 需要 `ground_truth_example.json` 文件进行检索评估
   - 需要安装 `ragas` 包进行生成评估：`pip install ragas`
   - 评估会增加运行时间，特别是 RAGAS 评估

3. **输出文件**：
   - 每次运行会覆盖同名的输出文件
   - 建议在运行前备份重要结果

4. **性能优化**：
   - 重排序阶段会显著提升检索质量，但会增加延迟
   - 可通过 `src/config.py` 中的 `RERANKING_CONFIG` 调整重排序参数

