<?php
/**
 * WooCommerce まわりの処理。
 *
 * WooCommerce のフック（woocommerce_* / before_woocommerce_init など）に登録する処理は
 * WooCommerce が無効なら呼ばれないので、ここにまとめておけばショップでないサイトでも害はない。
 * WooCommerce の関数（wc_get_products() など）を WordPress 本体のフックから直接呼ぶ場合だけ、
 * function_exists() で存在を確かめること。
 *
 * @package pressable-plugin
 */

defined( 'ABSPATH' ) || exit;

/**
 * HPOS（注文テーブル）とカート・チェックアウトブロックへの対応を宣言する。
 *
 * 宣言が無いと、WooCommerce の機能設定画面で「互換性のないプラグイン」として扱われる。
 * 注文データを直接 SQL で扱う処理を追加する場合は、HPOS・投稿テーブルの両方に対応させること。
 */
function pressable_plugin_declare_wc_compatibility() {
	if ( ! class_exists( \Automattic\WooCommerce\Utilities\FeaturesUtil::class ) ) {
		return;
	}

	\Automattic\WooCommerce\Utilities\FeaturesUtil::declare_compatibility( 'custom_order_tables', PRESSABLE_PLUGIN_FILE, true );
	\Automattic\WooCommerce\Utilities\FeaturesUtil::declare_compatibility( 'cart_checkout_blocks', PRESSABLE_PLUGIN_FILE, true );
}
add_action( 'before_woocommerce_init', 'pressable_plugin_declare_wc_compatibility' );
