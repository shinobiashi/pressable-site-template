<?php
/**
 * Title: お問い合わせ誘導（CTA）
 * Slug: pressable-theme/cta
 * Categories: pressable-theme, call-to-action
 * Description: 濃色の帯に見出し・説明文・ボタンを中央揃えで置くセクション。
 *
 * @package pressable-theme
 */

?>
<!-- wp:group {"align":"full","backgroundColor":"band","textColor":"band-contrast","style":{"spacing":{"padding":{"top":"var:preset|spacing|60","bottom":"var:preset|spacing|60","left":"var:preset|spacing|40","right":"var:preset|spacing|40"}}},"layout":{"type":"constrained","contentSize":"760px"}} -->
<div class="wp-block-group alignfull has-band-contrast-color has-band-background-color has-text-color has-background" style="padding-top:var(--wp--preset--spacing--60);padding-right:var(--wp--preset--spacing--40);padding-bottom:var(--wp--preset--spacing--60);padding-left:var(--wp--preset--spacing--40)"><!-- wp:heading {"textAlign":"center","level":2,"textColor":"band-contrast"} -->
<h2 class="wp-block-heading has-text-align-center has-band-contrast-color has-text-color">お気軽にお問い合わせください</h2>
<!-- /wp:heading -->

<!-- wp:paragraph {"align":"center","textColor":"band-muted"} -->
<p class="has-text-align-center has-band-muted-color has-text-color">ご相談・お見積りは無料です。フォームから 24 時間受け付けています。</p>
<!-- /wp:paragraph -->

<!-- wp:buttons {"layout":{"type":"flex","justifyContent":"center"},"style":{"spacing":{"margin":{"top":"var:preset|spacing|40"}}}} -->
<div class="wp-block-buttons" style="margin-top:var(--wp--preset--spacing--40)"><!-- wp:button -->
<div class="wp-block-button"><a class="wp-block-button__link wp-element-button" href="/contact/">お問い合わせフォームへ</a></div>
<!-- /wp:button --></div>
<!-- /wp:buttons --></div>
<!-- /wp:group -->
