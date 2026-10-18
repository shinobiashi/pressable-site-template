#!/usr/bin/env bash
#
# Studio に接続した Pressable（または WordPress.com）のサイトから、データベースと uploads だけを
# このリポジトリ（= Studio のサイトのフォルダ）に pull し、ローカル用の設定に戻す。
#
# テーマ・プラグインのコードは Git で管理しているので pull しない。pull に含めると、
# 未コミットの作業が本番の版で上書きされるため。

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# 案件ごとに pull 元（本番かステージング）の URL を設定しておく。空のままだと、Studio が
# WordPress.com アカウントの全サイトの一覧から選ばせるため、別のサイトを選び間違えやすい。
PULL_FROM=""
REMOTE_SITE="$PULL_FROM"

usage() {
	cat <<EOF
Usage: bin/studio-pull.sh [--remote-site <URL か ID>]

Options:
  --remote-site <site>  pull 元のサイト（既定: スクリプト内の PULL_FROM = ${PULL_FROM:-未設定}）
  -h, --help            このヘルプを表示する

ローカルのデータベースと uploads は、pull 元の内容で上書きされます。
EOF
}

while [ $# -gt 0 ]; do
	case "$1" in
		--remote-site)
			REMOTE_SITE="$2"
			shift 2
			;;
		-h | --help)
			usage
			exit 0
			;;
		*)
			echo "Unknown option: $1" >&2
			usage >&2
			exit 1
			;;
	esac
done

if ! command -v studio >/dev/null 2>&1; then
	echo "studio コマンドが見つかりません。Studio アプリの 設定 > 一般 >「ターミナル用 Studio CLI」を有効にし、新しいターミナルで実行してください。" >&2
	exit 1
fi
if [ ! -f "$REPO_DIR/wp-config.php" ]; then
	echo "$REPO_DIR は Studio サイトのフォルダではありません（wp-config.php がありません）。" >&2
	exit 1
fi

# 万一 pull が Git 管理下のファイルに触れても戻せるよう、作業ツリーがきれいなときだけ実行する。
tracked_changes() {
	git -C "$REPO_DIR" status --porcelain --untracked-files=no
}
if [ -n "$(tracked_changes)" ]; then
	echo "Git 管理下のファイルに未コミットの変更があります。コミットするか git stash で退避してから実行してください。" >&2
	git -C "$REPO_DIR" status --short --untracked-files=no >&2
	exit 1
fi

pull_args=(--path "$REPO_DIR" --options "sqls,uploads")
if [ -n "$REMOTE_SITE" ]; then
	pull_args+=(--remote-site "$REMOTE_SITE")
elif [ ! -t 0 ]; then
	# 対話できない環境（Claude Code などからの実行）では、Studio のサイト選択で止まってしまう。
	echo "pull 元が決まっていません。--remote-site を付けるか、スクリプト内の PULL_FROM に本番（またはステージング）の URL を設定してください。" >&2
	exit 1
else
	echo "注意: pull 元が未設定のため、Studio がサイトの一覧から選ばせます。案件のサイトを選んでください（毎回選ばずに済むよう PULL_FROM の設定をおすすめします）。"
fi

echo "==> データベースと uploads を pull します（ローカルのデータベースと uploads は上書きされます）"
studio pull "${pull_args[@]}"

if [ -n "$(tracked_changes)" ]; then
	echo "警告: pull で Git 管理下のファイルが変わりました。内容を確認し、不要なら git restore . で戻してください。" >&2
	git -C "$REPO_DIR" status --short --untracked-files=no >&2
fi

"$REPO_DIR/bin/studio-prepare.sh"
