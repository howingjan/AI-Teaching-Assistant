# 📁 目录结构和文件管理指南

## 完整目录树

```
ai-teaching-assistant/
│
├── 📚 文档（中文优先）
├── docs/
│   ├── README_CN.md                           ← 📖 完整使用指南（重点）
│   ├── ARCHITECTURE.md                        ← 🏗️  系统架构设计（含 Mermaid 图）
│   ├── DIRECTORY_GUIDE.md                     ← 📁 本文件
│   ├── ai-tutoring-agent-product-plan-v1.md  ← 🎯 完整产品规划
│   ├── PRIVACY_AND_INTEGRITY.md               ← ⚖️ 隐私/版权/学术诚信
│   └── decisions/                             ← 🧭 ADR-001~005 产品决策记录
│
├── 💾 主要代码
├── src/
│   ├── __init__.py
│   │
│   ├── core/                                  ← 核心数据和配置
│   │   ├── __init__.py
│   │   ├── models.py                          ✓ Document, Page, Chunk
│   │   └── config.py                          ✓ 全局配置管理
│   │
│   ├── document/                              ← 文档处理管道
│   │   ├── __init__.py
│   │   ├── pdf_parser.py                      ✓ PDF 文本提取
│   │   ├── text_chunker.py                    ✓ 语义分块
│   │   └── document_loader.py                 ✓ 统一加载器
│   │
│   ├── retrieval/                             ← 检索引擎
│   │   ├── __init__.py
│   │   └── retriever.py                       ✓ Embedding + TF-IDF 检索
│   │
│   ├── rag/                                   ← RAG 管道（Phase 2 + 3）
│   │   ├── __init__.py
│   │   ├── pipeline.py                        ✓ 任务编排 + 生成 + 导出
│   │   ├── llm_client.py                      ✓ DeepSeek API + mock 模式
│   │   └── citation_validator.py              ✓ 引用校验
│   │
│   ├── prompts/                               ← 提示词模板（Phase 2 + 3）
│   │   ├── __init__.py
│   │   └── teaching_templates.py              ✓ 5 类任务模板 + 消息组装
│   │
│   ├── eval/                                  ← 评测与可靠性（Phase 3 + 4）
│   │   ├── __init__.py
│   │   ├── evaluator.py                       ✓ TaskEvaluator + 报告导出
│   │   ├── case_sets.py                       ✓ 标准评测问题集（7 用例）
│   │   ├── monitor.py                         ✓ 成本/延迟监控（UsageMonitor）
│   │   └── failure_library.py                 ✓ 失败案例库
│   │
│   └── 🖥️ UI（Phase 4）
│   └── app.py                                 ✓ Streamlit 教师工作台
│
├── 🧪 测试
├── tests/
│   ├── __init__.py
│   ├── conftest.py                            ✓ pytest 配置
│   ├── test_models.py                         ✓ 数据模型测试（9）
│   ├── test_chunking.py                       ✓ 分块测试（7）
│   ├── test_rag.py                            ✓ Phase 2 RAG 测试
│   ├── test_phase3.py                         ✓ Phase 3 任务 + 评测测试
│   ├── test_phase4.py                         ✓ Phase 4 监控/失败库/UI 支撑
│   └── test_end_to_end.py                     ✓ 集成测试（3）
│
├── 🖥️ 演示脚本（examples/）
│   ├── demo_phase1.py                         ✓ 检索演示
│   ├── demo_phase2.py                         ✓ 备课演示
│   ├── demo_phase3.py                         ✓ 讲题/复习/速查表/真题 + 评测
│   ├── demo_phase4.py                         ✓ 可靠性与展示（评测+成本/延迟+失败库）
│   └── run_all.sh                             ✓ 一条命令跑完整个闭环
│
├── 📊 数据
├── data/
│   │
│   ├── courses/                               ← 👉 学校课程资料放这里
│   │   ├── COMP5310/                          # 按课程代码组织
│   │   │   ├── lectures/                      # 讲义、slides（PDF）
│   │   │   │   ├── 01_introduction.pdf
│   │   │   │   ├── 02_algorithms.pdf
│   │   │   │   ├── 03_data_structures.pdf
│   │   │   │   └── ...
│   │   │   │
│   │   │   ├── assignments/                   # 作业题目
│   │   │   │   ├── assignment1.pdf
│   │   │   │   ├── assignment2.md
│   │   │   │   └── ...
│   │   │   │
│   │   │   ├── exams/                         # 考试题和答案
│   │   │   │   ├── midterm_2025.pdf
│   │   │   │   └── final_2025.pdf
│   │   │   │
│   │   │   └── reference/                     # 参考资料
│   │   │       ├── glossary.md                # 术语表
│   │   │       ├── formulas.pdf               # 公式表
│   │   │       └── cheatsheet.md              # 快速参考
│   │   │
│   │   ├── COMP5311/                          # 其他课程（同样结构）
│   │   └── ...
│   │
│   ├── supplementary/                         ← 补习班课件和其他资源
│   │   ├── tutoring_materials/                # 你之前做的补习班教案
│   │   │   ├── week_1_intro.md
│   │   │   ├── week_2_practice.pdf
│   │   │   └── ...
│   │   │
│   │   └── additional_resources/              # 其他参考资料
│   │       ├── research_papers/               # 研究论文
│   │       ├── blog_posts/                    # 博客摘要
│   │       └── external_links.md              # 外部链接集合
│   │
│   ├── index/                                 ← 自动生成的索引
│   │   ├── COMP5310.json                      # COMP5310 的索引
│   │   ├── COMP5311.json                      # COMP5311 的索引
│   │   ├── default.json                       # 默认索引
│   │   └── supplementary.json                 # 补习班资料索引
│   │
│   └── output/                                ← 生成的教学材料
│       ├── lesson_plans/                      # 讲解教案（Phase 2）
│       │   ├── COMP5310_algorithms_lesson.md
│       │   └── ...
│       │
│       ├── problem_solutions/                 # 作业讲题（Phase 3）
│       │   ├── assignment1_problem_solution.md
│       │   └── ...
│       │
│       ├── reviews/                           # 期末复习包（Phase 3）
│       │   ├── final_review.md
│       │   └── ...
│       │
│       ├── cheat_sheets/                      # 速查表（Phase 3）
│       │   ├── two_page_cheatsheet.md
│       │   └── ...
│       │
│       ├── exam_mappings/                     # 真题知识点映射（Phase 3）
│       │   ├── exam_knowledge_mapping.md
│       │   └── ...
│       │
│       ├── eval/                              # 统一评测报告（Phase 3）
│       │   ├── phase3_evaluation_report.md
│       │   └── ...
│       │
│       └── logs/                              # 生成过程日志
│           ├── 2026-08-29_generate_lesson.log
│           └── ...
│
├── 📝 演示和配置
├── examples/
│   ├── demo_phase1.py                         ✓ Phase 1 检索演示
│   ├── demo_phase2.py                         ✓ Phase 2 备课包演示
│   └── demo_phase3.py                         ✓ Phase 3 讲题/复习/速查表/真题映射 + 评测
├── requirements.txt                           ✓ Python 依赖
├── .env.example                               ✓ 环境变量模板
├── .gitignore                                 ✓ Git 配置
└── README.md                                  ✓ 项目入口（简短中文）

├── 📋 其他
├── logs/                                      # 运行日志
│   └── *.log                                  # 自动生成的日志
│
└── 🐍 虚拟环境（不上传 Git）
    ├── AIvenv312/                             # Python 3.12（当前使用，支持 embedding）
    │   ├── bin/                               # 可执行文件
    │   └── lib/                               # 依赖包
    └── AIvenv/                                # Python 3.14（旧，仅支持 TF-IDF）
        └── ...
```

---

## 目录用途详解

### 📚 docs/ - 文档

| 文件 | 用途 | 何时阅读 |
|------|------|--------|
| README_CN.md | 🟢 **最重要** - 完整使用指南 | 第一次用系统时 |
| ARCHITECTURE.md | 理解系统设计、扩展点 | 想改代码或理解设计 |
| DIRECTORY_GUIDE.md | 本文件 - 文件夹说明 | 第一次放数据时 |
| ai-tutoring-agent-product-plan-v1.md | 产品规划（需求文档） | 深入理解产品 |

**建议：** 第一次用时按这个顺序阅读：
1. README.md（2 分钟概览）
2. docs/README_CN.md（10 分钟详细说明）
3. docs/DIRECTORY_GUIDE.md（本文，5 分钟了解文件夹）

---

### 💾 src/ - 源代码

#### src/core/
```
models.py (400 行)
  └─ 定义所有数据类型
     ├─ Document: 课程文档的元数据
     ├─ Page: 页面信息
     ├─ Chunk: 知识点片段（最重要）
     └─ SearchResult: 检索结果

config.py (180 行)
  └─ 全局配置
     ├─ DocumentConfig: PDF 处理参数
     ├─ RetrieverConfig: 搜索参数
     ├─ LLMConfig: LLM 参数（Phase 2）
     └─ OutputConfig: 输出格式参数
```

**何时修改：**
- ✏️ 需要改变块大小：编辑 `config.py` 中的 `chunk_max_tokens`
- ✏️ 需要改变搜索 top-k：编辑 `retriever_config.top_k`
- ✅ 很少需要修改 `models.py`（除非改数据结构）

---

#### src/document/
```
pdf_parser.py (250 行)
  └─ PDF 文本提取
     ├─ extract_text_from_pdf()
     ├─ get_pdf_stats()
     └─ 质量评估（GOOD/PARTIAL/SCANNED）

text_chunker.py (280 行)
  └─ 语义文本分割
     ├─ chunk_page()：单页分块
     ├─ chunk_pages()：多页分块
     └─ get_chunking_stats()：统计信息

document_loader.py (400 行)
  └─ 统一文档加载
     ├─ load_document()：加载单个文件
     ├─ load_documents_from_directory()：批量加载
     ├─ save_index()：保存索引
     └─ _load_index_from_disk()：读取索引
```

**工作流：**
```
用户上传 PDF
    ↓
document_loader.load_document()
    ↓
内部调用 pdf_parser.extract()
    ↓
内部调用 text_chunker.chunk_pages()
    ↓
返回 (Document, List[Chunk])
```

**何时修改：**
- ✏️ 支持新文件格式（Word、PPT）：添加新的 parser
- ✏️ 改变分块策略：编辑 `text_chunker.py`
- ✏️ 支持 OCR：在 `pdf_parser.py` 中添加

---

#### src/retrieval/
```
retriever.py
  ├─ EmbeddingRetriever: 当前默认（多语言语义检索）
  │   ├─ search()：主搜索方法
  │   ├─ _embed()：编码文本为向量
  │   └─ _get_chunk_embeddings()：加载/缓存向量
  │
  ├─ TFIDFRetriever: 可选（精确关键词匹配）
  │   ├─ search()：主搜索方法
  │   ├─ _tokenize()：分词
  │   └─ _compute_similarity()：相似度计算
  │
  └─ RetrieverFactory: 工厂模式
      ├─ create("embedding", ...)：创建 Embedding 检索器（默认）
      ├─ create("tfidf", ...)：创建 TF-IDF 检索器
      └─ create("bm25", ...)：[未来] BM25
```

**何时修改：**
- ✏️ 换 embedding 模型：编辑 `config.py` 中的 `embedding_model`
- ✏️ 改变 TF-IDF 参数（如 IDF 权重）：编辑 `_build_index()`
- ✏️ 添加 BM25 检索：实现 `class BM25Retriever(BaseRetriever)`

---

#### src/rag/ - RAG 管道（Phase 2 + Phase 3）
```
pipeline.py (✅ 已实现)
  └─ 编排整个 RAG 流程
     ├─ generate_lesson()            # Phase 2 备课包
     ├─ generate_problem_solution()  # Phase 3 作业/真题讲题
     ├─ generate_review()            # Phase 3 期末复习包
     ├─ generate_cheatsheet()        # Phase 3 两页速查表
     ├─ generate_exam_mapping()      # Phase 3 真题知识点映射
     ├─ generate_task()              # 统一任务分发
     └─ save_result() / export_*()   # Markdown/JSON 导出

llm_client.py (✅ 已实现)
  └─ LLM 接口封装
     ├─ DeepSeek API 调用（OpenAI 兼容）
     ├─ parse_json_response() 解析模型 JSON
     ├─ 重试逻辑
     └─ mock 模式（无 API key 时离线演示）

citation_validator.py (✅ 已实现)
  └─ 引用验证
     ├─ 检查 document_id 是否存在
     ├─ 检查页码是否在范围内
     └─ 解析出 chunk_id 和片段（供展示/导出）
```

---

#### src/prompts/ - 提示词模板（Phase 2 + Phase 3）
```
teaching_templates.py (✅ 已实现)
  ├─ SYSTEM_PROMPT                   # 系统提示词（讲师角色 + 只依据资料）
  ├─ LESSON_TEMPLATE                 # 备课包 JSON 输出 schema
  ├─ PROBLEM_SOLVING_TEMPLATE        # 讲题（教学辅导模式，不代写）
  ├─ REVIEW_TEMPLATE                 # 期末复习包
  ├─ CHEATSHEET_TEMPLATE             # 两页速查表
  ├─ EXAM_MAPPING_TEMPLATE           # 真题知识点映射
  ├─ build_*_messages()              # 各任务的 chat 消息组装
  └─ format_context()                # 检索片段 + 文档/页码格式化
```

---

#### src/eval/ - 统一评测（Phase 3）
```
evaluator.py (✅ 已实现)
  ├─ EvaluationCase                  # 单个评测问题（可标记 out_of_scope）
  ├─ TaskEvaluator                   # 运行用例并计算指标
  ├─ EvaluationReport                # 汇总报告（overall + by_task + 分用例）
  └─ to_markdown() / to_json()       # 报告导出
```

---

### 🧪 tests/ - 测试

```
conftest.py
  └─ pytest 配置（路径设置等）

test_models.py (200 行，9 个测试)
  ├─ test_document_creation
  ├─ test_document_requires_id_and_name
  ├─ test_empty_page_quality
  ├─ test_page_with_text
  ├─ test_chunk_cannot_be_empty
  ├─ test_chunk_char_end_auto_set
  ├─ test_chunk_creation
  ├─ test_search_result_score_validation
  └─ test_metadata_creation

test_chunking.py (250 行，7 个测试)
  ├─ test_chunk_empty_page
  ├─ test_chunk_ordering
  ├─ test_chunk_preservation_of_text
  ├─ test_chunk_single_page
  ├─ test_multiple_pages
  ├─ test_stats_calculation
  └─ test_stats_on_empty_chunks

test_end_to_end.py (200 行，3 个测试)
  ├─ test_document_loader_with_mock_documents
  ├─ test_end_to_end_flow
  └─ test_retriever_on_mock_index
```

**运行测试：**
```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行单个文件
python -m pytest tests/test_models.py -v

# 生成覆盖率报告
python -m pytest tests/ --cov=src --cov-report=html
```

**测试不会删除的原因：**
1. Phase 2 会改动分块/检索算法，需要回归测试
2. 引用准确率 > 90% 需要持续验证
3. 新增功能（如 OCR）需要新测试用例

---

### 📊 data/ - 数据管理

#### data/courses/ - 你的课程资料

**推荐组织方式：**

```
data/courses/
├── COMP5310/                    ← 【推荐】按课程代码组织
│   ├── lectures/                ← 讲义和 slides
│   ├── assignments/             ← 作业题
│   ├── exams/                   ← 考试
│   └── reference/               ← 参考资料
│
├── MATH101/                     ← 其他课程
│   ├── lectures/
│   └── ...
│
└── [添加更多课程]
```

**支持的文件格式：**
- ✅ PDF（首选）- 讲义、作业、考试
- ✅ Markdown (.md) - 笔记、教案
- ✅ 纯文本 (.txt) - 快速笔记
- ❌ Word (.docx) - Phase 2 中考虑支持
- ❌ PPT (.pptx) - Phase 2 中考虑支持
- ❌ 扫描图片 - Phase 2 中考虑支持 OCR

**上传文件的方式：**

```bash
# 方式 1：直接复制（推荐）
cp ~/我的文件/COMP5310_slides.pdf data/courses/COMP5310/lectures/

# 方式 2：拖拽复制（GUI）
# 在 Finder 中打开 data/courses/COMP5310/lectures/
# 拖拽 PDF 文件进去

# 方式 3：批量复制
cp ~/教学资料/COMP5310/* data/courses/COMP5310/
```

---

#### data/supplementary/ - 补习班资料

```
data/supplementary/
├── tutoring_materials/           ← 你之前做的补习班教案
│   ├── week_1_intro.md
│   ├── week_2_recursion.pdf
│   └── ...
│
└── additional_resources/         ← 其他参考资源
    ├── research_papers/          # 研究论文摘要
    ├── blog_posts/               # 有用的博客文章
    └── external_links.md         # 参考链接集合
```

**用途：** 补充学校课件，提供额外上下文

---

#### data/index/ - 自动生成的索引

```
data/index/
├── COMP5310.json                ← 加载 COMP5310 后自动生成
├── COMP5311.json                ← 加载 COMP5311 后自动生成
├── supplementary.json           ← 补习班资料索引
└── default.json                 ← 默认索引
```

**JSON 索引包含：**
```json
{
  "metadata": {
    "created_at": "2026-08-29T10:00:00",
    "total_documents": 5,
    "total_chunks": 250,
    "document_ids": ["doc_001", "doc_002", ...]
  },
  "documents": {
    "doc_001": {
      "document_id": "doc_001",
      "file_name": "01_introduction.pdf",
      "total_pages": 10,
      "file_size_mb": 2.5
    },
    ...
  },
  "chunks": [
    {
      "chunk_id": "doc_001_0_0",
      "document_id": "doc_001",
      "page_number": 0,
      "text": "...",
      "char_start": 0,
      "char_end": 250
    },
    ...
  ]
}
```

**不要手工编辑索引文件。** 系统会自动管理。

---

#### data/output/ - 生成的内容

```
data/output/
├── lesson_plans/                ← 讲解教案（Phase 2 生成）
│   ├── COMP5310_algorithms.md
│   └── COMP5310_data_structures.md
│
├── problem_solutions/           ← 讲题答案（Phase 2 生成）
│   ├── assignment1_solution.md
│   └── exam_questions_explained.md
│
├── cheat_sheets/                ← 速查表（Phase 2 生成）
│   └── algorithms_quick_ref.md
│
└── logs/                         ← 生成日志
    ├── 2026-08-29_generate_lesson.log
    └── ...
```

**这些文件是生成的，可以随时删除。** 需要的话再重新生成。

---

### 📝 配置文件

| 文件 | 用途 | 修改频率 |
|------|------|--------|
| requirements.txt | Python 依赖清单 | 很少（增加新库时） |
| .env.example | 环境变量模板 | 很少 |
| .env | 你的配置（不上传） | 根据需要 |
| .gitignore | Git 排除规则 | 很少 |
| README.md | 项目入口 | 很少 |

**创建 .env 文件：**
```bash
cp .env.example .env

# 编辑 .env
DEEPSEEK_API_KEY=sk_xxxxxxxxxxxx
LOG_LEVEL=INFO  # 可选
```

---

## 最佳实践

### ✅ 推荐做法

1. **文件组织**
   - 按课程代码组织 data/courses/
   - 讲义、作业、考试分别存放
   - 给文件起有意义的名字（01_introduction.pdf）

2. **数据备份**
   - 在 Git 中跟踪 data/courses/（课程资料）
   - 不跟踪 data/index/ 和 data/output/（自动生成）
   - 定期备份到云端或外部硬盘

3. **索引管理**
   - 让系统自动管理索引
   - 不要手工编辑 JSON 文件
   - 需要重建时删除旧索引，重新运行加载器

4. **测试**
   - 每添加新课程后运行测试
   - 验证 examples/demo_phase1.py 能正常工作
   - 检查生成的讲解质量

### ❌ 避免做法

- ❌ 在 src/ 中存放数据或索引
- ❌ 手工编辑 JSON 索引文件
- ❌ 混合不同课程的资料到同一文件夹
- ❌ 上传 .env 或 API 密钥到 Git
- ❌ 保存超大文件（>100MB）到 data/

---

## 常见任务

### 任务 1：上传新课程

```bash
# 1. 创建课程文件夹
mkdir -p data/courses/COMP5310/{lectures,assignments,exams,reference}

# 2. 复制文件
cp ~/我的文件/讲义*.pdf data/courses/COMP5310/lectures/
cp ~/我的文件/作业*.pdf data/courses/COMP5310/assignments/

# 3. 验证文件存在
ls data/courses/COMP5310/lectures/

# 4. 加载到系统
python3 -c "
from src.document.document_loader import DocumentLoader
loader = DocumentLoader(index_name='COMP5310')
loader.load_documents_from_directory('data/courses/COMP5310/')
loader.save_index()
print(f'已加载 {len(loader.chunks)} 个知识点')
"
```

---

### 任务 2：生成讲解（Phase 2 后）

```bash
# 1. 准备查询
query = "什么是递归算法?"

# 2. 运行生成（Python）
python3 -c "
from src.document.document_loader import DocumentLoader
from src.rag.pipeline import RAGPipeline

# 加载索引
loader = DocumentLoader(index_name='COMP5310')
loader._load_index_from_disk()

# 生成讲解
pipeline = RAGPipeline(retriever, llm_client)
result = pipeline.explain_concept('$query')

# 保存结果
with open('data/output/lesson_plans/explanation.md', 'w') as f:
    f.write(result)
"
```

---

### 任务 3：删除过期索引

```bash
# 删除所有索引（会重新生成）
rm data/index/*.json

# 删除生成的讲解
rm data/output/lesson_plans/*.md

# 删除日志
rm logs/*.log
```

---

### 任务 4：检查数据统计

```bash
python3 -c "
from src.document.document_loader import DocumentLoader

loader = DocumentLoader(index_name='COMP5310')
loader._load_index_from_disk()

stats = loader.get_index_stats()
print(f'文档数：{stats[\"total_documents\"]}')
print(f'知识点数：{stats[\"total_chunks\"]}')
print(f'总文件大小：{stats[\"total_size_mb\"]:.1f}MB')
"
```

---

## 文件大小参考

| 组件 | 典型大小 | 备注 |
|------|--------|------|
| 单个 PDF（讲义） | 1-5 MB | 20-30 页的 slides |
| 100 个 chunks 的索引 | ~100 KB | 很轻量 |
| 1000 个 chunks 的索引 | ~1 MB | 仍很轻量 |
| 生成的讲解（Markdown） | 10-50 KB | 2000-5000 字 |
| 整个项目（含 AIvenv） | ~450 MB | 大部分是虚拟环境 |

---

## 磁盘空间建议

| 配置 | 所需空间 | 适用于 |
|------|--------|------|
| 最小（1-2 门课） | 1 GB | 个人学习、演示 |
| 中等（5-10 门课） | 5 GB | 多个课程 |
| 大型（20+ 门课） | 20+ GB | 整个学期或年份 |

---

**最后更新：** 2026-08-29  
**版本：** 1.0  
**相关文档：** [使用指南](README_CN.md) | [架构设计](ARCHITECTURE.md)
