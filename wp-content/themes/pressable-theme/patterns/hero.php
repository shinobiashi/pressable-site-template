<?php
/**
 * Title: ヒーロー（トップ）
 * Slug: pressable-theme/hero
 * Categories: pressable-theme, banner
 * Description: 濃色の帯にキャッチコピーとボタンを置くメインビジュアル。背景画像はエディターで設定する。
 *
 * @package pressable-theme
 */

?>
<!-- wp:cover {"overlayColor":"band","isUserOverlayColor":true,"minHeight":480,"contentPosition":"center left","align":"full","style":{"spacing":{"padding":{"top":"var:preset|spacing|60","bottom":"var:preset|spacing|60","left":"var:preset|spacing|50","right":"var:preset|spacing|50"}}}} -->
<div class="wp-block-cover alignfull has-custom-content-position is-position-center-left" style="padding-top:var(--wp--preset--spacing--60);padding-right:var(--wp--preset--spacing--50);padding-bottom:var(--wp--preset--spacing--60);padding-left:var(--wp--preset--spacing--50);min-height:480px"><span aria-hidden="true" class="wp-block-cover__background has-band-background-color has-background-dim-100 has-background-dim"></span><div class="wp-block-cover__inner-container"><!-- wp:group {"layout":{"type":"constrained","contentSize":"1120px","justifyContent":"left"}} -->
<div class="wp-block-group"><!-- wp:paragraph {"textColor":"band-muted","fontSize":"x-small","style":{"typography":{"letterSpacing":"0.3em"}}} -->
<p class="has-band-muted-color has-text-color has-x-small-font-size" style="letter-spacing:0.3em">SITE NAME</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":1,"textColor":"band-contrast","fontSize":"xx-large","style":{"typography":{"lineHeight":"1.4"}}} -->
<h1 class="wp-block-heading has-band-contrast-color has-text-color has-xx-large-font-size" style="line-height:1.4">キャッチコピーを<br>ここに入力します。</h1>
<!-- /wp:heading -->

<!-- wp:paragraph {"textColor":"band-contrast","fontSize":"medium"} -->
<p class="has-band-contrast-color has-text-color has-medium-font-size">サイトの概要や、訪れた人に伝えたいことを 2〜3 行で入力します。</p>
<!-- /wp:paragraph -->

<!-- wp:buttons {"style":{"spacing":{"margin":{"top":"var:preset|spacing|40"}}}} -->
<div class="wp-block-buttons" style="margin-top:var(--wp--preset--spacing--40)"><!-- wp:button -->
<div class="wp-block-button"><a class="wp-block-button__link wp-element-button" href="/contact/">お問い合わせ</a></div>
<!-- /wp:button -->

<!-- wp:button {"textColor":"band-contrast","className":"is-style-outline"} -->
<div class="wp-block-button is-style-outline"><a class="wp-block-button__link has-band-contrast-color has-text-color wp-element-button" href="/company/">会社案内</a></div>
<!-- /wp:button --></div>
<!-- /wp:buttons --></div>
<!-- /wp:group --></div></div>
<!-- /wp:cover -->
