<?php
/**
 * Plugin Name: Local Mail Guard
 * Description: ローカル環境（環境タイプが local）でだけメール送信を止め、宛先と件名を debug.log に記録する。
 *
 * 本番のデータベースを pull したローカルサイトには、本物の顧客のメールアドレスや SMTP の設定が入っている。
 * ローカルでの動作確認や WP-Cron の実行で、顧客に本物のメールが送られないようにするためのもの。
 * リポジトリで管理しているが、.deployignore により本番にはデプロイされない（万一置かれても local 以外では何もしない）。
 *
 * @package local-mail-guard
 */

defined( 'ABSPATH' ) || exit;

if ( 'local' === wp_get_environment_type() ) {
	/*
	 * wp_mail() そのものを置き換える。mu-plugin は通常のプラグインより先に読み込まれるので、
	 * wp_mail() を自前で定義する SMTP / API 系のプラグイン（function_exists() で確認してから定義する）より優先される。
	 * bin/studio-prepare.sh が、実際に使われている wp_mail() がこのファイルのものかを確認する。
	 */
	if ( ! function_exists( 'wp_mail' ) ) {
		/**
		 * Records the mail in debug.log instead of sending it.
		 *
		 * @param string|string[] $to          Recipients.
		 * @param string          $subject     Subject.
		 * @param string          $message     Message body (not used).
		 * @param string|string[] $headers     Headers (not used).
		 * @param string|string[] $attachments Attachments (not used).
		 * @return bool Always true, so callers do not show an error.
		 */
		function wp_mail( $to, $subject, $message, $headers = '', $attachments = array() ) { // phpcs:ignore WordPress.NamingConventions.PrefixAllGlobals.NonPrefixedFunctionFound, Generic.CodeAnalysis.UnusedFunctionParameter.FoundAfterLastUsed -- Overrides the pluggable wp_mail() with its exact signature.
			$recipients = is_array( $to ) ? implode( ', ', $to ) : (string) $to;
			// phpcs:ignore WordPress.PHP.DevelopmentFunctions.error_log_error_log -- Records the blocked mail for local debugging.
			error_log( sprintf( '[local-mail-guard] Blocked mail to %s: %s', $recipients, $subject ) );

			return true;
		}
	}

	/*
	 * 別の mu-plugin が先に wp_mail() を定義していた場合の保険。
	 * WordPress 本体の wp_mail() が使われるときだけ効く。
	 */
	add_filter(
		'pre_wp_mail',
		static function ( $short_circuit, $atts ) {
			$recipients = is_array( $atts['to'] ) ? implode( ', ', $atts['to'] ) : (string) $atts['to'];
			// phpcs:ignore WordPress.PHP.DevelopmentFunctions.error_log_error_log -- Records the blocked mail for local debugging.
			error_log( sprintf( '[local-mail-guard] Blocked mail to %s: %s', $recipients, $atts['subject'] ) );

			return true;
		},
		10,
		2
	);
}
