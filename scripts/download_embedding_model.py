"""预下载本地检索用 embedding 模型，避免首次运行时联网等待。

模型：intfloat/multilingual-e5-small（约 118MB，多语言/跨语言，适合中英混合课件）
下载位置：默认 HuggingFace 缓存目录（可用环境变量 HF_HOME 覆盖，如 Docker 内设为
          /app/.hf 并随镜像一起打包）。
用法：
    python scripts/download_embedding_model.py
"""

from pathlib import Path


def main() -> None:
    from sentence_transformers import SentenceTransformer

    model_name = "intfloat/multilingual-e5-small"
    print(f">>> 加载 / 下载模型：{model_name} …")
    model = SentenceTransformer(model_name)  # 若不在缓存会自动下载
    # 触发一次编码，确保权重真正加载完成
    model.encode(["hello 你好，世界"])
    import os

    cache_dir = os.environ.get(
        "HF_HOME", str(Path.home() / ".cache" / "huggingface")
    )
    print(f"✅ 检索模型已就绪（缓存目录：{cache_dir}），可离线运行。")
    print(
        "   若下载缓慢/失败：请设置 https_proxy 后重试，"
        "或参考 https://hf-mirror.com 配置镜像。"
    )


if __name__ == "__main__":
    main()
