---
paths:
  - "wp-content/plugins/pressable-plugin/**"
  - "blocks/**"
---

# Pressable Plugin 開発ガイド

プラグイン（`wp-content/plugins/pressable-plugin/`）と、その独自ブロックのソース（`blocks/`）を読み書きするときに Claude Code が読み込むガイドです。プラグインのフォルダは本番にそのままデプロイされるので、このガイドとブロックのビルド環境はプラグインの外に置いています。

サイト固有の **機能** をまとめたプラグインです。見た目は `wp-content/themes/pressable-theme` が担当します（役割分担はリポジトリ直下の CLAUDE.md を参照）。

## 環境・前提

- WordPress 6.8+（`wp_register_block_types_from_metadata_collection()` を使うため）/ PHP 8.1+
- プラグインスラッグ / Text Domain: `pressable-plugin`
- ブロック名の名前空間: `pressable-plugin/`
- 独自ブロックのビルド: `@wordpress/scripts`。ビルド環境はリポジトリ直下の `blocks/`（`package.json`・`.nvmrc`・`src/`）。ビルドの出力先はプラグインの `build/`

```bash
cd blocks
nvm use
npm ci
npm run build    # blocks/src/ → プラグインの build/（--webpack-copy-php で render.php も、--blocks-manifest で blocks-manifest.php も生成）
npm run start    # 開発ウォッチ
npm run lint:js  # ESLint
npm run format   # Prettier
```

`build/` は **コミット対象**。Pressable はデプロイ時にビルドしないため、`blocks/src/` を変更したら必ず `npm run build` して build/ も一緒にコミットする（CI が build/ の更新漏れを検出する）。

プラグインのフォルダは丸ごと本番にデプロイされる。**本番で使わないファイル（説明の Markdown・ソース・`package.json` などの設定ファイル）をプラグインのフォルダに置かない**（Pressable では、`!` で戻したフォルダの中を `.deployignore` で除外できないため）。置いた場合は CI の `bin/check-deployignore.sh` が検出する。

## ディレクトリ構成

```text
pressable-plugin/
├── pressable-plugin.php   # プラグインヘッダー・定数・includes の読み込み
├── includes/
│   ├── blocks.php         # build/ の独自ブロックを一括登録
│   └── woocommerce.php    # WooCommerce 関連（HPOS・カート/チェックアウトブロックの互換宣言など）
└── build/                 # ビルド成果物（コミット対象。blocks/ の npm run build で作る）

blocks/                    # リポジトリ直下。デプロイしない
├── src/<ブロック名>/      # 独自ブロックのソース（block.json / index.js / edit.js / render.php）
└── package.json / package-lock.json / .nvmrc
```

## 独自ブロック

- `blocks/src/<ブロック名>/block.json` を置けば `npm run build` が自動で拾い、`build/blocks-manifest.php` に載る。PHP 側の登録コードを足す必要はない。
- 表示はサーバーサイドレンダリング（`render.php`・`save: () => null`）を基本にする。エディターのプレビューは edit.js でクライアント側に組み立て、`render.php` と表示を揃える（`ServerSideRender` は非推奨の仕組みなので新規には使わない）。日付はブラウザーではなくサイトのタイムゾーンで求め（PHP の `wp_date()` ⇔ JS の `@wordpress/date` の `date()`）、入力値の正規化も `render.php` と同じにする（例: `absint()` ⇔ `Math.abs( Math.trunc() )`）。
- `render.php` のローカル変数も WPCS の接頭辞ルールの対象になるので `$pressable_plugin_` を付ける。
- `@wordpress/*` パッケージは実行時には WordPress 本体のスクリプトを使う（ビルドで外部化される）。import するパッケージは ESLint のために devDependencies に追加する。
- 既存ブロック: `pressable-plugin/copyright`（「© 開始年–今年 権利者名」。テーマのフッターで使用）。

## 機能を追加するとき

- 機能ごとに `includes/<機能名>.php` を作り、`pressable-plugin.php` から `require_once` する。
- 関数・変数は `pressable_plugin_`、定数は `PRESSABLE_PLUGIN_` 接頭辞。出力はエスケープ、入力はサニタイズ、フォーム・Ajax・REST は nonce と権限を確認する。
- WooCommerce のフックへの登録は `includes/woocommerce.php` に書く（WooCommerce が無効なら呼ばれない）。WordPress 本体のフックから WooCommerce の関数を呼ぶ場合だけ `function_exists()` で確認する。
- 注文データを直接 SQL で扱う場合は HPOS（`wc_orders`）と投稿テーブルの両方に対応させる（`OrderUtil::custom_orders_table_usage_is_enabled()` で分岐）。
- 画面の文言は日本語で直接書き、テキストドメイン `pressable-plugin` を付ける。

## バージョン

- `pressable-plugin.php` のヘッダー `Version` と定数 `PRESSABLE_PLUGIN_VERSION` を同時に上げる。
