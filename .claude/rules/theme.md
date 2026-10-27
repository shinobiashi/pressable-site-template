---
paths:
  - "wp-content/themes/pressable-theme/**"
---

# Pressable Theme 開発ガイド

テーマ（`wp-content/themes/pressable-theme/`）のファイルを読み書きするときに Claude Code が読み込むガイドです。テーマのフォルダは本番にそのままデプロイされるので、このガイドはテーマの外（`.claude/rules/`）に置いています。

Pressable で構築するサイト用の **WordPress ブロックテーマ（FSE）** です。見た目（デザイントークン・テンプレート・パターン・CSS）だけを担当し、機能は `wp-content/plugins/pressable-plugin` が担当します（役割分担はリポジトリ直下の CLAUDE.md を参照）。

## 環境・前提

- WordPress 6.8+ / PHP 8.1+。WooCommerce は任意（有効なときだけショップ用テンプレートとミニカートが使われる）
- テーマスラッグ / Text Domain: `pressable-theme`
- ビルド工程なし（npm 不要）。独自ブロックはプラグイン側で作る

## ディレクトリ構成

```text
pressable-theme/
├── style.css            # テーマヘッダーのみ（Version がアセットとパターンキャッシュのバージョンの正）
├── theme.json           # デザイントークンの正
├── styles/dark.json     # スタイルバリエーション（ダーク）
├── functions.php        # テーマサポート・CSS 読込・パターンカテゴリ・商品一覧の件数
├── templates/           # front-page / index / page / page-full（全幅・タイトルなし）/ single / search / 404
│                        # archive-product / single-product（WooCommerce）
├── parts/               # header / footer
├── patterns/            # トップ各セクション + 下層ページ雛形（PHP・カテゴリ "pressable-theme"）
└── assets/css/theme.css # theme.json で書けない装飾（カード・お知らせ一覧・商品カード等）
```

- テーマのフォルダは丸ごと本番にデプロイされる。**本番で使わないファイル（説明の Markdown・ソース・設定ファイルなど）をテーマのフォルダに置かない**（Pressable では、`!` で戻したフォルダの中を `.deployignore` で除外できないため）。置いた場合は CI の `bin/check-deployignore.sh` が検出する。

## デザイントークン（theme.json が正・ハードコード禁止）

| slug | 値 | 用途 |
| --- | --- | --- |
| base / surface | #f8f7f4 / #ffffff | ページ背景 / カード背景 |
| contrast / body | #1d2327 / #50575e | 見出し・本文 / 補足本文 |
| primary / primary-dark / on-primary | #1f5f99 / #174a78 / #ffffff | ボタン・リンク / ホバー / プライマリ上の文字 |
| accent | #b45309 | 英字キッカー等の差し色（明るい背景で WCAG AA 4.5:1 以上） |
| band / band-contrast / band-muted | #1d2327 系 | 濃色の帯セクション（ヒーロー・CTA・商品一覧の見出し） |
| line / image-bg / footer | #dcdcde / #ececea / #101517 | 罫線・画像下地・フッター |

- サイトごとの配色は **slug を変えずに値だけ** 差し替える（テンプレート・パターン・CSS は slug で参照しているため）。styles/dark.json も同じ slug をすべて定義しておく（足りない slug は CSS 変数が未定義になる）。
- フォントはシステムフォント（ゴシック）。Web フォントを使う場合は `assets/fonts/` に置いて theme.json の `fontFace` で登録する（外部 CDN より推奨）。
- 角丸は `custom.radius`（card / button）。角丸を直書きしない。
- 新しい色が必要な場合は theme.json のパレットに追加してから使う。

## コーディング規約

- **パターン第一**: セクション追加はまずコアブロック＋パターン（patterns/*.php）で。コアで再現できない表示はプラグインに独自ブロックを作る。
- パターンは PHP。画像を同梱する場合は `assets/images/` に置き、`get_theme_file_uri( 'assets/images/…' )` で参照する。データに応じて出し分けるパターン（`news.php` の「カテゴリが無ければ何も出力しない」など）も PHP で書ける。
- パターンカテゴリは `pressable-theme`（functions.php で登録）。テンプレートからだけ読み込むパターンはヘッダーに `Inserter: no` を付ける。
- CSS はまず theme.json、次に assets/css/theme.css。クラス接頭辞はテーマスラッグ＋ハイフン（`pressable-theme-`）。テーマスラッグと揃えておくと、rename-site スキルでスラッグと一緒に置き換わる。
- ブレークポイントは WP 標準に合わせ `max-width: 781px`。タブレット幅の調整が必要な場合は `max-width: 1279px`（WP の `$break-wide` 未満）を使う。
- ヘッダーの検索は、PC 用の検索欄（`pressable-theme-header-search`）とスマホ用の「ボタンのみ」（`pressable-theme-header-search-mobile`）の 2 つの検索ブロックを、theme.css で 781px を境に切り替えている。重複に見えても片方を消さない。
- PHP は WordPress コーディング規約（関数・変数は `pressable_theme_`、定数は `PRESSABLE_THEME_` 接頭辞、エスケープ必須）。リポジトリ直下で `composer lint`。
- テーマのパターン一覧は WordPress が 30 分キャッシュする（style.css の Version が変わらない限り）。パターンを追加・改名したら、ローカル（Studio）はリポジトリのルートで `studio wp eval 'wp_get_theme()->delete_pattern_cache();'` を実行して消す。本番は反映まで最大 30 分かかり、すぐ反映したいときは style.css の Version を上げる。
- エディターで保存済みのテンプレート・テンプレートパーツは DB に入り、テーマファイルより優先される（ファイルの変更が表示に出ない）。その場合はエディターでテンプレートをリセットするか、変更をエディター側でも行う。

## プラグインとの関係

- フッターのコピーライト行はプラグインの `pressable-plugin/copyright` ブロック（年を自動更新）。プラグインが無効だとこの行だけ表示されない。
- テーマからプラグインの PHP 関数を直接呼ばない。

## WooCommerce まわり

- ヘッダーのアカウントアイコンとミニカートは、WooCommerce が有効なときに WooCommerce 自身がナビゲーションの直後へ自動挿入する（Block Hooks）。parts/header.html に `woocommerce/mini-cart` を書くと二重に表示されるので書かない。ショップでないサイトでは何も出ない。
- 商品一覧: `templates/archive-product.html`（product-collection・inherit:true）。taxonomy-product_cat / product_tag は未定義のため archive-product にフォールバックする（意図的）。表示件数は functions.php の `loop_shop_per_page`（3 列 × 4 行 = 12 件）で決まる（inherit:true のためブロックの perPage は効かない）。列数を変えたら件数も合わせる。
- 商品詳細: `templates/single-product.html`（blockified 構成・関連商品 4 件）。
- カート/チェックアウト: 固定ページ内の WooCommerce ブロックをそのまま使用。WooCommerce のテンプレートには左右の余白がないため、theme.css で固定ページと同じ余白を付けている。
- ショップでないサイトでは archive-product.html / single-product.html を削除してよい（残しても使われないだけ）。

## 新しいサイトで最初に置き換える箇所

1. サイト名・テーマ名・テーマスラッグ（Text Domain・接頭辞・CSS クラスを含む）は rename-site スキルで一括変更する（手で置換しない）
2. theme.json のパレット値（色の slug はそのまま）とフォント
3. parts/footer.html の住所・電話、フッターのリンク先
4. patterns/hero.php・features.php・cta.php の文言とリンク先（`/contact/`・`/company/` を前提にしている）
5. screenshot.png（1200×900）を追加する

## 導入時セットアップ（クライアント向けメモ）

1. テーマ有効化 → 外観 > エディターでロゴ・メニューを設定。
2. 投稿カテゴリ「お知らせ」（スラッグ `news`）を作成する（無いとトップのお知らせ欄が出ず、フッターのリンクも 404 になる）。
3. 固定ページ「会社案内」（スラッグ `company`）はパターン「下層ページ雛形（会社案内）」から作成。全幅で作りたいページはテンプレート「全幅（タイトルなし）」を選ぶ。
4. 配色を変える場合は 外観 > エディター > スタイルで「ダーク」を選択可能。
