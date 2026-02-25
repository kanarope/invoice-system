# 請求書回収・分類・振込設定システム

他社からの請求書をAI/OCRで自動読み取りし、事業部別に分類、freee連携で振込設定まで行うWebアプリケーション。
電子帳簿保存法・インボイス制度に準拠。

## 技術スタック

| レイヤー | 技術 |
|---------|------|
| フロントエンド | Next.js 14 (App Router) + TypeScript + Tailwind CSS |
| バックエンド | Python FastAPI + SQLAlchemy |
| データベース | PostgreSQL |
| AI/OCR | OpenAI GPT-4o (Vision) |
| 会計連携 | freee API |
| メール取得 | Gmail API |
| コンプライアンス | 国税庁適格請求書発行事業者公表API |

## セットアップ

### 1. 環境変数

```bash
cp backend/.env.example backend/.env
# .env を編集してAPIキーを設定
```

### 2. Docker Compose で起動

```bash
docker-compose up -d db
```

### 3. バックエンド起動

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 4. フロントエンド起動

```bash
cd frontend
npm install
npm run dev
```

### 5. 初期ユーザー登録

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","name":"管理者","password":"admin123","role":"admin"}'
```

## 主な機能

- 請求書アップロード（ドラッグ&ドロップ、複数ファイル対応）
- AI/OCR自動読み取り（GPT-4o Vision）
- 適格請求書発行事業者番号の国税庁API照合
- インボイス制度記載要件チェック
- 事業部別分類（AI自動推定 + 手動変更）
- 承認フロー（確認→承認→振込設定）
- freee API連携（取引登録・振込設定）
- Gmail自動取得（請求書メールの自動収集）
- 電子帳簿保存法準拠（改ざん検知、訂正削除履歴、検索機能）
- ダッシュボード（ステータス別・事業部別集計）
- 監査ログ

## APIドキュメント

バックエンド起動後: http://localhost:8000/docs
