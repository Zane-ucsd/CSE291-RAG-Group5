# tests/main.py 使用说明文档

## 📋 概述

`tests/main.py` 是 RAG Pipeline 的主入口文件，提供了完整的查询处理流程和可选的评估功能。该脚本支持两种运行模式：**标准模式**和**交互模式**。

## 🚀 运行方式

### 1. 标准模式（默认）

运行预设的查询列表，处理所有查询并生成结果：

```bash
# 基本运行（不进行评估）
python tests/main.py

# 启用评估模式
python tests/main.py --evaluation
```

### 2. 交互模式

实时输入查询，立即获得结果：

```bash
python tests/main.py interactive
```

在交互模式下：
- 输入查询后按回车键执行
- 输入 `exit`、`quit` 或 `q` 退出程序

### 3. 通过环境变量启用评估

除了使用 `--evaluation` 参数，也可以通过环境变量启用评估：

```bash
# Windows PowerShell
$env:EVALUATE_WITH_RAGAS="true"
python tests/main.py

# Linux/Mac
export EVALUATE_WITH_RAGAS=true
python tests/main.py
```

## 📊 评估模式详解

### 何时触发评估

评估模式会在以下情况下触发：

1. **命令行参数**：使用 `--evaluation` 参数
2. **环境变量**：设置 `EVALUATE_WITH_RAGAS=true`
3. **函数参数**：在代码中调用 `main(evaluate=True)`

### 评估覆盖内容

当启用评估模式时，系统会执行以下两个评估流程：

#### 1. 检索评估（Retrieval Evaluation）

**评估对象**：
- Elasticsearch 检索结果
- 重排序（Reranking）前后的对比

**前提条件**：
- 需要存在 `ground_truth_example.json` 文件
- 如果文件不存在，会跳过检索评估并显示警告

**评估内容**：
- **重排序后**：评估最终检索结果的质量
- **重排序前**：如果结果中包含 `pre_rerank_documents` 字段，会评估重排序前的检索结果
- **对比分析**：自动生成重排序前后的指标对比

**输出文件**：
- `evaluation_report_after_rerank.json`：重排序后的评估报告
- `evaluation_report_before_rerank.json`：重排序前的评估报告（如果可用）

#### 2. 生成评估（Generation Evaluation）

**评估对象**：
- 使用 RAGAS 框架评估生成答案的质量

**前提条件**：
- 需要安装 `ragas` 包：`pip install ragas`
- 如果未安装，会跳过生成评估并显示提示

**评估内容**：
- 基于 RAGAS 的多个指标评估生成质量
- 如果提供了 ground truth，会计算更多指标

**输出文件**：
- `generation_evaluation.json`：RAGAS 评估报告

## 📈 输出指标说明

### 检索评估指标

检索评估报告（`evaluation_report_after_rerank.json`）包含以下指标：

#### 聚合指标（aggregate）

| 指标名称 | 说明 | 范围 |
|---------|------|------|
| `mean_precision` | 平均精确度 | 0-1，越高越好 |
| `mean_recall` | 平均召回率 | 0-1，越高越好 |
| `mean_f1` | 平均 F1 分数 | 0-1，越高越好 |
| `mean_mrr` | 平均倒数排名 | 0-1，越高越好 |
| `mean_map` | 平均平均精度 | 0-1，越高越好 |
| `mean_hit_rate` | 平均命中率 | 0-1，越高越好 |
| `mean_precision@k` | 前 k 个结果的平均精确度 | 0-1，越高越好 |
| `mean_recall@k` | 前 k 个结果的平均召回率 | 0-1，越高越好 |
| `mean_f1@k` | 前 k 个结果的平均 F1 分数 | 0-1，越高越好 |
| `mean_ndcg@k` | 前 k 个结果的归一化折损累积增益 | 0-1，越高越好 |
| `std_*` | 各指标的标准差 | - |

**说明**：
- `k` 通常为 1, 3, 5, 10
- `precision@k`：前 k 个结果中相关文档的比例
- `recall@k`：前 k 个结果覆盖的相关文档比例
- `mrr`：第一个相关文档的倒数排名
- `ndcg@k`：考虑排序质量的累积增益指标

#### 单查询指标（per_query）

每个查询包含以下详细信息：
- `query`：查询文本
- `relevant_count`：相关文档总数
- `retrieved_count`：检索到的文档数
- `relevant_retrieved`：检索到的相关文档数
- 所有聚合指标对应的单查询指标

#### 重排序对比

如果同时生成了重排序前后的评估报告，程序会自动输出对比信息：

```
📊 Reranking Impact Comparison
Ranking Quality (most improved):
  Precision@1:  0.xxxx → 0.xxxx (Δ+0.xxxx)
  MRR:          0.xxxx → 0.xxxx (Δ+0.xxxx)
  NDCG@10:      0.xxxx → 0.xxxx (Δ+0.xxxx)
```

### 生成评估指标（RAGAS）

生成评估报告（`generation_evaluation.json`）包含以下 RAGAS 指标：

| 指标名称 | 说明 | 范围 | 是否需要 Ground Truth |
|---------|------|------|---------------------|
| `faithfulness` | 答案忠实度：答案是否基于提供的上下文，无编造信息 | 0-1，越高越好 | 否 |
| `answer_relevancy` | 答案相关性：答案与问题的相关程度 | 0-1，越高越好 | 否 |
| `context_precision` | 上下文精确度：检索到的上下文中相关部分的比例 | 0-1，越高越好 | 是（推荐） |
| `context_recall` | 上下文召回率：检索到的上下文覆盖 ground truth 的程度 | 0-1，越高越好 | 是（必需） |

**每个指标包含**：
- `mean`：平均值
- `min`：最小值
- `max`：最大值
- `scores`：每个查询的详细分数列表

## 📁 输出文件格式

### 1. rag_results.json

包含所有查询的完整结果：

```json
[
  {
    "query": "查询文本",
    "response": "生成的答案",
    "sources": ["文档来源1", "文档来源2", ...],
    "documents": [
      {
        "id": "文档ID",
        "content": "文档内容",
        "score": 0.95,
        ...
      }
    ],
    "num_documents": 10,
    "category": "badminton",
    "pre_rerank_documents": [...]  // 仅在评估模式下存在
  }
]
```

### 2. evaluation_report_after_rerank.json

检索评估报告格式：

```json
{
  "aggregate": {
    "mean_precision": 0.225,
    "mean_recall": 0.188,
    "mean_f1": 0.163,
    "mean_mrr": 0.667,
    "mean_map": 0.122,
    "mean_hit_rate": 0.583,
    "mean_precision@1": 0.583,
    "mean_precision@3": 0.333,
    "mean_precision@5": 0.267,
    "mean_precision@10": 0.225,
    "mean_recall@1": 0.061,
    "mean_recall@3": 0.119,
    "mean_recall@5": 0.156,
    "mean_recall@10": 0.188,
    "mean_ndcg@1": 0.583,
    "mean_ndcg@3": 0.377,
    "mean_ndcg@5": 0.337,
    "mean_ndcg@10": 0.316,
    "std_precision": 0.148,
    "std_recall": 0.209,
    ...
  },
  "per_query": [
    {
      "query": "查询文本",
      "relevant_count": 58,
      "retrieved_count": 10,
      "relevant_retrieved": 4,
      "precision": 0.4,
      "recall": 0.069,
      "f1_score": 0.118,
      "mrr": 1.0,
      "map": 0.050,
      "precision@1": 1.0,
      "precision@3": 0.667,
      ...
    }
  ]
}
```

### 3. generation_evaluation.json

RAGAS 评估报告格式：

```json
{
  "faithfulness": {
    "mean": 0.949,
    "min": 0.727,
    "max": 1.0,
    "scores": [0.818, 1.0, 1.0, ...]
  },
  "answer_relevancy": {
    "mean": 0.856,
    "min": 0.0,
    "max": 0.992,
    "scores": [0.908, 0.965, ...]
  },
  "context_precision": {
    "mean": 0.873,
    "min": 0.742,
    "max": 1.0,
    "scores": [0.742, 0.876, 1.0]
  },
  "context_recall": {
    "mean": 0.481,
    "min": 0.159,
    "max": 0.75,
    "scores": [0.159, 0.75, 0.545]
  }
}
```

## 🔧 运行逻辑流程

### 标准模式流程

```
1. 初始化 RAG Pipeline
   ↓
2. 加载预设查询列表（12个查询）
   ↓
3. 对每个查询执行：
   - 调用 pipeline.query()
   - 如果启用评估，设置 return_pre_rerank=True
   - 打印结果和来源
   ↓
4. 保存所有结果到 rag_results.json
   ↓
5. 如果启用评估：
   ├─ 检查 ground_truth_example.json 是否存在
   │  ├─ 存在 → 执行检索评估
   │  │  ├─ 评估重排序后结果
   │  │  ├─ 评估重排序前结果（如果可用）
   │  │  └─ 生成对比报告
   │  └─ 不存在 → 跳过检索评估
   │
   └─ 执行生成评估（RAGAS）
      ├─ 检查 ragas 是否安装
      ├─ 安装 → 执行评估
      └─ 未安装 → 跳过并提示
```

### 交互模式流程

```
1. 初始化 RAG Pipeline
   ↓
2. 进入交互循环：
   ├─ 等待用户输入查询
   ├─ 执行查询
   ├─ 显示结果
   └─ 继续循环或退出
```

## ⚙️ 配置要求

### 必需配置

确保以下服务已配置并运行：

1. **Elasticsearch**：在 `src/config.py` 中配置连接信息
2. **PostgreSQL**：在 `src/config.py` 中配置数据库连接
3. **OpenAI API Key**：用于生成 embeddings（在 `src/config.py` 或环境变量中设置）
4. **Gemini API Key**：用于生成答案（在 `src/config.py` 或环境变量中设置）

### 评估模式额外要求

1. **Ground Truth 文件**：
   - 文件名：`ground_truth_example.json`
   - 位置：项目根目录
   - 格式：包含查询和相关文档ID的JSON文件

2. **RAGAS 包**（仅生成评估需要）：
   ```bash
   pip install ragas
   ```

## 📝 示例用法

### 示例 1：基本运行

```bash
python tests/main.py
```

输出：
- `rag_results.json`：包含所有查询的结果

### 示例 2：完整评估

```bash
python tests/main.py --evaluation
```

输出：
- `rag_results.json`：查询结果
- `evaluation_report_after_rerank.json`：检索评估（重排序后）
- `evaluation_report_before_rerank.json`：检索评估（重排序前，如果可用）
- `generation_evaluation.json`：RAGAS 生成评估

### 示例 3：交互式查询

```bash
python tests/main.py interactive
```

```
Enter your query: What is runner's knee?
[显示结果]
Enter your query: exit
👋 Goodbye!
```

## ⚠️ 注意事项

1. **评估模式性能**：
   - 评估模式会增加运行时间，特别是 RAGAS 评估
   - 建议在开发/测试阶段使用评估模式

2. **Ground Truth 文件**：
   - 如果文件不存在，检索评估会被跳过
   - 确保文件格式正确，否则可能导致评估失败

3. **RAGAS 评估**：
   - 需要网络连接（调用 LLM API）
   - 可能需要较长时间，特别是处理大量查询时

4. **输出文件覆盖**：
   - 每次运行会覆盖同名的输出文件
   - 建议在运行前备份重要结果

## 🔍 故障排查

### 问题 1：评估模式未触发

**检查**：
- 是否使用了 `--evaluation` 参数
- 环境变量 `EVALUATE_WITH_RAGAS` 是否正确设置

### 问题 2：检索评估被跳过

**检查**：
- `ground_truth_example.json` 文件是否存在
- 文件是否在项目根目录

### 问题 3：RAGAS 评估失败

**检查**：
- 是否安装了 `ragas`：`pip install ragas`
- 网络连接是否正常
- API 密钥是否有效

### 问题 4：导入错误

**检查**：
- 是否在项目根目录运行
- `src` 目录是否在 Python 路径中
- 依赖包是否已安装

## 📚 相关文档

- [评估方法说明](../docs/EVALUATION_METHODS.md)
- [指标详解](../docs/METRICS_EXPLANATION.md)
- [生成评估说明](../docs/GENERATION_EVALUATION.md)
- [RAGAS 进度说明](../docs/RAGAS_PROGRESS_EXPLANATION.md)

## 📞 支持

如有问题或建议，请查看项目文档或联系开发团队。

