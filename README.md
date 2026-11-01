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
#    界面：资料库 / 教学任务 / 新旧课件比对与更新

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

## �📚 文档

| 文档 | 说明 |
|------|------|
| [🏗️ 架构设计](docs/ARCHITECTURE.md) | 系统分层、技术选型、数据流 |
| [📁 目录结构](docs/DIRECTORY_GUIDE.md) | 文件夹用途与数据组织 |
| [⚖️ 隐私与学术诚信](docs/PRIVACY_AND_INTEGRITY.md) | 数据、版权、诚信边界 |
| [🧭 新旧课件比对执行方案](docs/AGENTIC_COURSE_MATERIAL_UPDATE_PLAN.md) | LangGraph 工作流、审核边界与后续阶段 |
| [🧭 产品决策记录](docs/decisions/) | ADR-001~004 关键取舍 |

## ✨ 核心功能

**Phase 1：可引用知识库 ✅**
- 📄 PDF 解析（保留页码与元数据，仅支持 PDF）
- ✂️ 语义分块（结构感知，≤400 token，精确字符位置追踪）
- 🔍 Hybrid 混合检索：多语言 embedding 语义召回 + BM25 关键词召回，并用 RRF 融合排序（本地运行）
- 💾 本地 JSON 索引 + embedding 向量缓存

**Phase 2：RAG 生成 ✅**
- 🤖 基于所选资料（可多选）生成备课 / 期末复习 / 作业讲题
- 📚 备课内容覆盖所选资料的**全部知识点**，并自动生成约 3 道练习题
- 🔗 每条内容带来源引用（页码 + chunk_id，防幻觉）
- 🧱 结构化输出（学习目标、前置知识、讲解、术语、例题、练习）
- ✅ 引用校验（识别幻觉页码/文档/片段）
- ⚠️ 资料不足提醒
- 📤 Markdown / JSON / HTML 导出

**Phase 3：作业讲题 / 期末复习 ✅**
- ✏️ 作业讲题模式（分步思路 + 分层提示，不代写答案）
- 🎓 期末复习已并入备课：全选全部资料即可生成覆盖整学期的复习材料

**Phase 4：可靠性与展示版本 ✅**
- 🖥️ Streamlit 教师工作台（资料库 / 教学任务，结果内联展示、可编辑并导出）
- ⏱️ 成本与延迟监控（每次生成的耗时、tokens、预估成本）
- 🧭 产品决策记录（ADR-001~004）
- 📜 隐私、版权与学术诚信说明

**Agentic Demo：新旧课件比对与更新**
- 🧭 LangGraph 编排 PDF/DOCX 解析、知识点抽取、Hybrid Search 证据召回和覆盖报告
- 🧑‍🏫 教师审核后，可把已选建议生成独立的 DOCX 修订副本；上传原件不被覆盖
- 📄 本机安装 LibreOffice 后可将修订版 DOCX 可选导出为 PDF
- 🔁 同名资料库课件替换须单独确认；替换前保留可在资料库页恢复的旧版本备份
- 🔒 使用前明确确认课件文本会发送到 DeepSeek API；文件解析、PDF 转换和索引替换均在本机进行
- 📄 单文件最大 50 MB、最多 120 个文本片段；更大的课件需拆分后比对

## 🎯 教学任务

| 任务 | 输入 | 输出 |
|------|------|------|
| 📖 备课 / 期末复习 | 资料多选（全选 = 期末复习） | 覆盖所选资料全部知识点的教学材料 + 约 3 道习题 |
| ✏️ 作业讲题 | 题目文本 + 资料范围 | 分步解题思路 + 分层提示（不代写答案） |

> 「资料范围」支持**多选**；生成前无需填写「本周主题」——内容范围完全由所选资料决定。
> 勾选「🎓 期末复习」会自动全选全部课件，生成覆盖整学期内容的复习/备课材料。

## �️ 教师工作台（Streamlit UI）

`streamlit run app.py` 后打开两个扁平化页面（无嵌套 tab）：

- **📚 资料库**：课程统计、文档清单（文件/类型/页数/解析质量/片段数）、上传 PDF 自动合并进知识库，并支持一键刷新
- **🎯 教学任务**：多选「资料范围」（勾选期末复习 = 全选全部资料）→ 选任务（备课·期末复习 / 作业讲题）→ 结果内联展示：来源引用、需确认项、可编辑，并导出 Markdown / HTML / JSON，同时显示耗时与成本
- **🆕 新旧课件比对**：覆盖报告、教师审核、DOCX 修订版与可选 PDF；可另外确认同名 PDF 资料替换，旧版可从资料库页回滚

> 只支持真实生成：必须配置 `DEEPSEEK_API_KEY`（.env），未配置时生成会报错提示。
> PDF 导出可选依赖本机 LibreOffice；未安装时仍可下载 DOCX 修订版。

## 📊 项目结构

```
├── app.py               # Streamlit 教师工作台（资料库 / 教学任务）
├── Dockerfile           # Docker 打包（含检索模型，不含课件）
├── docker-compose.yml   # 一键启动（数据挂载 ./data）
├── scripts/             # setup.sh 一键安装 / run.sh 一键启动 / 模型预下载
├── src/                 # 核心代码（core/document/retrieval/rag/prompts/eval）
├── tests/               # 单元与集成测试
├── docs/                # 文档（中文，含 ADR 决策记录）
├── data/                # 课程资料与索引（本地私有，不入镜像）
└── logs/                # 运行日志（usage.jsonl 成本/延迟记录，可选）
```

---

**当前状态：** Phase 1-4 全部完成  
**最后更新：** 2026-10-22
