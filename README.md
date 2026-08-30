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

# 4. 验证检索（Phase 1，支持中英文跨语言查询）
python examples/demo_phase1.py --course COMP5310 --query "data exploration"
python examples/demo_phase1.py --course COMP5310 --query "数据探索"   # 中文也能搜英文课件

# 5. 一键备课（Phase 2，未配置 API key 时自动进入 mock 模式）
python examples/demo_phase2.py --course COMP5310 --topic "data exploration" --export

# 6. 作业讲题 / 期末复习 / 速查表 / 真题映射（Phase 3）
python examples/demo_phase3.py --task problem_solving --export
python examples/demo_phase3.py --task review --export
python examples/demo_phase3.py --task cheatsheet --export
python examples/demo_phase3.py --task exam_mapping --export

# 7. 统一任务评测（Phase 3，含资料外拒答测试）
python examples/demo_phase3.py --evaluate --export-eval

# 8. Phase 4 - 可靠性与展示（评测 + 成本/延迟 + 失败案例库）
python examples/demo_phase4.py --course COMP5310 --export

# 9. 启动本地教师工作台（Streamlit UI）
streamlit run app.py

# 10. 一条命令跑完整个演示闭环
bash examples/run_all.sh COMP5310

# 11. 运行测试
python -m pytest tests/ -v
```

## 📚 文档

| 文档 | 说明 |
|------|------|
| [📖 使用指南](docs/README_CN.md) | 完整说明、数据管理、常见问题 |
| [🏗️ 架构设计](docs/ARCHITECTURE.md) | 系统分层、技术选型、扩展点 |
| [📁 目录结构](docs/DIRECTORY_GUIDE.md) | 文件夹用途与数据组织 |
| [🎯 产品规划](docs/ai-tutoring-agent-product-plan-v1.md) | 产品需求与路线图 |
| [⚖️ 隐私与学术诚信](docs/PRIVACY_AND_INTEGRITY.md) | 数据、版权、诚信边界 |
| [🧭 产品决策记录](docs/decisions/) | ADR-001~005 关键取舍 |

## ✨ 核心功能

**Phase 1：可引用知识库 ✅**
- 📄 PDF / Markdown / 文本解析（保留页码与元数据）
- ✂️ 语义分块（精确字符位置追踪）
- 🔍 Embedding 语义检索（多语言、跨语言、离线，可切回 TF-IDF）
- 💾 本地 JSON 索引 + embedding 向量缓存

**Phase 2：RAG 生成 ✅**
- 🤖 基于课程资料生成讲解、讲题、复习、速查表
- 🔗 每条内容带来源页码引用
- 🧱 结构化输出（学习目标、前置知识、讲解、术语、例题、练习）
- ✅ 引用校验（识别幻觉页码/文档）
- ⚠️ 资料不足提醒
- 📤 Markdown / JSON / HTML 导出

**Phase 3：作业 / 真题 / 期末复习 ✅**
- ✏️ 作业讲题模式（分步思路 + 分层提示，不代写答案）
- 🗺️ 真题知识点映射（含资料未覆盖考点识别）
- 🎓 期末知识点地图（依赖关系 + 高频混淆点 + 自测题）
- 📋 两页 cheat sheet（版面约束 + 压缩建议）
- 🧪 统一任务评测（引用准确率、字段完整率、资料外拒答率）

**Phase 4：可靠性与展示版本 ✅**
- 🖥️ Streamlit 教师工作台（资料库 / 教学任务 / 生成结果 / 评测与失败案例）
- ⏱️ 成本与延迟监控（每次生成的耗时、tokens、预估成本）
- 📊 自动化评测报告（含成本/延迟明细，导出 MD / JSON）
- 🗂️ 失败案例库（自动收集 + 历史案例，产品规划 7.3）
- 🧭 产品决策记录（ADR-001~005）
- 📜 隐私、版权与学术诚信说明

## 🎯 五个教学任务

| 任务 | 输入 | 输出 |
|------|------|------|
| 💡 课程讲解 | 知识点 | 5-10 分钟讲解稿 |
| ✏️ 讲题解答 | 题目文本 | 分步解题思路 + 分层提示 |
| 🎓 期末复习 | 章节 | 知识点地图 + 自测题 |
| 📋 速查表 | 知识领域 | 两页速查表草稿 |
| 🗺️ 真题映射 | 真题/考点 | 知识点映射 + 覆盖缺口 |

## �️ 教师工作台（Streamlit UI）

`streamlit run app.py` 后打开四个区域：

- **📚 资料库**：查看文档/页数/解析质量、检索可视化（可展开来源片段）、上传 PDF/Markdown/文本重建索引
- **🎯 教学任务**：五个任务入口（不是空白聊天框），表单化输入
- **📄 生成结果**：结构化展示、来源引用展开、需老师确认项、老师编辑、导出 Markdown / HTML / JSON，并显示耗时与成本
- **📊 评测与失败案例**：查看最新评测报告与失败案例库，或在界面内一键运行评测

> 未配置 `DEEPSEEK_API_KEY` 时自动进入 mock 模式，UI 全流程可离线演示。

## 📊 项目结构

```
├── app.py       # Streamlit 教师工作台（Phase 4 UI）
├── src/         # 核心代码（core/document/retrieval/rag/prompts/eval）
├── tests/       # 单元与集成测试
├── examples/    # 演示脚本（demo_phase1/2/3/4 + run_all.sh）
├── docs/        # 文档（中文，含 ADR 决策记录）
├── data/        # 课程资料、索引、输出（含评测报告与失败案例库）
└── logs/        # 运行日志（usage.jsonl 成本/延迟记录）
```

---

**当前状态：** Phase 1-4 全部完成  
**最后更新：** 2026-08-30
