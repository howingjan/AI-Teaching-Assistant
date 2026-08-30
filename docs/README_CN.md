# 📖 AI 教学助手 - 完整使用指南

## 项目简介

**AI 教学助手** 是一个为高校教师设计的智能补充教学系统。它利用 RAG (检索增强生成) 技术，帮助老师从课程资料自动生成讲解、练习和复习材料。

**核心价值：**
- 🎯 **节省时间** - 从"手工编写教案"到"智能生成"
- ✅ **确保准确** - 所有内容都有课程资料来源、完全可验证
- 🔒 **保护隐私** - 课程资料完全本地存储，不上传云端
- 🚀 **快速迭代** - 支持多次快速修改和导出

## 三个开发阶段

### Phase 1：可引用知识库 ✅ 已完成
**功能：** 将课程 PDF 自动转换为可搜索的知识库
- ✓ PDF 文本提取（保留页码和位置）
- ✓ 智能分块（句子级别，保证上下文连贯）
- ✓ Embedding 语义检索（多语言、跨语言，可切回 TF-IDF）
- ✓ 本地 JSON 索引 + embedding 向量缓存（支持离线使用）

**测试状态：** 34 项测试全部通过

---

### Phase 2：RAG 生成管道 ✅ 已完成
**功能：** 用 LLM 基于检索结果生成教学内容
- 将用户查询发送给检索引擎，获取相关课程内容
- 用专门的 Prompt 让 LLM 生成讲解
- 自动添加引用（"参见第 X 页"）
- 验证生成内容确实来自课程资料

**支持的任务：**
1. 💡 **课程讲解** - 讲述某个知识点，5-10 分钟讲义
2. ✏️ **讲题解答** - 逐步讲解作业题或考题
3. 🎓 **期末复习** - 重点汇总和典型例题
4. 📋 **速查表** - 术语定义、公式、常见误区

---

### Phase 3：作业 / 真题 / 期末复习 + 统一评测 ✅ 已完成
**功能：** 在备课包基础上扩展三个高价值教学场景，并加入可复现的评测层
- ✏️ **作业讲题模式** - 分步思路 + 分层提示（Level 1→3），不代写答案
- 🗺️ **真题知识点映射** - 真题 → 知识点，含资料未覆盖考点识别
- 🎓 **期末复习包** - 知识点地图（依赖关系）+ 高频混淆点 + 自测题 + 优先级建议
- 📋 **两页速查表** - 版面约束 + 压缩建议 + 篇幅估算
- 🧪 **统一任务评测** - 引用准确率、字段完整率、资料外拒答率、任务专项检查

```bash
# 讲题 / 复习 / 速查表 / 真题映射 / 评测
python examples/demo_phase3.py --task problem_solving --export
python examples/demo_phase3.py --task review --export
python examples/demo_phase3.py --task cheatsheet --export
python examples/demo_phase3.py --task exam_mapping --export
python examples/demo_phase3.py --evaluate --export-eval   # 统一评测
```

---

### Phase 4：可靠性与展示版本 ✅ 已完成
**功能：** 提供可面试/可展示的完整版本
- 🖥️ **Streamlit 教师工作台** - 资料库 / 教学任务 / 生成结果 / 评测与失败案例四个区域
- 📚 **资料库** - 上传 PDF/Markdown/文本、索引统计、检索可视化（可展开来源片段）
- 🎯 **教学任务** - 五个任务入口（本周备课 / 作业讲题 / 期末复习 / 速查表 / 真题映射）
- 📄 **生成结果** - 结构化展示 + 来源引用展开 + 老师编辑 + 导出 Markdown / HTML / JSON，显示耗时与成本
- ⏱️ **成本与延迟监控** - 每次生成的耗时、tokens、预估成本写入 `logs/usage.jsonl`
- 📊 **自动化评测报告** - 含成本/延迟明细，导出 MD / JSON
- 🗂️ **失败案例库** - 自动收集 + 历史案例（引用超范围、跨语言检索空结果等）
- 🧭 **产品决策记录** - ADR-001~005（检索/结构化输出/讲题模式/UI/失败文化）
- ⚖️ **隐私、版权与学术诚信说明** - `docs/PRIVACY_AND_INTEGRITY.md`

```bash
# 启动教师工作台
streamlit run app.py

# 可靠性与展示演示（评测 + 成本/延迟 + 失败案例库）
python examples/demo_phase4.py --course COMP5310 --export

# 一条命令跑完整个闭环
bash examples/run_all.sh COMP5310
```

---

## 安装和配置

### 环境要求
- Python 3.12（embedding 检索依赖 torch，暂不支持 3.14）
- 4GB 内存（推荐 8GB+，embedding 模型约需 1GB）
- 10GB 磁盘空间（含模型约 500MB）

### 安装步骤

```bash
# 1. 进入项目目录
cd /Users/missho/Desktop/AIPM/ai-teaching-assistant

# 2. 激活虚拟环境（Python 3.12）
source AIvenv312/bin/activate

# 3. 安装依赖（如果还未安装）
pip install -r requirements.txt

# 4. 配置 API 密钥（仅生成内容时需要）
cp .env.example .env
# 编辑 .env 文件，加入 DeepSeek API 密钥
```

### 确认安装成功

```bash
# 运行演示脚本
python examples/demo_phase1.py

# 输出应该显示：
# ✓ 4 个示例查询的检索结果
# ✓ 每个结果都包含页码和内容

# 运行测试
python -m pytest tests/ -v

# 应该显示：19 passed
```

---

## 文件和数据管理

### 课程资料放在哪？

**目录结构：**
```
data/courses/
├── COMP5310/                   # 按课程代码组织
│   ├── lectures/               # 讲义和 slides（PDF）
│   │   ├── 01_introduction.pdf
│   │   ├── 02_algorithms.pdf
│   │   └── 03_data_structures.pdf
│   │
│   ├── assignments/            # 作业题目（PDF 或 markdown）
│   │   ├── assignment1.pdf
│   │   └── assignment2.pdf
│   │
│   ├── exams/                  # 考试题和答案
│   │   └── final_exam.pdf
│   │
│   └── reference/              # 参考资料
│       ├── glossary.md         # 术语表
│       └── formulas.pdf        # 公式表
│
├── OTHER_COURSE/               # 其他课程
│
└── supplementary/              # 补习班课件和参考资料
    ├── tutoring_materials/     # 你之前做的补习班教案
    └── additional_resources/   # 补充资源（论文、博客等）
```

**支持的文件格式：**
- ✅ PDF（推荐）- 讲义、作业、考试
- ✅ Markdown (.md) - 笔记、手写大纲
- ✅ 纯文本 (.txt) - 快速笔记

**上传数据：**
```bash
# 方式 1：手动复制（简单）
cp ~/Downloads/COMP5310_*.pdf data/courses/COMP5310/lectures/

# 方式 2：命令行复制
cp ~/教学资料/COMP5310/* data/courses/COMP5310/
```

### 索引在哪？

自动生成的索引文件保存在 `data/index/`：
```
data/index/
├── COMP5310.json              # COMP5310 课程的索引
├── default.json               # 默认索引
└── my_course.json             # 其他课程的索引
```

**JSON 索引包含：**
- 文档元数据（标题、作者、文件大小）
- 分块信息（每个知识点的位置和关键词）
- 索引生成时间和版本信息

**不需要手动编辑索引文件。** 系统会自动维护。

### 生成的内容放在哪？

`data/output/` 包含系统生成的教学材料：
```
data/output/
├── lesson_plans/               # 生成的讲义
│   └── COMP5310_algorithms.md
├── problem_solutions/          # 生成的讲题
│   └── assignment1_solution.md
├── cheat_sheets/               # 生成的速查表
│   └── algorithms_cheatsheet.md
└── logs/                       # 生成过程的日志
```

---

## 使用示例

### 例子 1：快速验证系统

```bash
# 运行演示脚本（使用 mock 数据）
python examples/demo_phase1.py

# 输出：4 个示例查询 + 检索结果
```

### 例子 2：用真实课程数据

```python
from src.document.document_loader import DocumentLoader
from src.retrieval.retriever import RetrieverFactory
from src.core.config import Config

# 步骤 1：加载课程资料
loader = DocumentLoader(index_name="COMP5310")
loader.load_documents_from_directory("data/COMP5310/")
loader.save_index()

print(f"📚 已加载 {len(loader.documents)} 个文档")
print(f"📄 总共 {len(loader.chunks)} 个知识点")

# 步骤 2：创建检索器（默认 embedding，支持跨语言）
retriever = RetrieverFactory.create(
    Config.retriever.retriever_type,
    loader.chunks,
    loader.documents,
    model_name=Config.retriever.embedding_model,
    cache_path=str(Config.get_embedding_cache_path("COMP5310")),
)

# 步骤 3：执行搜索（中文查询也能匹配英文课件）
query = "数据探索"   # 会跨语言匹配到英文课件 "Data Exploration"
results = retriever.search(query, top_k=5)

# 步骤 4：查看结果
for i, result in enumerate(results, 1):
    print(f"\n结果 {i}：")
    print(f"  页码：第 {result.chunk.page_number} 页")
    print(f"  内容：{result.chunk.text[:200]}...")
    print(f"  相关度：{result.score:.3f}")
```

### 例子 3：运行测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试
python -m pytest tests/test_retriever.py -v

# 生成覆盖率报告
python -m pytest tests/ --cov=src --cov-report=html
```

---

## 常见问题

### Q: 系统能处理扫描的 PDF 吗？
**A:** 当前不能。Phase 1 使用文本提取。如果 PDF 中的内容只是扫描图片，系统会检测到并标记为 `SCANNED`。

**改进方案（Phase 2+）：**
- 添加 OCR（光学字符识别）
- 推荐使用 PaddleOCR（支持中文，准确率 > 95%）

### Q: 图片中的内容能被理解吗？
**A:** 不能。当前系统只提取纯文本。图片中的文字（如图表、示意图）会被忽略。

**未来改进：**
- Phase 3：集成图像理解模型，自动识别图表文本
- 现在的建议：对重要的图表，手工添加文字说明

### Q: 可以加载网络资源（如 Wikipedia）吗？
**A:** 不在 MVP 范围内。当前只支持本地文件。

**建议的替代方案：**
- 将网页保存为 PDF，放入 `data/supplementary/`
- 手工提取关键内容保存为 Markdown

### Q: 生成的讲解准确吗？
**A:** 取决于 Phase 2 的实现。Phase 1（当前）只负责检索，不生成。

**准确性保障（Phase 2）：**
- 所有生成的内容都带页码引用
- 可自动验证每句话是否来自课程资料
- 超出课程范围的问题会主动拒答

---

## 进阶使用

### 自定义检索器

当前默认使用 Embedding（多语言语义检索），可切换回 TF-IDF：

```python
from src.retrieval.retriever import RetrieverFactory
from src.core.config import Config

# 使用 Embedding（当前默认，跨语言语义检索）
retriever = RetrieverFactory.create(
    "embedding", chunks, documents,
    model_name=Config.retriever.embedding_model,
    cache_path=str(Config.get_embedding_cache_path("COMP5310")),
)

# 切换回 TF-IDF（精确关键词，可解释，无额外依赖）
retriever = RetrieverFactory.create("tfidf", chunks, documents)

# 未来可加 BM25
# retriever = RetrieverFactory.create("bm25", chunks, documents)
```

### 调整分块参数

在 `src/core/config.py` 中修改：

```python
document.chunk_max_tokens = 1000      # 每块最多 1000 字
document.chunk_overlap_sentences = 2  # 块之间重叠 2 个句子
document.max_chars_per_page = 5000    # 每页最多 5000 字
```

### 查看详细日志

```bash
# 启用 DEBUG 日志
export LOG_LEVEL=DEBUG
python examples/demo_phase1.py

# 日志会保存到 logs/ 文件夹
cat logs/*.log
```

---

## 故障排除

### 问题：运行报错 "ModuleNotFoundError"

**原因：** 依赖未正确安装或虚拟环境未激活

**解决：**
```bash
# 确保虚拟环境激活（Python 3.12）
source AIvenv312/bin/activate

# 重新安装依赖
pip install --force-reinstall -r requirements.txt
```

### 问题：搜索没有结果

**原因：** 
1. 课程资料未加载
2. 索引文件损坏
3. 查询词汇太特殊，数据中不存在

**解决：**
```bash
# 清除旧索引
rm data/index/*.json

# 重新加载数据
python examples/demo_phase1.py  # 使用 mock 数据测试

# 如果仍无结果，检查日志
cat logs/*.log
```

### 问题：内存占用过高

**原因：** 加载的课程资料太多

**解决：**
- 减少一次加载的文件数量
- 按课程分别建立索引（如 COMP5310.json、COMP5311.json）
- 增加系统内存

---

## 下一步

### 立即可做
1. ✅ 运行 `python examples/demo_phase1.py` 验证系统
2. 📋 运行 `python -m pytest tests/ -v` 检查所有测试（47 项）
3. 📁 准备你的 COMP5310 课程资料

### 短期（1-2 周）
1. 用真实课程跑统一评测（`demo_phase3.py --evaluate`）
2. 扩充评测问题集（加入更多真题、作业题和资料外问题）
3. 根据评测报告迭代提示词与检索参数

### 中期（2-4 周）
1. 构建 Phase 4 Streamlit UI（资料库 + 5 个任务入口）
2. 引入 embedding 检索并对照 TF-IDF 做评测对比
3. 增加失败案例库（解析失败、引用错误、资料冲突）

### 长期（1-2 个月）
1. 用真实课程进行端到端评测
2. 收集老师反馈并迭代
3. 按产品规划扩展学生端与自动批改

---

## 获取帮助

- 📚 查看本目录中的其他文档（ARCHITECTURE.md, DIRECTORY_GUIDE.md 等）
- 🔧 检查代码注释（每个文件都有详细的中英文说明）
- 📊 运行测试看系统是否正常工作
- 💬 在 Issues 中提出问题或建议

---

**最后更新：** 2026-08-29  
**版本：** Phase 3（作业/真题/期末复习 + 统一评测）
**下一版本：** Phase 4（Streamlit UI）
