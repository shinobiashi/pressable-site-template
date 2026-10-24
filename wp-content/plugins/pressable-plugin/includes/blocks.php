<?php
/**
 * 独自ブロックの登録。
 *
 * @package pressable-plugin
 */

defined( 'ABSPATH' ) || exit;

/**
 * 独自ブロック（build/ 配下）を一括登録する。
 *
 * 登録には npm run build（--blocks-manifest）が生成する build/blocks-manifest.php を使う。
 * 各ブロックの block.json をまとめたファイルなので、block.json を個別に読み込まずに済む。
 */
function pressable_plugin_register_blocks() {
	$manifest = PRESSABLE_PLUGIN_DIR . 'build/blocks-manifest.php';
	if ( ! file_exists( $manifest ) ) {
		return;
	}

	wp_register_block_types_from_metadata_collection( PRESSABLE_PLUGIN_DIR . 'build', $manifest );
}
add_action( 'init', 'pressable_plugin_register_blocks' );
