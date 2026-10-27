# レビューベースライン(許容済み指摘リスト)
レビュー時、ここに記載された項目は指摘しないこと。

## 形式
- [カテゴリ] 対象範囲 — 許容理由

## 許容項目
- [Blocks] `src/*/index.js` の `registerBlockType( metadata.name, { edit, save } )`（block.json の内容を渡さない書き方） — サーバー側で登録した block.json の属性・supports はエディターに渡されて合わせられる（`@wordpress/create-block` の公式テンプレートと同じ）。テンプレート（pressable-site-template）の PR #1 で実測済み
- [WooCommerce] `woocommerce/product-collection`（`inherit: true`）の中の `core/query-pagination` — WooCommerce 自身のブロックテンプレート（`blockified/archive-product.html`）と同じ構成。`woocommerce/product-pagination` というブロックは存在しない。テンプレート（pressable-site-template）の PR #1 で商品 15 件のページ送りを実測済み
- [Studio] `studio config get/set` の `environment-type` / `--environment-type` — WordPress Studio CLI 1.24.0 の正式なキー・オプション
- [Theme] `templates/search.html` のクエリの `"postType":"post"`（`inherit: true`） — メインクエリを使うので、投稿・固定ページ・商品がすべて検索対象になる

<!--
- [WPCS] (例)Yoda condition 非適用 — チーム規約で不採用
- [DB] (例)$wpdb 直接クエリは Repository クラス内に限り許容 — 抽象化済みのため
-->
