# Ultimate Fusion App

![Favicon](./favicon.ico)

## 概要

**Ultimate Fusion App** は、最新の技術を駆使して構築された統合型Webアプリケーションです。主な機能には、EXIFデータ解析、テキスト音声合成（TTS）、GPTベースの対話機能、AI画像分類などが含まれます。ユーザーは、これらの機能をシームレスに利用できる直感的なインターフェースを提供します。

## 主な機能

- **ユーザー認証と登録**: 安全なログインとユーザー管理。
- **ファイルアップロードと処理**: テキスト、画像、PDF、Word文書などのアップロードと処理。
- **EXIFデータ解析と可視化**: 画像のEXIFデータを解析し、統計情報や視覚化を提供。
- **テキスト音声合成（TTS）**: 大量のテキストを音声に変換。
- **AI画像分類**: 画像をAIモデルで分類し、結果を表示。
- **GPT対話機能**: OpenAIのGPTモデルを使用した高度な対話システム。
- **ユーザーダッシュボードとフィードバック管理**: ユーザーのアクティビティログやフィードバックを管理。
- **プロフィール管理**: ユーザーのプロフィール情報と外部リンクの管理。

## 技術スタック

- **フロントエンド:** Streamlit
- **バックエンド:** Python, SQLAlchemy
- **データベース:** PostgreSQL
- **認証:** Streamlit Authenticator
- **API:** OpenAI, Google Cloud Text-to-Speech, Replicate
- **コンテナ化:** Docker, Docker Compose
- **その他:** Lottie, Matplotlib, Seaborn, Plotly, pytest

## セットアップ手順

### 前提条件

- **Python 3.10+**
- **Docker**（オプション、コンテナ化された環境での実行を希望する場合）
- **Google Cloud Text-to-Speech API キー**
- **OpenAI API キー**
- **Replicate API トークン**

### 1. リポジトリのクローン

```bash
git clone https://github.com/MKYUKI/Ultimate-Fusion-App.git
cd Ultimate-Fusion-App
