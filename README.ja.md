# Dynaman - 動的スキーマ PoC

[Read in English](README.md)

**Dynaman** は、現代の **NoCode/LowCode プラットフォーム** における中心的なパターンである **未固定かつ動的なスキーマ** のアーキテクチャと実装を実証するために設計された Proof of Concept (PoC) プロジェクトです。

データベースモデルがハードコードされた従来のアプリケーションとは異なり、Dynaman ではユーザーが実行時にデータ構造（エンティティ/スキーマ）を定義できます。システムは、ユーザー定義の構造をサポートするために、コードの変更やデプロイを必要とせずに、検証ロジックと API エンドポイントを動的に生成します。

## 🎯 コアコンセプト

主な目的は、データの形状がコンパイル時に不明な **ユーザー定義要件** をどのように処理するかを示すことです。これは以下によって実現されます：

1.  **メタデータ駆動アーキテクチャ**: スキーマ定義（メタデータ）を実際のデータ（実行データ）とは別に保存します。
2.  **動的な Pydantic モデル**: 保存されたメタデータに基づいて、Python クラスと検証ルールをオンザフライで構築します。
3.  **スキーマレスストレージ**: MongoDB の柔軟性を利用して、アプリケーションレベルで厳格な検証を強制しながら、可変コンテンツを保存します。

## 🛠 技術スタック

### バックエンド・コア (`/engine`)
*   **言語**: Python 3.13+
*   **フレームワーク**: [FastAPI](https://fastapi.tiangolo.com/) (非同期 Web フレームワーク)
*   **データベースドライバ**: [Motor](https://motor.readthedocs.io/) (非同期 MongoDB ドライバ)
*   **バリデーション**: [Pydantic](https://docs.pydantic.dev/) (動的モデル作成)
*   **アーキテクチャ**: クリーンアーキテクチャ / ドメイン駆動設計 (DDD)。

### 認証サービス (`/auth-service`)
*   **言語**: Python 3.13+
*   **フレームワーク**: FastAPI
*   **セキュリティ**: JWT (JSON Web Tokens), ロールベースアクセス制御 (RBAC)

### インフラストラクチャ
*   **コンテナ化**: Docker & Docker Compose
*   **ゲートウェイ**: Nginx (リバースプロキシ)

### フロントエンド (`/dynaman-ui`)
*   **フレームワーク**: [React](https://react.dev/) (with Vite)
*   **言語**: TypeScript
*   **スタイリング**: [Tailwind CSS](https://tailwindcss.com/)
*   **UI コンポーネント**: [shadcn/ui](https://ui.shadcn.com/)
*   **状態/データ**: React Hooks, Axios

## ✨ 主な機能

*   **スキーマエディタ**: 新しいエンティティ（例：「製品」、「従業員」）をカスタムフィールドで定義するための専用 UI。
*   **サポートされているフィールドタイプ**:
    *   文字列 (String)、数値 (Number)、ブール値 (Boolean)
    *   **日付 (Date)** (バリデーション付き)
    *   **参照 (Reference)** (他の動的エンティティへのリンク)
*   **動的 CRUD API**:定義されたすべてのエンティティに対して自動的に生成される REST エンドポイント。
*   **データエクスプローラー**: 任意のエンティティのレコードを表示、検索、編集、削除するための汎用データグリッド。
*   **実行時バリデーション**: ユーザー定義のルール（必須フィールド、データ型）に基づいた堅牢なデータ整合性チェック。

## 🚧 最新の実装 (Sprint 3)

*   **マイクロサービスアーキテクチャ**: システムを `engine` (コア)、`auth-service` (ID管理)、`dynaman-ui` に分割しました。
*   **API ゲートウェイ**: **Nginx** リバースプロキシを実装し、トラフィックをルーティングします (`/api/v1/schemas` → engine metadata, `/api/v1/data` → engine execution, `/api/v1/auth` → auth-service)。
*   **認証とセキュリティ**:
    *   ログインとトークン管理を行う専用の **Auth Service**。
    *   セキュアなステートレス認証のための **JWT** (JSON Web Token) 実装。
    *   **RBAC** (ロールベースアクセス制御) の実装。ロール: `SYSTEM_ADMIN`, `USER_ADMIN`, `USER`。
*   **Docker 統合**: サービスのオーケストレーションのための完全な `docker-compose.yml` セットアップ。

## 📂 プロジェクト構成

```
dynaman/
├── auth-service/           # [NEW] 認証マイクロサービス
│   ├── api/                # Auth ルーター
│   ├── domain/             # ユーザーエンティティ & セキュリティロジック
│   └── main.py             # Auth エントリーポイント
│
├── engine/                 # Python バックエンド (コア)
│   ├── api/                # FastAPI ルーター
│   ├── execution_context/  # 実行時データレコードの処理
│   ├── metadata_context/   # スキーマ定義の処理
│   └── main.py             # エントリーポイント
│
├── dynaman-ui/             # React フロントエンド
│   ├── src/
│   │   ├── components/     # UI コンポーネント
│   │   ├── pages/          # アプリケーションビュー
│   │   └── context/        # [NEW] AuthContext
│
├── docker-compose.yml      # [NEW] コンテナオーケストレーション
└── nginx-gateway.conf      # [NEW] API ゲートウェイ設定
```

## 🚀 始め方

### 前提条件
*   Python 3.13+
*   Node.js 18+
*   MongoDB (ローカルで実行または Docker 経由)

### バックエンドのセットアップ
1.  `engine` ディレクトリに移動します:
    ```bash
    cd engine
    ```
2.  仮想環境を作成して有効化します:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Windows の場合は .venv\Scripts\activate
    ```
3.  依存関係をインストールします:
    ```bash
    pip install -r requirements.txt
    ```
4.  サーバーを起動します:
    ```bash
    fastapi dev main.py
    ```
    API は `http://localhost:8000` で利用可能になります。

### フロントエンドのセットアップ
1.  `dynaman-ui` ディレクトリに移動します:
    ```bash
    cd dynaman-ui
    ```
2.  依存関係をインストールします:
    ```bash
    npm install
    ```
3.  開発サーバーを起動します:
    ```bash
    npm run dev
    ```
    UI は `http://localhost:5173` で利用可能になります。

---

*このプロジェクトは教育およびデモンストレーションを目的としています。*

## 🤖 AI 開発

このプロジェクトは **GCA** (Gemini Code Assist) によって全面的に開発されました。
