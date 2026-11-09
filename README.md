# 🎓 AI 教学助手

> 为高校教师打造的 AI 补充教学系统 | 从课程资料到教学内容一站式生成

## ⚡ 快速开始

> 需要 Python 3.12 环境（embedding 检索依赖 torch，暂不支持 Python 3.14）。

```bash
# 1. 激活虚拟环境（Python 3.12）
source AIvenv312/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置 API（生成内容时需要）
cp .env.example .env   # 编辑 .env 添加 DEEPSEEK_API_KEY

# 4. 启动本地教师工作台（Streamlit UI，默认加载 COMP5310 课程）
streamlit run app.py
#    界面：资料库 / 教学任务 / 新旧课件比对

# 5. 运行测试
python -m pytest tests/ -v

# 说明：只支持真实生成；必须配置 DEEPSEEK_API_KEY（.env），未配置时生成会报错提示。
```

## � 给别人用 / 换机器跑

本项目是**本地私有工具**：课件与索引只在本地 `data/`，Docker 镜像与仓库代码不含任何课件。

### 🐳 方式一：Docker（推荐给不熟 Python 的老师）

```bash
# 1) 准备 .env（填入 DEEPSEEK_API_KEY）
cp .env.example .env

# 2) 构建并启动（首次会下载依赖 + 检索模型，约几分钟）
docker compose up -d --build

# 3) 浏览器打开 http://localhost:8501
#    把课件 PDF 放入 ./data/<课程名>/uploads 或在页面「📚 资料库」上传
```

> 镜像面向 linux/amd64（CPU 版 torch，体积更小）。Apple Silicon 构建失败时，
> 删除 `Dockerfile` 中 `--index-url https://download.pytorch.org/whl/cpu` 那行再 build。
> 资料通过 `./data` 卷持久化，升级/重建容器不丢课件与索引。

### 🛠 方式二：一键脚本（macOS / Linux，需已装 Python 3.12）

```bash
./scripts/setup.sh        # 建 .venv + 装依赖 + 预下载检索模型 + 生成 .env
# 编辑 .env 填入 DEEPSEEK_API_KEY 后：
./scripts/run.sh          # 启动，浏览器打开 http://localhost:8501
```

### ❓ 首次使用常见问题

- **为什么首次安装很久？** 需安装 torch（约 2-3 GB），并一次性下载检索模型（约 118MB，之后可离线）。
- **模型下载失败/太慢？** 配置代理后重跑 `python scripts/download_embedding_model.py`；国内可用镜像：`export HF_ENDPOINT=https://hf-mirror.com` 后重跑。
- **没有课件怎么办？** 在「📚 资料库」上传 PDF；或放入 `data/<课程名>/lectures`、`uploads` 后点「🔄 刷新」。
- **只支持真实生成**：请务必在 `.env` 填入 `DEEPSEEK_API_KEY`，未配置时生成会报错提示。

## 🛠 技术栈（对齐岗位关键词）

| 领域 | 实现 |
|------|------|
| RAG / 检索 | Hybrid 混合检索：`multilingual-e5-small` embedding + BM25 + RRF 融合（本地运行） |
| 防幻觉 | 引用校验 `CitationValidator`：幻觉页码/文档/片段进入 `needs_review`，不静默放行 |
| 结构化输出 | 提示词模板 + `json_object` + 抗截断的平衡括号 JSON 解析 |
| 课件比对 | 线性流水线编排「新旧课件比对」（校验 → 解析 → 知识点 → 证据 → 报告），人工审核在 UI 完成 |
| 文档智能 | PDF（`pdfplumber`）+ DOCX（`python-docx`）解析、分块与来源定位 |
| 多模型后端 | DeepSeek / OpenAI / Azure OpenAI，环境变量切换 |
| 可观测性 | UsageMonitor 记录每次生成的耗时 / tokens / 预估成本 |
| 工程实践 | Docker + docker-compose、GitHub Actions CI（lint + 测试 + 覆盖率）与 GHCR 发布 |
| 安全与治理 | 本地检索优先（资料不出本机）、非 root 容器、无 key 不降级 |

## ✨ 核心能力

**知识库与检索**
- 📄 PDF 解析（保留页码与元数据），语义分块（结构感知，≤400 token）
- 🔍 Hybrid 混合检索：多语言 embedding + BM25 + RRF 融合，向量缓存到磁盘
- 💾 本地 JSON 索引 + embedding 向量缓存（本地优先，资料不出本机）

**RAG 生成**
- 🤖 基于所选资料（可多选）生成备课 / 期末复习 / 作业讲题
- 📚 备课覆盖所选资料全部知识点，自动生成约 3 道练习题；按课堂时长调整内容规模
- 🔗 每条内容带来源引用（页码 + chunk_id），结构化输出 + 引用校验防幻觉
- ✏️ 作业讲题模式：分步思路 + 分层提示，不代写答案
- 📤 Markdown / JSON / HTML 导出

**新旧课件比对**
- 🧭 上传最新学校 PDF + 往期补习 DOCX/PDF，顺序流水线串联校验、解析、知识点抽取、
  Hybrid Search 证据召回与覆盖报告
- 🧑‍🏫 逐项教师审核：covered / partial / missing / conflict / uncertain 五态 + 原文证据
- 📄 报告可下载 JSON / Markdown；比对只生成报告，不改写原件、不更新资料库

**可观测性**
- ⏱️ 耗时 / tokens / 成本监控

## 🎯 教学任务

| 任务 | 输入 | 输出 |
|------|------|------|
| 📖 备课 / 期末复习 | 资料多选（全选 = 期末复习） | 覆盖所选资料全部知识点的教学材料 + 约 3 道习题 |
| ✏️ 作业讲题 | 题目文本 + 资料范围 | 分步解题思路 + 分层提示（不代写答案） |

> 「资料范围」支持**多选**；生成前无需填写「本周主题」——内容范围完全由所选资料决定。
> 勾选「🎓 期末复习」会自动全选全部课件，生成覆盖整学期内容的复习/备课材料。

## 🧭 教师工作台（Streamlit UI）

`streamlit run app.py` 后打开三个扁平化页面（无嵌套 tab）：

- **📚 资料库**：课程统计、文档清单（文件/类型/页数/解析质量/片段数）、上传 PDF 自动合并进知识库，并支持一键刷新
- **🎯 教学任务**：多选「资料范围」（勾选期末复习 = 全选全部资料）→ 选任务（备课·期末复习 / 作业讲题）→ 结果内联展示：来源引用、需确认项、可编辑，并导出 Markdown / HTML / JSON，同时显示耗时与成本
- **🆕 新旧课件比对**：上传学校 PDF 与补习 DOCX/PDF → 带证据的覆盖报告（五态 + 原文引用），可下载 JSON / Markdown

> 只支持真实生成：必须配置 `DEEPSEEK_API_KEY`（.env），未配置时生成会报错提示。

## 📊 项目结构

```
├── app.py               # Streamlit 教师工作台（资料库 / 教学任务 / 课件比对）
├── src/core/runtime.py  # 共享的知识库加载与 pipeline 构建（UI 复用）
├── src/course_update/   # 课件比对流水线与覆盖报告
├── .github/workflows/   # CI（lint + 测试 + 覆盖率）与 Docker 发布
├── Dockerfile           # Docker 打包（含检索模型，不含课件）
├── docker-compose.yml   # 一键启动（数据挂载 ./data）
├── scripts/             # setup.sh 一键安装 / run.sh 一键启动 / 模型预下载
├── src/                 # 核心代码（core/document/retrieval/rag/prompts/course_update）
├── tests/               # 单元与集成测试
├── data/                # 课程资料与索引（本地私有，不入库、不入镜像）
└── logs/                # 运行日志（usage.jsonl 成本/延迟记录，可选）
```

---

**当前状态：** RAG 主线（知识库 → 检索 → 生成 → 引用校验 → 部署）与课件比对均已落地。  
**最后更新：** 2026-11-08
