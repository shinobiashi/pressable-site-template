---
name: rename-site
description: このリポジトリ（Pressable サイトテンプレート）のサイト名・テーマ名とテーマスラッグ・プラグイン名とプラグインスラッグを一括で変更する。テンプレートから新しいサイトのリポジトリを作った直後に「サイト名を〇〇、テーマを〇〇（スラッグ〇〇）、プラグインを〇〇にして」「テーマ名とプラグイン名を案件用に変えて」「pressable-theme / pressable-plugin をリネームして」「テンプレートの名前を一括置換して」などと言われたら必ず使う。ディレクトリ名・Text Domain・PHP の関数/変数/定数の接頭辞・CSS クラス接頭辞・パターンのスラッグ・ブロックの名前空間・.gitignore・.deployignore・PHPCS 設定・CI・Studio 用スクリプトまで、手作業の置換では漏れやすい箇所を同梱スクリプトでまとめて書き換える。名前の一部だけ（テーマだけ・プラグインだけ）を変える場合にも使う。このスキルはテンプレートにだけ置き、テンプレートから作ったリポジトリでは名前を変えた最後に自分自身を削除する。
---

# rename-site

テンプレートの既定のサイト名・テーマ・プラグインの名前を、案件の名前に一括で変更する。置換は `scripts/rename.py` が行う。手で検索置換しないこと。スラッグは Text Domain・PHP の接頭辞・CSS クラス・パターンのスラッグ・ブロック名・パス・CI 設定に形を変えて散らばっていて、手作業だと必ず漏れが出るため。

このスキルの置き場所はテンプレート（pressable-site-template）だけ。GitHub の「Use this template」は全ファイルをコピーするので、新しいリポジトリにも一度は入るが、名前を変えた最後（手順 7）に削除する。残すと案件ごとに古い版が増え、テンプレートで直した内容が届かないため。テンプレート自身（origin が pressable-site-template）では、スクリプトは名前の変更も削除も拒否する。

## 使ってよいタイミング

最適なのは **テンプレートから作ったリポジトリを Studio サイトのフォルダに取り込んだ直後**、つまり初回デプロイ・コンテンツ作成より前。このときローカルのデータベースは本番から pull したものでも構わない（本番ではまだこのテーマ・プラグインを使っていないため）。

公開後やコンテンツを作り込んだ後の変更は勧めない。WordPress は次の情報をスラッグで覚えているため、変更すると壊れる。

- 有効なテーマ（`stylesheet` / `template` オプション）とテーマの設定（`theme_mods_<スラッグ>`）。新しいスラッグのテーマは別テーマ扱いになり、無効化・設定リセットが起きる
- エディターで保存したテンプレート・テンプレートパーツ（テーマスラッグに紐付く）。新しいテーマからは見えなくなる
- 有効なプラグイン（`<スラッグ>/<スラッグ>.php`）。プラグインが無効化される
- 投稿や保存済みテンプレートに書かれたブロック名（`<プラグインスラッグ>/copyright` など）。「未対応のブロック」になる
- 本番の旧ディレクトリは `.deployignore` の許可リストから外れるため、削除されずにサーバーに残る

ユーザーが公開後の変更を求めた場合は、上記の影響と必要な後始末（新テーマ・プラグインの有効化、テンプレートの作り直し、旧ディレクトリの削除）を説明し、了承を得てから進める。

## 入力

| 項目 | 例 | 決まりごと |
| --- | --- | --- |
| サイト名 | サンプル商店 | 日本語可 |
| テーマ名 | Sample Store | 日本語可 |
| テーマスラッグ | sample-store | 英小文字で始まり、英小文字・数字・ハイフンのみ。3〜50 文字。`wp-` で始めない |
| プラグイン名 | Sample Store Functions | 日本語可 |
| プラグインスラッグ | sample-store-functions | テーマスラッグと同じ決まり。テーマスラッグとは別の名前にする |

- 名前に `" \ $` バッククォート `*/` は使えない（PHP のコメント・JSON・シェル変数に書き込むため）。
- スラッグが示されていなければ、名前から英小文字・ハイフンの候補を作ってユーザーに確認する。日本語だけの名前ならスラッグを尋ねる。
- スラッグはそのまま PHP の接頭辞になる（`sample-store` → `sample_store_`・`SAMPLE_STORE_`）。短い一般名詞（`shop` など）は他のプラグインの関数と衝突しやすいので、ハイフンを含む固有の名前を勧める。テーマとプラグインで揃えるなら、テーマ `sample-store`・プラグイン `sample-store-functions` のような組み合わせが分かりやすい。
- 一部だけ変える場合も、変えない項目は現在の値を渡す（現在の値はスクリプトの出力の「変更内容」で確認できる）。

## 手順

1. **作業ツリーを確認する。** `git status` で未コミットの変更があれば、リネームの差分と混ざらないよう先にコミットするか退避するかをユーザーに確認する（コミットは指示があるまでしない）。

2. **dry-run で確認する。** リポジトリのルートで実行する。

   ```bash
   python3 -I .claude/skills/rename-site/scripts/rename.py \
     --site-name "サンプル商店" \
     --theme-name "Sample Store" --theme-slug sample-store \
     --plugin-name "Sample Store Functions" --plugin-slug sample-store-functions \
     --dry-run
   ```

   出力の「変更内容」「書き換えるファイル」「リネーム」を確認する。「警告」「注意」が出たら、その内容をユーザーに伝える。本番で既にこのテーマ・プラグインを使っていそうな場合（README の見出しが既に案件名になっている、など）は、上の「使ってよいタイミング」に照らしてユーザーに確認する。

   リポジトリのフォルダは Studio サイトも兼ねていて、WordPress 本体・uploads・WooCommerce などの他のプラグインも置かれている。スクリプトは Git が管理しているファイル（`git ls-files`）だけを対象にするので、それらには触れない。

3. **適用する。** 同じコマンドを `--dry-run` なしで実行する。最後に古い名前の残り・JSON・PHP 構文を自動でチェックし、問題があれば終了コード 2 で一覧を出す。その場合は内容を確認して直す。

4. **ブロックを再ビルドし、JS の lint を実行する。** build/ の中身はテキスト置換済みで動くが、`index.asset.php` のバージョンハッシュが古いままで、CI の「build/ の更新漏れチェック」で落ちる。再ビルドが必要。また、Text Domain の長さが変わると Prettier の折り返し位置が変わり（`__( '…', '<スラッグ>' )` が 1 行に収まるようになる、など）、CI の `lint:js` で落ちることがある。エラーが出たら `npx wp-scripts lint-js src --fix` で直す（整形だけなので build/ の出力は変わらない）。

   ```bash
   cd wp-content/plugins/<新しいプラグインスラッグ>
   nvm use && npm ci && npm run build && npm run lint:js
   ```

5. **PHPCS を実行する。** リポジトリのルートで `composer install`（未実施なら）→ `composer lint`。接頭辞が変わっても WPCS の設定（`.phpcs.xml.dist`）は一緒に書き換わっているので、エラーが出たら置換漏れを疑う。

6. **ローカルサイトで有効化する（リポジトリが Studio サイトのフォルダの場合）。** `bin/studio-prepare.sh` を実行すると、新しいスラッグのテーマ・プラグインを有効化する（ローカルのデータベースは旧スラッグを覚えているため）。Studio のサイト名やサイトタイトルも変えたい場合は、`studio config set --name "<サイト名>"` と `studio wp option update blogname "<サイト名>"` をリポジトリのルートで実行する。

7. **このスキルを削除する。** リポジトリのルートで dry-run → 実行の順に行う。

   ```bash
   python3 -I .claude/skills/rename-site/scripts/rename.py --remove-skill --dry-run
   python3 -I .claude/skills/rename-site/scripts/rename.py --remove-skill
   ```

   次のものを消す。名前を変える前・テンプレート自身・マーカーの対応が取れていないときは、何も変えずに終了コード 1 で止まる。

   - スキルのディレクトリと、テンプレート自身のレビュー記録 `docs/reviews/`（どちらもディレクトリごと `git rm`。リネームの置換で未コミットの変更があっても消すので、その旨を「注意」で出す）
   - 各ファイルで `rename-site:start` / `rename-site:end` のコメントに囲まれたテンプレート用の記述（`.gitignore` の許可行、CI の `rename-skill` ジョブ、README.md・CLAUDE.md のスキルの説明）
   - `docs/review-backlog.md` の中身（テンプレートで後回しにした指摘）。表の見出しと区切り行だけを残し、案件のレビューがそのまま追記できるようにする

   `docs/review-baseline.md`（レビューで許容した書き方）は残す。案件も同じコードを受け継ぐので、案件のレビューでもそのまま有効なため。

8. **報告する。** 変更した名前・識別子の対応、リネームしたパス、実行したチェックの結果、スキルを削除したことを伝える。コミットはユーザーの指示を待つ。リネームとスキルの削除は同じコミットにしてよい。

## スキルを削除した後に名前を変えるとき

公開後は変えない前提（上の「使ってよいタイミング」）。どうしても必要なときは、手元のテンプレートを `git pull` で最新にし、そのスクリプトを `--repo` でサイトのリポジトリを指定して実行する。手順はこのファイルと同じ（手順 7 の削除は不要。スクリプトも案内しない）。

```bash
cd ~/Studio/<サイトのフォルダ>
python3 -I ~/Dev/pressable-site-template/.claude/skills/rename-site/scripts/rename.py --repo . \
  --site-name "サンプル商店" \
  --theme-name "Sample Store" --theme-slug sample-store \
  --plugin-name "Sample Store Functions" --plugin-slug sample-store-functions \
  --dry-run
```

`--repo` を付けないと、既定の対象はスクリプトの置き場所のリポジトリ（テンプレート）になり、テンプレート自身なので拒否される。

## スクリプトが変更するもの

- テーマ・プラグインのディレクトリ名と、プラグインのメインファイル名（git で管理されていれば `git mv`）
- スラッグ（`sample-store`）・PHP 接頭辞（`sample_store`）・定数接頭辞（`SAMPLE_STORE`）が現れる、Git 管理下のすべてのテキストファイル。Text Domain、`@package`、パターンのスラッグとカテゴリ、CSS クラス（`<テーマスラッグ>-card` など）、ブロック名、`.gitignore`・`.deployignore` の許可リスト、`.phpcs.xml.dist`、CI のパス、`bin/studio-*.sh`、各 CLAUDE.md・README.md、build/、package.json / package-lock.json が該当する
- 名前が書かれた決まった行: `Theme Name`・`Plugin Name`・各説明文のサイト名・functions.php と theme.css の先頭・各 CLAUDE.md の見出し・package.json の description・README.md の見出しと冒頭
- `--remove-skill` のとき: `.claude/skills/rename-site/` と `docs/reviews/`（中が空になった親ディレクトリも消す）、Git 管理下のファイルの `rename-site:start` / `rename-site:end` で囲んだ範囲、`docs/review-backlog.md` の表の中身（見出しと区切り行は残す）。対象は `rename.py` の `TEMPLATE_ONLY_DIRS` と `TABLE_HEADER_ONLY`

## 変更しないもの

- `composer.json` の `name`（変えると composer.lock のハッシュがずれるため）と `.phpcs.xml.dist` の ruleset 名
- README.md の「新しいサイトを始める」にあるテンプレートリポジトリ名
- パターンの文言やフッターの住所など、案件ごとに手で書き換えるプレースホルダー（テーマの CLAUDE.md の「新しいサイトで最初に置き換える箇所」を参照）
- Git が管理していないファイル（同じフォルダにある WordPress 本体・uploads・他のプラグインやテーマ・Studio のファイル）と、データベース・本番サーバー

## スクリプトを変更するとき

`scripts/test_rename.py` に、全体のリネーム・一部だけのリネーム（変えないスラッグが変えるスラッグを含む場合）・新スラッグが旧スラッグを含む場合・ハイフンの無い一般語のスラッグ・不正な入力・変更なし・テンプレート自身での拒否・スキルの削除（削除後のファイルと docs/・名前を変える前の拒否・対応の取れないマーカー）・削除後にテンプレートのスクリプトを `--repo` で使うリネーム、のシナリオテストがある。`rename.py` を変更したら実行する（テンプレートの CI でも実行される）。

スキルのディレクトリは置換の対象外で、リネームしてからスキルを削除するまでの間は、サイトのリポジトリの CI でもテストが走る。テストにテンプレートの既定の名前（`pressable-theme` / `pressable-plugin`）を直書きせず、現在のテーマ・プラグインのディレクトリを探して使う。

テンプレートにだけ必要な記述（スキルの説明・テストのコマンド・CI のジョブなど）をテンプレートに足すときは、`<!-- rename-site:start -->` と `<!-- rename-site:end -->`（YAML・.gitignore では `# rename-site:start` と `# rename-site:end`）で囲む。マーカーは単独の行に置くか（その行から終わりの行まで、直後の空行も含めて消える）、1 行の中で文を囲む（その部分だけ消える）。囲みを入れ子にせず、囲みの中にマーカーの文字列そのものを書かない。

テンプレート自身ではスクリプトが動かないので、手で試すときはテンプレートを一時ディレクトリにコピーし、そこで `git init` してから実行する（`test_rename.py` の `setUp` と同じやり方）。

```bash
python3 -I .claude/skills/rename-site/scripts/test_rename.py
```

## うまくいかないとき

- **「テーマが複数あります」「プラグインが複数あります」** — リポジトリに別のテーマやプラグインをコミットしている。変更元を `--from-theme-slug` / `--from-plugin-slug` で指定する。
- **「該当する行が見つからないため変更しません」** — その行が手で書き換えられている。スラッグなどの置換は行われているので、表示された箇所だけ手で直す。
- **「古い名前が残っています」** — スクリプトが知らない形で名前が書かれている。表示されたファイルを開いて直す。
- **「テンプレート（pressable-site-template）自身なので、名前を変えません」** — テンプレートのリポジトリで実行している。テンプレートから作ったリポジトリで実行するか、`--repo` で対象を指定する。
- **「まだ名前を変えていません」**（`--remove-skill`） — README.md の見出しがテンプレートのまま。先に名前を変える。
- **「rename-site:start と rename-site:end の対応が取れていません」** — 表示されたファイルのマーカーが欠けているか、入れ子になっている。手で直してからもう一度実行する（何も変更されていない）。
