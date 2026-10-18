#!/usr/bin/env bash
#
# このリポジトリ（= WordPress Studio のサイトのフォルダ）をローカル開発用に整える。
# リポジトリを取り込んだ直後・リネームの後・Studio アプリで pull した後に実行する
# （bin/studio-pull.sh は最後にこのスクリプトを自動で実行する）。何度実行してもよい。

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
THEME_SLUG="pressable-theme"
PLUGIN_SLUG="pressable-plugin"
# 本番（Pressable）の PHP バージョンに合わせる。pull で Studio の設定が変わることがあるため毎回戻す。
PHP_VERSION="8.3"

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
	echo "Usage: bin/studio-prepare.sh"
	echo "PHP ${PHP_VERSION}・環境タイプ local・デバッグログを設定し、${THEME_SLUG} と ${PLUGIN_SLUG} を有効化する。"
	exit 0
fi

if ! command -v studio >/dev/null 2>&1; then
	echo "studio コマンドが見つかりません。Studio アプリの 設定 > 一般 >「ターミナル用 Studio CLI」を有効にし、新しいターミナルで実行してください。" >&2
	exit 1
fi
if [ ! -f "$REPO_DIR/wp-config.php" ]; then
	echo "$REPO_DIR は Studio サイトのフォルダではありません（wp-config.php がありません）。README の「新しいサイトを始める」の手順でリポジトリを Studio サイトに取り込んでください。" >&2
	exit 1
fi

studio_wp() {
	studio wp --path "$REPO_DIR" "$@"
}

# config set は変更が無いと失敗扱いで終わるため、値が違うときだけ実行する。
set_config() {
	local key="$1"
	local value="$2"
	shift 2

	if [ "$(studio config get --path "$REPO_DIR" "$key")" != "$value" ]; then
		studio config set --path "$REPO_DIR" "$@"
	fi
}

echo "==> Studio の設定を整えます（PHP ${PHP_VERSION}・環境タイプ local・デバッグログ）"
set_config php "$PHP_VERSION" --php "$PHP_VERSION"
# local-mail-guard（メール送信の停止）は環境タイプが local のときだけ働く。
set_config environment-type local --environment-type local
set_config debug-log true --debug-log
studio start --path "$REPO_DIR" --skip-browser --skip-log-details

echo "==> テーマとプラグインを有効化します"
studio_wp theme activate "$THEME_SLUG"
studio_wp plugin activate "$PLUGIN_SLUG"
studio_wp rewrite flush

# 使われている wp_mail() がどのファイルで定義されているかを見る（フィルターが登録されているかだけでは、
# wp_mail() を自前で定義するプラグインがあると送信を止められないため）。
mail_function_file="$(studio_wp eval 'echo ( new ReflectionFunction( "wp_mail" ) )->getFileName();')"
if [[ "$mail_function_file" != *"/wp-content/mu-plugins/local-mail-guard.php"* ]]; then
	echo "警告: local-mail-guard がメール送信を止められていません。このサイトからメールが送信される可能性があります。" >&2
	echo "      使われている wp_mail(): ${mail_function_file:-（取得できませんでした）}" >&2
	echo "      wp-content/mu-plugins/local-mail-guard.php があるか、環境タイプが local かを確認してください。" >&2
fi

echo
echo "==> 完了しました（URL とログイン情報）"
studio status --path "$REPO_DIR"
