# -*- coding: utf-8 -*-
{
	'name': "CPE Ventas",

	'summary': """
		Enlace del modulo de ventas con la creacion de facturas electronicas""",

	'description': """
		Facturación electrónica - Perú 
		Enlace del modulo de ventas con la creacion de facturas electronicas
	""",

	'author': "F & M Solutions Service S.A.C",
	'website': "https://www.solse.pe",
	'category': 'Financial',
	'version': '1.0',

	'depends': [
		'solse_pe_edi',
		'sale_management',
	],
	'data': [
		'views/sale_order_view.xml',
	],
	'installable': True,
	'price': 60,
	'currency': 'USD',
}