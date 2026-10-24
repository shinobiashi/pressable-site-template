<?php
/**
 * コピーライトブロックのサーバーサイドレンダリング。
 *
 * 年はサイトのタイムゾーンで表示時に計算する（保存済みのテンプレートでも毎年手直ししなくてよい）。
 * 権利者名が空ならサイト名を使う。表示内容の組み立ては edit.js のプレビューと揃えること。
 *
 * @var array    $attributes ブロック属性。
 * @var string   $content    インナーコンテンツ（未使用）。
 * @var WP_Block $block      ブロックインスタンス。
 *
 * @package pressable-plugin
 */

defined( 'ABSPATH' ) || exit;

$pressable_plugin_this_year  = (int) wp_date( 'Y' );
$pressable_plugin_start_year = isset( $attributes['startYear'] ) ? absint( $attributes['startYear'] ) : 0;
$pressable_plugin_years      = ( $pressable_plugin_start_year && $pressable_plugin_start_year < $pressable_plugin_this_year )
	? $pressable_plugin_start_year . '–' . $pressable_plugin_this_year
	: (string) $pressable_plugin_this_year;

$pressable_plugin_holder = isset( $attributes['holder'] ) ? trim( (string) $attributes['holder'] ) : '';
if ( '' === $pressable_plugin_holder ) {
	$pressable_plugin_holder = get_bloginfo( 'name' );
}
$pressable_plugin_suffix = isset( $attributes['suffix'] ) ? trim( (string) $attributes['suffix'] ) : '';

$pressable_plugin_text = implode(
	' ',
	array_filter(
		array( '©', $pressable_plugin_years, $pressable_plugin_holder, $pressable_plugin_suffix ),
		'strlen'
	)
);
?>
<p <?php echo get_block_wrapper_attributes(); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- get_block_wrapper_attributes() returns escaped attributes. ?>><?php echo esc_html( $pressable_plugin_text ); ?></p>
