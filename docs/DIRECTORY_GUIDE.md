# 目录结构说明

> 快速了解每个文件夹/文件的用途，以及“课件从哪里来、索引存哪里、结果怎么导出”。

## 1. 顶层结构

```
.
├── app.py                 # Streamlit 教师工作台（唯一入口）
├── Dockerfile             # Docker 打包（含检索模型，不含课件）
├── docker-compose.yml     # 一键启动，卷挂载 ./data
├── requirements.txt       # Python 3.12 依赖
├── .env.example           # 环境变量模板（复制为 .env 填 API key）
├── scripts/
│   ├── setup.sh           # 一键安装（venv + 依赖 + 预下载模型 + 生成 .env）
│   ├── run.sh             # 一键启动
│   └── download_embedding_model.py  # 预下载检索模型到本地缓存
├── src/
│   ├── core/              # config.py 配置；models.py 数据模型
│   ├── document/          # PDF 解析 / 分块 / 索引（loader/parser/chunker）
│   ├── retrieval/         # Hybrid 检索（e5-small + BM25，RRF 融合排序）
│   ├── course_update/     # 比对、PDF 导出与可回滚的课程资料替换
│   ├── prompts/           # 备课 / 讲题提示词模板
│   ├── rag/               # llm_client / citation_validator / pipeline
│   └── eval/monitor.py    # 生成耗时与成本记录
├── tests/                 # 离线单元/集成测试（确定性假 LLM）
├── docs/                  # 本目录、架构、隐私、ADR
│   └── AGENTIC_COURSE_MATERIAL_UPDATE_PLAN.md  # 新旧课件比对与更新执行方案
├── data/                  # 课程资料与索引（本地私有，gitignored）
│   ├── <course>/          # 如 COMP5310：lectures/、assignments/、uploads/
│   └── index/             # <course>.json + <course>_embeddings.npy
└── logs/                  # usage.jsonl（可选）
```

## 2. 数据生命周期

1. **放入课件**：页面「📚 资料库」上传 PDF → 存入 `data/<course>/uploads/`；或手动放入
   `data/<course>/lectures` 等目录。
2. **建立索引**：首次加载会把该课程目录下 PDF 全部解析、分块并写入
   `data/index/<course>.json`（文档+片段+元数据）与 `<course>_embeddings.npy`（向量缓存）。
   之后每次加载会通过 `sync_directory` 自动合并磁盘上新增的文件；页面「🔄 刷新」可强制重建。
3. **生成**：教学任务按所选资料范围生成，结果内联在页面，可导出 Markdown / HTML / JSON。
4. **清理**：删除 `data/<course>` 即删除该课程全部资料与对应输出；索引需一并清理或刷新重建。

新旧课件比对任务将暂存于 `data/course_updates/<task_id>/`，包括输入副本、报告和修订版 DOCX；
教师审核后可另行确认替换课程资料库中的同名 PDF；旧版本备份保存在
`data/course_update_backups/<course>/<backup_id>/`，可在资料库页恢复。比对文本会发送到配置的 DeepSeek API。

## 3. 需要知道的事

- **只支持 PDF** 课件（`Config.document.supported_formats`）。
- 资料库仍只索引 PDF；独立的「新旧课件比对」支持学校 PDF 与补习 DOCX/PDF。
- 修订版 DOCX 可选导出 PDF；需要本机安装 LibreOffice（`soffice` 或 `libreoffice`）。
- 资料库替换需单独确认，先重建候选索引，成功后清除 embedding 缓存；旧 PDF 保留为可回滚备份。
- 比对需安装 `langgraph` 与 `python-docx`；单文件不超过 50 MB、最多 120 个文本片段。
- **真实生成**：必须在 `.env` 配置 `DEEPSEEK_API_KEY`；未配置时生成会报错。
- **Python 版本**：请使用 3.12（`AIvenv312`）。旧版 `AIvenv`（3.14）与过期规划文档已移除。
- **首次运行**会一次性下载检索模型（约 118MB，之后离线）；Docker 构建期已预下载进镜像。
- **测试是离线的**：`tests/` 用确定性假 LLM，不消耗 API、不要求联网。

## 4. 关键文件速查

| 文件 | 作用 |
|------|------|
| `src/core/config.py` | 路径、文档/检索/LLM/输出配置；`.env` 加载 |
| `src/core/models.py` | Document/Chunk/Citation/GeneratedLesson/GeneratedProblemSolution 等模型 |
| `src/document/document_loader.py` | 解析入库、索引存取、`sync_directory` 增量合并 |
| `src/retrieval/retriever.py` | Hybrid 检索器（embedding + BM25 + RRF） |
| `src/course_update/graph.py` | LangGraph 比对/审核流程及安全生成 DOCX 副本 |
| `src/course_update/library_update.py` | PDF 资料库替换、索引/缓存一致性、旧版本备份和回滚 |
| `src/course_update/pdf_export.py` | 可选 LibreOffice DOCX→PDF 转换与输出校验 |
| `docs/AGENTIC_COURSE_MATERIAL_UPDATE_PLAN.md` | 新旧课件比对、人工审核、DOCX 修订与安全更新执行方案 |
| `src/rag/pipeline.py` | `generate_lesson` / `generate_problem_solution` / `generate_task` / 导出 |
| `src/prompts/teaching_templates.py` | 备课 / 讲题模板、按时长定内容规模、附加老师指令 |
| `app.py` | 页面编排与会话状态（course / reload_token / 结果缓存） |
