# RAG Pipeline for Sports Injury Knowledge Base

## 项目结构

```
project-phase2/
├── src/                    # 源代码模块
│   ├── config.py          # 配置管理
│   ├── preprocessing/     # 预处理模块
│   ├── embedding/         # 向量化模块
│   ├── retrieval/         # 检索模块
│   ├── reranking/         # 重排序模块
│   ├── generation/        # 生成模块
│   ├── pipeline/          # 主流程模块
│   ├── utils/             # 工具模块
│   └── validation/        # 验证模块
├── tests/                 # 测试文件
├── docs/                  # 文档
├── data/                  # 数据文件
├── run_preprocessing.py   # 预处理入口
├── validate_ground_truth.py  # 验证入口
└── requirements.txt       # 依赖包
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

### 3. 运行预处理

```bash
python run_preprocessing.py --base-dir rag_papers
```

### 4. 运行测试

```bash
# 方式1: 从根目录运行（推荐）
python main.py

# 方式2: 交互式模式
python main.py interactive

# 方式3: 直接运行tests/main.py
python tests/main.py
```

### 5. 验证Ground Truth

```bash
python validate_ground_truth.py ground_truth_example.json --check-llm
```

## 模块说明

- **预处理**: PDF处理、文本分块、数据库初始化
- **向量化**: OpenAI embeddings生成
- **检索**: Elasticsearch向量检索和混合检索
- **重排序**: 交叉编码器重排序
- **生成**: Gemini API响应生成
- **验证**: Ground truth数据验证

## 使用示例

```python
from src.pipeline import RAGPipeline

# 初始化
pipeline = RAGPipeline()

# 查询
result = pipeline.query("What rehabilitation methods are most effective for treating knee injuries?")

print(result["response"])
```

