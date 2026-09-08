# syntax=docker/dockerfile:1
# ============================================================
# AI 教学助手 - Docker 镜像
#
# 构建（在项目根目录）：
#   docker build -t ai-teaching-assistant .
# 运行：
#   cp .env.example .env        # 填入 DEEPSEEK_API_KEY 后
#   docker compose up -d
# 然后浏览器打开 http://localhost:8501
#
# 说明：
#   - torch 使用官方 CPU wheel（体积小、够用），面向 linux/amd64；
#     若你在 Apple Silicon（arm64）上构建，请注释掉下方 CPU index 那行，
#     直接 `RUN pip install -r requirements.txt`（会拉取通用 torch）。
#   - 检索模型在“构建期”下载并打进镜像（HF_HOME=/app/.hf），运行期可离线。
#   - 课件 data/ 不进镜像，通过 docker-compose 卷挂载，保护隐私与版权。
# ============================================================
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/app/.hf \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# OpenMP 运行库（torch 依赖）
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 先装 CPU 版 torch（避免拉取数 GB 的 CUDA 依赖）
# 注：linux/arm64 用户请注释掉下面一行
RUN pip install --index-url https://download.pytorch.org/whl/cpu "torch==2.2.2"

# 其余依赖（requirements.txt 里 torch==2.2.2 会命中已装的 2.2.2+cpu，不会重装）
COPY requirements.txt ./
RUN pip install -r requirements.txt

# 构建期预下载检索模型 -> 打入镜像，运行期离线可用
COPY scripts/download_embedding_model.py ./scripts/download_embedding_model.py
RUN python scripts/download_embedding_model.py

# 应用代码
COPY app.py ./
COPY src ./src
COPY README.md ./

# 非 root 运行
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8501

CMD ["streamlit", "run", "app.py", \
     "--server.address=0.0.0.0", \
     "--server.port=8501", \
     "--server.headless=true", \
     "--server.fileWatcherType=none"]
