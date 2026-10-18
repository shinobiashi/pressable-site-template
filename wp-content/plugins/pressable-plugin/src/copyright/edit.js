import { __ } from '@wordpress/i18n';
import { useBlockProps, InspectorControls } from '@wordpress/block-editor';
import { PanelBody, TextControl } from '@wordpress/components';
import { useSelect } from '@wordpress/data';
import { store as coreStore } from '@wordpress/core-data';

/**
 * エディター上のプレビュー。表示内容の組み立ては render.php と揃えること。
 *
 * @param {Object}                    props               Block props.
 * @param {Object}                    props.attributes    Block attributes.
 * @param {( attrs: Object ) => void} props.setAttributes Attribute setter.
 * @return {Element} Element to render.
 */
export default function Edit( { attributes, setAttributes } ) {
	const { startYear, holder, suffix } = attributes;

	// 設定の編集権限が無いユーザーでも読めるよう、サイト名は REST API のインデックスから取る。
	const siteTitle = useSelect(
		( select ) =>
			select( coreStore ).getEntityRecord( 'root', '__unstableBase' )
				?.name,
		[]
	);

	const thisYear = new Date().getFullYear();
	const years =
		startYear && startYear < thisYear
			? `${ startYear }–${ thisYear }`
			: String( thisYear );
	const text = [ '©', years, holder.trim() || siteTitle, suffix.trim() ]
		.filter( Boolean )
		.join( ' ' );

	return (
		<>
			<InspectorControls>
				<PanelBody
					title={ __( 'コピーライト設定', 'pressable-plugin' ) }
				>
					<TextControl
						label={ __( '開始年', 'pressable-plugin' ) }
						help={ __(
							'入力すると「開始年–今年」の表記になります。',
							'pressable-plugin'
						) }
						type="number"
						value={ startYear ?? '' }
						onChange={ ( value ) => {
							const year = parseInt( value, 10 );
							setAttributes( {
								startYear: Number.isNaN( year )
									? undefined
									: year,
							} );
						} }
						__nextHasNoMarginBottom
						__next40pxDefaultSize
					/>
					<TextControl
						label={ __( '権利者名', 'pressable-plugin' ) }
						help={ __(
							'空欄の場合はサイト名を表示します。',
							'pressable-plugin'
						) }
						value={ holder }
						onChange={ ( value ) =>
							setAttributes( { holder: value } )
						}
						__nextHasNoMarginBottom
						__next40pxDefaultSize
					/>
					<TextControl
						label={ __( '末尾の文言', 'pressable-plugin' ) }
						value={ suffix }
						onChange={ ( value ) =>
							setAttributes( { suffix: value } )
						}
						__nextHasNoMarginBottom
						__next40pxDefaultSize
					/>
				</PanelBody>
			</InspectorControls>
			<p { ...useBlockProps() }>{ text }</p>
		</>
	);
}
