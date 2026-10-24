<?php
/**
 * Title: お知らせ（最新 3 件）
 * Slug: pressable-theme/news
 * Categories: pressable-theme
 * Description: 投稿カテゴリ「お知らせ」（スラッグ news）の最新 3 件を日付つきで一覧表示。
 *
 * クエリーブロックのカテゴリ指定は term ID のため、サイトごとに異なる ID をスラッグから引いて埋め込む。
 * カテゴリが無いサイトでは何も出力しない。
 *
 * @package pressable-theme
 */

$pressable_theme_news_term = get_term_by( 'slug', 'news', 'category' );
if ( ! $pressable_theme_news_term ) {
	return;
}
$pressable_theme_news_link = get_term_link( $pressable_theme_news_term );
?>
<!-- wp:group {"style":{"spacing":{"padding":{"top":"var:preset|spacing|60","bottom":"var:preset|spacing|60","left":"var:preset|spacing|40","right":"var:preset|spacing|40"}}},"layout":{"type":"constrained","contentSize":"1120px"}} -->
<div class="wp-block-group" style="padding-top:var(--wp--preset--spacing--60);padding-right:var(--wp--preset--spacing--40);padding-bottom:var(--wp--preset--spacing--60);padding-left:var(--wp--preset--spacing--40)"><!-- wp:group {"layout":{"type":"flex","verticalAlignment":"bottom","justifyContent":"space-between"}} -->
<div class="wp-block-group"><!-- wp:group {"layout":{"type":"flex","verticalAlignment":"bottom"}} -->
<div class="wp-block-group"><!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">お知らせ</h2>
<!-- /wp:heading -->

<!-- wp:paragraph {"textColor":"accent","fontSize":"x-small","style":{"typography":{"letterSpacing":"0.22em"}}} -->
<p class="has-accent-color has-text-color has-x-small-font-size" style="letter-spacing:0.22em">NEWS</p>
<!-- /wp:paragraph --></div>
<!-- /wp:group -->

<?php if ( ! is_wp_error( $pressable_theme_news_link ) ) : ?>
<!-- wp:paragraph {"fontSize":"small"} -->
<p class="has-small-font-size"><a href="<?php echo esc_url( $pressable_theme_news_link ); ?>">すべて見る →</a></p>
<!-- /wp:paragraph -->
<?php endif; ?>
</div>
<!-- /wp:group -->

<!-- wp:query {"queryId":4,"query":{"perPage":3,"pages":0,"offset":0,"postType":"post","order":"desc","orderBy":"date","author":"","search":"","exclude":[],"sticky":"","inherit":false,"taxQuery":{"category":[<?php echo (int) $pressable_theme_news_term->term_id; ?>]}},"className":"pressable-theme-news"} -->
<div class="wp-block-query pressable-theme-news"><!-- wp:post-template -->
<!-- wp:group {"className":"pressable-theme-news-item","style":{"spacing":{"blockGap":"var:preset|spacing|40"}},"layout":{"type":"flex","flexWrap":"nowrap","verticalAlignment":"center"}} -->
<div class="wp-block-group pressable-theme-news-item"><!-- wp:post-date {"format":"Y.m.d","textColor":"body","fontSize":"small"} /-->

<!-- wp:post-title {"level":3,"isLink":true,"fontSize":"medium"} /--></div>
<!-- /wp:group -->
<!-- /wp:post-template -->

<!-- wp:query-no-results -->
<!-- wp:paragraph {"textColor":"body"} -->
<p class="has-body-color has-text-color">現在お知らせはありません。</p>
<!-- /wp:paragraph -->
<!-- /wp:query-no-results --></div>
<!-- /wp:query --></div>
<!-- /wp:group -->
