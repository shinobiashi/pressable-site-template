<?php
/**
 * Pressable Theme setup.
 *
 * テーマは見た目（テンプレート・パターン・スタイル）だけを扱う。
 * 独自ブロックや WooCommerce の挙動変更などの機能は pressable-plugin に実装する。
 *
 * @package pressable-theme
 */

defined( 'ABSPATH' ) || exit;

/*
 * アセットのキャッシュバスター。style.css の Version を正とし、ここでは読み取るだけにする
 * （Version を上げるとテーマのパターンキャッシュも作り直される）。
 */
define( 'PRESSABLE_THEME_VERSION', wp_get_theme( get_template() )->get( 'Version' ) );

/**
 * テーマサポート・エディタースタイル。
 */
function pressable_theme_setup() {
	add_theme_support( 'woocommerce' );
	add_editor_style( 'assets/css/theme.css' );
}
add_action( 'after_setup_theme', 'pressable_theme_setup' );

/**
 * 商品一覧（ショップ・商品カテゴリ・商品タグ）の表示件数を 3 列 × 4 行の 12 件にする。
 *
 * テンプレート（templates/archive-product.html）の商品コレクションブロックは inherit: true で
 * メインクエリを使うため、件数はブロックの perPage ではなくこのフィルターで決まる。
 *
 * @return int
 */
function pressable_theme_products_per_page() {
	return 12;
}
add_filter( 'loop_shop_per_page', 'pressable_theme_products_per_page' );

/**
 * フロントのスタイル読み込み。
 */
function pressable_theme_enqueue_assets() {
	wp_enqueue_style( 'pressable-theme', get_theme_file_uri( 'assets/css/theme.css' ), array(), PRESSABLE_THEME_VERSION );
}
add_action( 'wp_enqueue_scripts', 'pressable_theme_enqueue_assets' );

/**
 * パターンカテゴリ「サイト独自」を登録。
 */
function pressable_theme_pattern_categories() {
	register_block_pattern_category(
		'pressable-theme',
		array( 'label' => __( 'サイト独自', 'pressable-theme' ) )
	);
}
add_action( 'init', 'pressable_theme_pattern_categories' );
