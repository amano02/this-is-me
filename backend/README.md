# Portfolio Backend (Django + PostgreSQL)

`this-is-me` ポートフォリオサイトのデータ管理を行う Django バックエンドです。
Phase 1 の成果物として、プロジェクト構成・DBモデル・管理画面（Django Admin）を実装しています。

## 構成

```
backend/
├── manage.py
├── config/            # プロジェクト設定 (settings/urls/wsgi/asgi)
├── apps/
│   ├── core/          # サイトプロフィール・SNSリンク・ヒーロースライダー
│   ├── works/         # ジャンル・作品・作品メディア・タグ・使用ツール（中核）
│   └── contact/       # お問い合わせメッセージ
├── templates/         # プロジェクト共通テンプレート（今後追加）
├── static/            # 開発用の静的ファイル
├── media/             # アップロードされた画像・動画・音声（gitignore対象）
├── requirements.txt
├── .env.example       # 環境変数のサンプル
└── .env               # 実際の環境変数（gitignore対象、各自作成）
```

## データモデル概要

| モデル | 役割 |
|---|---|
| `core.SiteProfile` | 表示名・肩書き・出身地・誕生日・自己紹介など（1件のみ） |
| `core.SnsLink` | SiteProfile に紐づく SNS リンク一覧 |
| `core.HeroSlide` | トップページのフルスクリーンスライダー画像 |
| `works.Genre` | 作品ジャンル（イラスト、3DCG、音楽など）。管理画面から追加・並び替え可能 |
| `works.Work` | 作品本体。タイトル・解説・制作日・制作時間・タグ・使用ツール・公開状態など |
| `works.WorkMedia` | 作品に紐づく複数メディア（画像／動画／音声／外部埋め込み／PDF等） |
| `works.Tag` | 作品に付与する自由タグ（検索・絞り込みに利用） |
| `works.WorkTool` | 使用ツール（Illustrator, Blender 等） |
| `contact.ContactMessage` | お問い合わせフォームの送信内容 |

## セットアップ手順

### 1. 仮想環境と依存パッケージ

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. PostgreSQL データベースの準備

既存の PostgreSQL サーバーに以下のようにDBとユーザーを作成してください。

```sql
CREATE USER portfolio_user WITH PASSWORD 'お好きなパスワード';
CREATE DATABASE portfolio_db OWNER portfolio_user ENCODING 'UTF8';
GRANT ALL PRIVILEGES ON DATABASE portfolio_db TO portfolio_user;
```

> **開発環境メモ**: このリポジトリの検証では、システムの PostgreSQL サービスへの
> root 権限がなかったため、ユーザー権限で動作する独自データディレクトリ
> (`backend/pgdata`, ポート `5433`, Unixソケット `/tmp`) を作成して動作確認を行いました。
> 通常の PostgreSQL サーバー（ポート5432など）を使う場合は `.env` の `DB_HOST` / `DB_PORT` を
> 環境に合わせて変更してください。
>
> 検証用サーバーの起動/停止コマンド:
> ```bash
> export PATH="/Library/PostgreSQL/15/bin:$PATH"
> pg_ctl -D backend/pgdata -l backend/pgdata_logfile.log -o "-p 5433 -k /tmp" start
> pg_ctl -D backend/pgdata stop
> ```

### 3. 環境変数

```bash
cp .env.example .env
# .env を開き、DB接続情報・SECRET_KEY等を編集
```

### 4. マイグレーションとスーパーユーザー作成

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. 開発サーバー起動

```bash
python manage.py runserver
```

`http://127.0.0.1:8000/admin/` から管理画面にログインし、ジャンル・作品・メディアを登録できます。

## 管理画面（Django Admin）でできること

- **ジャンル管理**: ドラッグ&ドロップで並び替え、公開/非公開の切り替え
- **作品管理**: タイトル・解説・見どころ・制作日・制作時間・使用ツール・タグを入力し、
  画像/動画/音声/外部埋め込みを複数登録（インライン編集）
- **検索・絞り込み**: タイトル・解説・タグ・ツール名で検索、ジャンル/ステータス/タグ/ツール/日付でフィルタ
- **お問い合わせ確認**: フォーム送信内容を一覧・既読管理

## Phase 2 で実装した内容

- 既存の `index.html` / `layout.css` / `parts.css` / `script.js` を Django テンプレート化
  （`templates/base.html`, `templates/index.html`）。デザイン・アニメーション（Vegas / Scrollify / Modaal）はそのまま維持
- `Genre` を `{% for %}` でループ表示するため、**ジャンルを管理画面で増やすだけで**セクションが自動生成される
- 作品ギャラリー・詳細モーダルは `Work` / `WorkMedia` からDB駆動で生成。複数メディア（画像・動画・音声・外部埋め込み・PDF）にも対応済み
- ヒーロースライダーの画像は `HeroSlide` モデルから取得し、`script.js` に `window.HERO_SLIDES` として注入（DB未設定時は従来のデフォルト画像にフォールバック）
- お問い合わせフォームは `ContactForm` 経由で `ContactMessage` に保存し、成功/失敗メッセージを表示

### 既存データの投入（初回のみ）

元の静的サイトにあった22作品・4ジャンル・プロフィール・ヒーロー画像をDBへ投入するコマンドを用意しています。

```bash
python manage.py seed_initial_data
```

- 既にデータが存在する場合は安全のため何もしません（`--force` で再投入も可能）
- 画像ファイルは `backend/static/1-6/img/` から読み込み、`media/` 配下へコピーして `ImageField` に保存します
- 実行後は管理画面から自由に編集・追加・削除できます

## Phase 3 で実装した内容

- **検索・並び替え API**（`/api/works/`）
  - `q` … キーワード検索（タイトル・解説・タグ名）
  - `genre` … ジャンル slug で絞り込み
  - `sort` … `date_desc`（新着順）/ `date_asc`（古い順）/ `title`（タイトル順）/ `featured`（おすすめ順）
  - `page` … ページネーション（24件/ページ）
- **作品詳細 API**（`/api/works/<slug>/`）… 詳細モーダルの遅延読み込み用
- **ギャラリーモーダル内の検索 UI** … キーワード入力・ジャンル絞り込み・並び替えを Ajax で即時反映
- **「もっと見る」ボタン** … 24件超の作品がある場合に追加読み込み

### API 使用例

```bash
# 全作品（新着順）
curl "http://127.0.0.1:8000/api/works/"

# キーワード検索
curl "http://127.0.0.1:8000/api/works/?q=コーヒー"

# ジャンル絞り込み + タイトル順
curl "http://127.0.0.1:8000/api/works/?genre=3dcg&sort=title"

# 作品詳細
curl "http://127.0.0.1:8000/api/works/コーヒー/"
```

## 次のフェーズ（予定）

- Phase 4: 動画・音声・埋め込みメディアのアップロードUI改善、SNSリンクの実URL設定
- Phase 5: 本番デプロイ設定（PostgreSQL本番接続、静的/メディアファイルの配信、HTTPS化）
