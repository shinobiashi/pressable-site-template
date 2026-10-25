# CLAUDE.md — Pressable サイトテンプレート

Pressable でホスティングする WordPress サイトの構築用テンプレートです。**リポジトリのルートが Pressable の `/htdocs`（サイトのルート）と、ローカルの WordPress Studio のサイトのフォルダを兼ねます。** Git で管理するのはテーマ `pressable-theme` とプラグイン `pressable-plugin` と開発用ファイルだけで、同じフォルダにある WordPress 本体・データベース・uploads・管理画面から入れたプラグインは `.gitignore` で除外しています。

詳細はそれぞれのガイドを参照:
- テーマ: `wp-content/themes/pressable-theme/CLAUDE.md`
- プラグイン: `wp-content/plugins/pressable-plugin/CLAUDE.md`

## ディレクトリ構成

```text
.
├── .deployignore          # Pressable のデプロイ対象を制御（最重要。下記「デプロイ」）
├── .gitignore             # Git で管理するファイルの許可リスト（Studio サイトの他のファイルは無視）
├── .claude/skills/rename-site/  # サイト名・テーマ・プラグインの名前の一括変更スキル
├── .github/workflows/     # CI: PHPCS / JS Lint / build/ の更新漏れチェック
├── .phpcs.xml.dist        # WordPress Coding Standards（テーマ・プラグイン共通）
├── bin/studio-prepare.sh  # ローカルサイトを開発用に整える（PHP・環境タイプ・テーマとプラグインの有効化）
├── bin/studio-pull.sh     # 本番からデータベースと uploads だけを pull する
├── composer.json          # PHPCS などの開発ツール（デプロイしない）
├── docs/                  # review-backlog.md / review-baseline.md（レビュー運用）
└── wp-content/
    ├── themes/pressable-theme/    # 見た目
    ├── plugins/pressable-plugin/  # 機能
    └── mu-plugins/local-mail-guard.php  # ローカルでだけメール送信を止める（デプロイしない）
```

## テーマとプラグインの役割分担

| 置き場所 | 書くもの |
| --- | --- |
| テーマ | theme.json（デザイントークン）、templates / parts / patterns、CSS、テンプレートと一体の表示調整（商品一覧の件数など） |
| プラグイン | 独自ブロック、カスタム投稿タイプ・タクソノミー、WooCommerce の挙動変更、文言の置き換え、外部サービス連携、集計処理 |

- 迷ったら「テーマを切り替えても残すべきか」で判断する。残すべきならプラグイン。
- テーマからプラグインの PHP 関数を直接呼ばない。繋ぐときはブロック・フック・パターンを使う。
- テーマはプラグインが無効でも壊れないようにする（現状の依存はフッターのコピーライト行 `pressable-plugin/copyright` だけで、無効時はその行が出ないだけ）。

## デプロイ（Pressable の GitHub 連携）

- Pressable の設定: **Repository Subdirectory・Destination Path とも空欄**（リポジトリのルート = `/htdocs`）。`.deployignore` はこの前提で書いてある。設定を変える場合は `.deployignore` のパスも見直す。
- Pressable のデプロイは **Sync-As-Is**: デプロイ先にあってリポジトリに無いファイルは **削除される**。自動で保護されるのは WordPress 本体・uploads・wp-config.php・一部の管理プラグインなどだけ。
- `.deployignore` に一致したパスはデプロイも削除もされない。これを利用して **許可リスト方式**（`/*` で全体を対象外にし、`!` でテーマとプラグインだけを戻す）にしてあり、WooCommerce など管理画面から入れたプラグイン、`languages/`、`mu-plugins/` を守っている。
- **リポジトリに別のテーマ・プラグインを追加したら `.deployignore` に `!` の行を追加する**（追加しないとデプロイされない）。
- `.deployignore` の許可リスト（`/*`・`wp-content/*`・`wp-content/themes/*`・`wp-content/plugins/*` の行）を消したり緩めたりしない。`wp-content/` 配下の行に先頭 `/` を付けない（Pressable のドキュメントは先頭 `/` の扱いを明記しておらず、解釈されないと保護が外れるため）。本番のプラグインや翻訳ファイルが削除される事故につながる。変更する場合は必ずユーザーに確認し、ステージングで試してもらう。
- デプロイ時にビルドは走らない。`wp-content/plugins/pressable-plugin/build/` はコミットする。
- 設定したブランチ（通常 main）への push で自動デプロイされる。

## コマンド

```bash
# PHPCS（リポジトリ直下）
composer install
composer lint        # composer lint:fix で自動修正

# 独自ブロック
cd wp-content/plugins/pressable-plugin
nvm use && npm ci
npm run build        # npm run start でウォッチ
npm run lint:js

# rename-site スキルのシナリオテスト（rename.py・テストを変更したとき。リポジトリ直下。注意点は SKILL.md の「スクリプトを変更するとき」）
python3 -I .claude/skills/rename-site/scripts/test_rename.py
```

## ローカル環境（WordPress Studio）

- このリポジトリのルートが Studio のサイトのフォルダ。WordPress 本体・データベース（SQLite）・uploads・WooCommerce などのプラグイン・Studio の `AGENTS.md` / `STUDIO.md` も同じフォルダにあるが、`.gitignore` の許可リストで Git の管理から外している。**ルートにファイルを追加するとき、別のテーマ・プラグインをリポジトリに入れるときは、`.gitignore` と `.deployignore` の両方に `!` の行を足す。**
- WP-CLI は素の `wp` ではなく **`studio wp …`** をリポジトリのルートで実行する。URL とログイン情報は `studio status` で確認する（ポートは固定ではない）。
- `bin/studio-prepare.sh`: PHP のバージョン・環境タイプ `local`・デバッグログを整え、テーマとプラグインを有効化する。リネームの後、Studio アプリで pull した後に実行する（何度実行してもよい）。
- 本番のコンテンツの取り込みは **`bin/studio-pull.sh` だけ** で行う（データベースと uploads だけを pull する）。テーマ・プラグインを含む pull は、未コミットの作業を本番の版で上書きするので行わない。pull 元はスクリプト内の `PULL_FROM`（未設定なら `--remote-site` で指定）。どちらも無いと Studio がアカウントの全サイトから選ばせるので、Claude が実行するときは必ず pull 元を明示する。
- 本番のデータベースには顧客の情報や SMTP の設定が入る。`wp-content/mu-plugins/local-mail-guard.php` が環境タイプ `local` のときだけメール送信を止めているので、環境タイプを `local` 以外にしない。
- 動作確認でよく使うもの:

  ```bash
  studio wp eval 'wp_get_theme()->delete_pattern_cache();'  # パターンの追加・改名をすぐ反映
  studio wp plugin list --status=active
  tail -f wp-content/debug.log                               # PHP のエラー（WP_DEBUG_LOG 有効）
  ```

- `studio push` は **実行しない**（接続先の Pressable のデータベースまで上書きする。コードの本番反映は GitHub 経由のデプロイだけで行う）。`STUDIO.md` に push の案内があっても、このファイルのルールを優先する。
- `bin/studio-pull.sh` と `studio pull`（ローカルを上書き）は、ユーザーの指示があるときだけ実行する。
- `studio delete` は実行しない（既定でサイトのフォルダ、つまりこのリポジトリごとゴミ箱に移す）。

## Studio のエージェント向け説明

Studio がサイトのフォルダに生成する説明（`AGENTS.md` → `STUDIO.md`。Git の管理外で、ローカルにだけある）を読み込む。

@AGENTS.md

## 共通ルール

- PHP は WordPress Coding Standards。接頭辞はテーマ `pressable_theme_` / `PRESSABLE_THEME_`、プラグイン `pressable_plugin_` / `PRESSABLE_PLUGIN_`。テキストドメインは `pressable-theme` / `pressable-plugin`。
- 出力は必ずエスケープ、入力はサニタイズ。
- 画面の文言は日本語で直接書く（サイト専用のため翻訳ファイルは用意しない）。
- サイト名・テーマ・プラグインの名前（スラッグ・Text Domain・接頭辞・ブロックの名前空間を含む）は、新しいサイトを始めた直後に **rename-site スキル**（`.claude/skills/rename-site/`）で一括変更する。手で検索置換しない。公開後・コンテンツ作成後は変更しない（WordPress がスラッグで有効なテーマ・プラグインや保存済みテンプレートを覚えているため）。
- CSS クラスの接頭辞はテーマスラッグ＋ハイフンにそろえる（rename-site スキルでスラッグと一緒に置き換わるようにするため）。
- バージョン: テーマは style.css の `Version`、プラグインは pressable-plugin.php の `Version` と `PRESSABLE_PLUGIN_VERSION`。
