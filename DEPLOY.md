# デプロイ手順（Vercel + GitHub Pages）

## 概要

| 環境 | 役割 |
|---|---|
| **Vercel** | Django アプリ本体（DB・API・管理画面） |
| **GitHub Pages** | `https://amano02.github.io/this-is-me/` から Vercel へリダイレクト |

GitHub Pages では Python/Django を実行できないため、フル機能版は Vercel でホスティングします。

---

## 1. Neon で PostgreSQL を作成（無料）

1. https://neon.tech にサインアップ
2. 新規プロジェクト作成
3. **Connection string** をコピー（`postgres://...?sslmode=require` 形式）

---

## 2. Vercel にデプロイ

### 方法 A: Vercel ダッシュボード（推奨・初回）

1. https://vercel.com に GitHub アカウントでログイン
2. **Add New Project** → `amano02/this-is-me` を Import
3. 設定:
   - **Framework Preset**: Other
   - **Root Directory**: （空欄 = リポジトリルート）
   - **Build Command**: `cd backend && bash build.sh`
   - **Install Command**: `cd backend && pip install -r requirements.txt`
4. **Environment Variables** を追加:

| 変数名 | 値 |
|---|---|
| `DATABASE_URL` | Neon の接続文字列 |
| `DJANGO_SECRET_KEY` | ランダムな長い文字列 |
| `DJANGO_DEBUG` | `False` |
| `DJANGO_PRODUCTION` | `True` |
| `DJANGO_ALLOWED_HOSTS` | `.vercel.app,this-is-me.vercel.app,amano02.github.io` |

5. **Deploy** をクリック

### 方法 B: GitHub Actions（2回目以降の自動デプロイ）

1. Vercel ダッシュボード → Project Settings → General から `VERCEL_ORG_ID` / `VERCEL_PROJECT_ID` を取得
2. https://vercel.com/account/tokens で Token 作成
3. GitHub リポジトリ → Settings → Secrets → Actions に追加:
   - `VERCEL_TOKEN`
   - `VERCEL_ORG_ID`
   - `VERCEL_PROJECT_ID`
4. `main` へ push すると自動デプロイ

---

## 3. 初回デプロイ後

1. Vercel の URL（例: `https://this-is-me-xxx.vercel.app`）を確認
2. 管理画面: `https://your-url.vercel.app/admin/`
3. スーパーユーザー作成（Vercel CLI または Neon SQL コンソール経由で不可のため、ローカルから migrate 後に createsuperuser、または build.sh の seed データを利用）

ローカルから本番 DB に接続してスーパーユーザー作成:

```bash
cd backend
export DATABASE_URL="postgres://..."
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_initial_data
python manage.py createsuperuser
```

---

## 4. GitHub Pages

`main` ブランチのルート `index.html` が自動的に GitHub Pages で公開されます（リダイレクトページ）。

- URL: https://amano02.github.io/this-is-me/
- 設定: リポジトリ → Settings → Pages → Source: **Deploy from branch** → Branch: **main** / **/ (root)**

Vercel の確定 URL が分かったら、ルート `index.html` のリダイレクト先 URL を更新してください。

---

## トラブルシューティング

| 症状 | 対処 |
|---|---|
| 500 Error | Vercel Logs で `DATABASE_URL` 未設定を確認 |
| 静的ファイルが表示されない | `collectstatic` が build.sh で実行されているか確認 |
| 画像が表示されない | build 時に `seed_initial_data` が実行されているか確認 |
| CSRF エラー（お問い合わせ） | `CSRF_TRUSTED_ORIGINS` に Vercel URL を追加 |
