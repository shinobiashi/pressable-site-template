<?php
/**
 * Plugin Name:       Pressable Plugin
 * Description:       サイト固有の機能（独自ブロック・WooCommerce のカスタマイズなど）をまとめたプラグイン。見た目は pressable-theme が担当します。
 * Version:           1.0.0
 * Requires at least: 6.8
 * Requires PHP:      8.3
 * Author:            Shinobiashi INC.
 * License:           GPL-2.0-or-later
 * License URI:       https://www.gnu.org/licenses/gpl-2.0.html
 * Text Domain:       pressable-plugin
 * Update URI:        false
 *
 * @package pressable-plugin
 */

defined( 'ABSPATH' ) || exit;

define( 'PRESSABLE_PLUGIN_VERSION', '1.0.0' );
define( 'PRESSABLE_PLUGIN_FILE', __FILE__ );
define( 'PRESSABLE_PLUGIN_DIR', plugin_dir_path( __FILE__ ) );

require_once PRESSABLE_PLUGIN_DIR . 'includes/blocks.php';
require_once PRESSABLE_PLUGIN_DIR . 'includes/woocommerce.php';
