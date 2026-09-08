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
│   ├── retrieval/         # Embedding 检索器（e5-small，向量缓存）
│   ├── prompts/           # 备课 / 讲题提示词模板
│   ├── rag/               # llm_client / citation_validator / pipeline
│   └── eval/monitor.py    # 生成耗时与成本记录
├── tests/                 # 离线单元/集成测试（确定性假 LLM）
├── docs/                  # 本目录、架构、隐私、ADR
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

## 3. 需要知道的事

- **只支持 PDF** 课件（`Config.document.supported_formats`）。
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
| `src/retrieval/retriever.py` | `RetrieverFactory.create("embedding", ...)` |
| `src/rag/pipeline.py` | `generate_lesson` / `generate_problem_solution` / `generate_task` / 导出 |
| `src/prompts/teaching_templates.py` | 备课 / 讲题模板、按时长定内容规模、附加老师指令 |
| `app.py` | 页面编排与会话状态（course / reload_token / 结果缓存） |
