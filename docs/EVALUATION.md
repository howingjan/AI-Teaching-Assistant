# 评估体系（Evaluation）

> 面向「模型优化与评估」职责的回归评测：衡量检索质量与生成质量，确保改动
> （换 chunking、换 prompt、换检索策略）有可复现的量化依据，而非凭感觉。

## 1. 为什么需要

RAG 系统的质量由两段决定：**检索是否找对** + **生成是否忠于资料**。本目录提供：

| 层 | 指标 | 说明 |
|----|------|------|
| 检索 | Hit@k / Recall@k / MRR / Precision@k | 黄金问题集上，检索到的片段是否命中人工标注的相关片段 |
| 生成（可选） | 忠实度 / 答案相关性 | LLM-as-judge 打分（1–5），需配置 API key |
| 回归 | 同一套脚本可反复跑 | 改 prompt / 分块 / 检索前后跑一次，对比指标变化 |

## 2. 快速开始

```bash
# 内置演示语料（离线，不下载模型，快速体验完整流程）
python -m src.eval.run_eval --demo --retrievers bm25

# 对真实课程语料评估（BM25 纯关键词基线，无需下载 embedding 模型）
python -m src.eval.run_eval --course COMP5310 --retrievers bm25

# 评估全部三种检索（embedding / bm25 / hybrid，需下载 embedding 模型）
python -m src.eval.run_eval --course COMP5310

# 输出 JSON 报告
python -m src.eval.run_eval --course COMP5310 --out logs/eval_report.json

# 额外运行 LLM-as-judge 生成质量打分（需 DEEPSEEK_API_KEY）
python -m src.eval.run_eval --course COMP5310 --judge
```

## 3. 黄金问题集

黄金问题定义在 [golden_questions.json](../src/eval/golden_questions.json)，每条：

```json
{
  "id": "q001",
  "query": "什么是梯度下降？",
  "relevant_document_ids": [],
  "relevant_snippets": ["gradient descent", "梯度下降"],
  "relevant_chunk_ids": []
}
```

相关性的判定有两种方式（见 [golden.py](../src/eval/golden.py)）：

1. **`relevant_chunk_ids`（精确）**：直接标注相关 chunk id，最严格，适合在真实语料构建索引后人工标注；
2. **`relevant_snippets`（片段匹配）**：chunk 文本包含任一片段即视为相关。`relevant_document_ids` 为空表示不限文档。这种方式与 chunk id（由文件哈希生成）解耦，**跨语料可移植**，适合直接对 `data/COMP5310` 等课程运行。

> 当前内置的黄金集是「机器学习通识」示例。对真实课程，建议从课件里挑 10–20 个真实问题，
> 把相关知识点原文填进 `relevant_snippets`，即可得到有意义的基线。

## 4. 指标定义

对单条查询，设预测排序列表 `P`（长度 ≤ k）、相关集合 `R`：

- **Hit@k**：`R ∩ P` 非空则 1，否则 0。
- **Recall@k**：`|R ∩ P| / |R|`（截断到 1）。
- **MRR**：第一个相关片段排名的倒数（`1 / rank`），没命中为 0。
- **Precision@k**：`|R ∩ P| / |P|`。

汇总值为所有查询的算术平均。实现见 [metrics.py](../src/eval/metrics.py)。

## 5. 检索策略对比（为什么用 hybrid）

`--retrievers embedding bm25 hybrid` 会分别给出三组指标。预期结论：

- **BM25**：对「原词命中」强，但**跨语言失效**（中文问题检索英文课件时召回接近 0）；
- **Embedding**：跨语言语义召回强，但可能漏掉专有名词/公式的精确匹配；
- **Hybrid（RRF 融合）**：两者互补，通常获得最高的 Hit@k / Recall@k。

这正是 [retriever.py](../src/retrieval/retriever.py) 默认使用 hybrid 的量化依据。`BM25Retriever` 是本次为评测独立出的纯关键词基线检索器。

## 6. 生成质量（LLM-as-judge）

[judge.py](../src/eval/judge.py) 用 LLM 对生成结果打两个 1–5 分：

- **忠实度（faithfulness）**：答案的每一条陈述是否都能由检索到的资料支持（防幻觉）；
- **答案相关性（answer relevance）**：答案是否直接、完整地回答了问题。

评分需要 API key，无法离线；因此默认不跑，只在 `--judge` 时执行，便于把「需要花钱的打分」与「免费的检索指标」解耦。

## 7. 回归建议

- 改分块参数（chunk 大小 / overlap）后：跑 `--course <课程> --retrievers hybrid`，对比 Recall@k；
- 改提示词后：跑 `--judge`，对比忠实度 / 相关性；
- CI 中已加入 [test_eval_metrics.py](../tests/test_eval_metrics.py) 的离线单测，保证指标计算的正确性，不依赖模型或网络。
