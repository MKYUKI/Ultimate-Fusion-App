# Dockerfile

# ビルドステージ
FROM python:3.10-slim AS builder

# 作業ディレクトリの設定
WORKDIR /app

# システム依存のパッケージをインストール
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# pipのアップグレード
RUN pip install --upgrade pip

# Poetryのインストール
RUN pip install poetry

# Poetryの設定をコピー
COPY poetry.lock pyproject.toml /app/

# 依存関係のインストール
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# 実行ステージ
FROM python:3.10-slim

# 作業ディレクトリの設定
WORKDIR /app

# ビルドステージから依存関係をコピー
COPY --from=builder /app /app

# アプリケーションコードをコピー
COPY . /app

# 新規ユーザーの作成
RUN useradd -m appuser

# 非特権ユーザーに切り替え
USER appuser

# ポートの公開
EXPOSE 8501

# 環境変数の設定
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ENABLECORS=false

# アプリケーションの実行
CMD ["streamlit", "run", "app.py"]
