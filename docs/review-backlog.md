# レビューバックログ(今回対応しない指摘)
| 追記日 | ID | 重大度 | 場所 | 内容 | 起票状況 |
|---|---|---|---|---|---|
| 2026-10-18 | initial R1-L2 | Low | wp-content/plugins/pressable-plugin/src/copyright/edit.js:19-23 | エディターのプレビューで、サイト名のエンティティ（`A&B` が `A&amp;B`）がデコードされない。`@wordpress/html-entities` の `decodeEntities()` を通すとよい（フロントは正しい） | 未起票 |
| 2026-10-18 | initial R1-L3 | Low | bin/studio-pull.sh:31-33 | 値の無い `--remote-site` で `$2: unbound variable` になる。安全側で止まるが、引数の数を確かめて usage を出すとよい | 未起票 |
| 2026-10-18 | initial R1-L4 | Low | wp-content/themes/pressable-theme/style.css:8 ほか | PHP の要件の記載が食い違う（ヘッダーは `Requires PHP: 8.3`、`.phpcs.xml.dist` の testVersion と各 CLAUDE.md は 8.1+）。どれかに揃える | 未起票 |
| 2026-10-18 | initial R1-L5 | Low | wp-content/themes/pressable-theme/assets/css/theme.css:7,100,165 | 影の色 `rgba(29, 35, 39, 0.08)` と `border-radius: 20px` の直書き。theme.json の `custom` に shadow・pill の radius を足して参照するとよい（ダークでも影が変わらない） | 未起票 |
| 2026-10-18 | initial R1-L6 | Low | wp-content/themes/pressable-theme/templates/single-product.html:22 | `woocommerce/product-meta` は typography をサポートしないため `fontSize` が効かない。内側の group に付ける | 未起票 |
| 2026-10-18 | initial R1-L7 | Low | wp-content/themes/pressable-theme/parts/footer.html:14 | お知らせのリンクが `/category/news/` の固定 URL。カテゴリーのベースを変えるとフッターだけ 404 になる。前提としてテーマの CLAUDE.md に明記するか、ナビゲーションブロックにする | 未起票 |
| 2026-10-18 | initial R1-L8 | Low | bin/studio-pull.sh | Git の作業ツリーでないフォルダで実行すると、未コミットの変更の確認が黙って通る。`git rev-parse --is-inside-work-tree` で先に確かめるとよい | 未起票 |
| 2026-10-18 | initial R1-L9 | Low（要判断） | includes/blocks.php:3 ほか | グローバルルール「コードは英語」に対し、コメントと docblock が日本語（okatora-shop と同じ書き方）。コメントがルールの対象かをユーザーが判断する | 未起票 |
| 2026-10-18 | initial R2-2 | Low | bin/studio-prepare.sh:59 | `mail_function_file="$(studio_wp eval …)"` は `set -e` の下で、eval が失敗するとその場で終了し、警告も `studio status` も出ない。`\|\| mail_function_file=""` を付けると警告まで進む | 未起票 |
| 2026-10-18 | initial R2-3 | Low | .claude/skills/rename-site/scripts/rename.py（TOKEN_START） | 直前が `-` のときは置換しないため、`wp-block-<プラグインスラッグ>-copyright` のような生成されるクラス名をファイルに書くと置き換わらず、残りチェックにも出ない（今は該当なし）。SKILL.md に制約として書く | 未起票 |
| 2026-10-18 | initial R2-4 | Low（要判断） | .claude/skills/rename-site/scripts/rename.py | 旧スラッグがハイフンの無い一般語（`store` など）だと、後ろ側の境界が無いため一般の単語まで置き換わる（`edit.js` の `import { store as coreStore }` など）。スラッグにハイフンを必須にすれば、この種の問題をまとめて防げる | 未起票 |
