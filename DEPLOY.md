# デプロイについて（重要）

## 結論

| 環境 | Django版を動かせるか | 状態 |
|---|---|---|
| **GitHub Pages** | ❌ **不可** | 静的HTMLのみ。Python/DBは実行できない |
| **Vercel** | ❌ **現構成では不可** | Serverless向きではなく500エラー（後述） |

---

## GitHub Pages について

GitHub Pages は **静的ファイル（HTML/CSS/JS/画像）しか配信できません**。

- ✅ 可能: 旧来の静的ポートフォリオ（`index.html` + `1-6/` フォルダ）
- ❌ 不可能: Django、PostgreSQL、検索API、管理画面、お問い合わせDB保存

**現在**: ルートの `index.html`（静的版）が GitHub Pages で表示されます。  
URL: https://amano02.github.io/this-is-me/

---

## Vercel について

Django + データベース + 大量の画像メディアという構成は **Vercel の Serverless Python 向きではありません**。

試みた結果、以下の制約で安定稼働できませんでした:

- Lambda サイズ上限（225MB）と画像アセットの兼ね合い
- 読み取り専用ファイルシステム（SQLite書き込み・メディアアップロード不可）
- Django WSGI の非公式サポート
- ビルド時の PostgreSQL 接続が必須

**→ Vercel ではこの Django アプリを本番運用することは現実的ではありません。**

---

## 推奨する代替（Django 版を公開したい場合）

| サービス | 適合度 | 無料枠 |
|---|---|---|
| **[Render](https://render.com)** | ◎ Django + PostgreSQL 向き | あり |
| **[Railway](https://railway.app)** | ◎ 同上 | あり（制限付き） |
| **[Fly.io](https://fly.io)** | ○ Docker で Django 可 | あり |

Render なら `backend/` を Web Service としてデプロイし、PostgreSQL アドオンを追加するだけで Phase 1〜3 の機能がそのまま動きます。

---

## ローカルでの利用

```bash
cd backend
source venv/bin/activate
# PostgreSQL 起動後
python manage.py runserver
# → http://127.0.0.1:8000/
```

管理画面: http://127.0.0.1:8000/admin/
