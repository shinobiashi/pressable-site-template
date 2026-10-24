<?php
// This file is generated. Do not modify it manually.
return array(
	'copyright' => array(
		'$schema' => 'https://schemas.wp.org/trunk/block.json',
		'apiVersion' => 3,
		'name' => 'pressable-plugin/copyright',
		'version' => '1.0.0',
		'title' => 'コピーライト',
		'category' => 'theme',
		'icon' => 'shield',
		'description' => '「© 開始年–今年 権利者名」を表示します。年は表示のたびに自動で更新されます。',
		'keywords' => array(
			'copyright',
			'コピーライト',
			'著作権'
		),
		'textdomain' => 'pressable-plugin',
		'attributes' => array(
			'startYear' => array(
				'type' => 'integer'
			),
			'holder' => array(
				'type' => 'string',
				'default' => ''
			),
			'suffix' => array(
				'type' => 'string',
				'default' => 'All Rights Reserved.'
			)
		),
		'supports' => array(
			'html' => false,
			'color' => array(
				'text' => true,
				'background' => false,
				'link' => false
			),
			'spacing' => array(
				'margin' => true
			),
			'typography' => array(
				'fontSize' => true,
				'textAlign' => true
			)
		),
		'editorScript' => 'file:./index.js',
		'render' => 'file:./render.php'
	)
);
