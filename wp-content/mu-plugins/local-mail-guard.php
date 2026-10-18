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
	add_filter(
		'pre_wp_mail',
		static function ( $short_circuit, $atts ) {
			$to = is_array( $atts['to'] ) ? implode( ', ', $atts['to'] ) : (string) $atts['to'];
			// phpcs:ignore WordPress.PHP.DevelopmentFunctions.error_log_error_log -- Records the blocked mail for local debugging.
			error_log( sprintf( '[local-mail-guard] Blocked mail to %s: %s', $to, $atts['subject'] ) );

			// Returning true reports the mail as sent, so callers do not show an error.
			return true;
		},
		10,
		2
	);
}
