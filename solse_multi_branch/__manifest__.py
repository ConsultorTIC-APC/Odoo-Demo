# -*- coding: utf-8 -*-
# Copyright (c) 2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
{
	'name': "Multi Sucursal",

	'summary': """
		Multi Sucursal
		""",

	'description': """
		Multi Sucursal
	""",

	'author': "F & M Solutions Service S.A.C",
	'website': "https://www.solse.pe",

	'category': 'Uncategorized',
	'version': '14.0.2',
	'depends': ['base', 'web','sale_management', 'purchase', 'solse_pe_edi', 'solse_pe_cpe'],
	'data': [
		'data/res_branch_data.xml',
		'security/security.xml',
		'security/ir.model.access.csv',
		'report/report_invoice.xml',
		'views/res_branch_view.xml',
		'views/template.xml',
		'views/stock_view.xml',
		'views/sale_view.xml',
		'views/purchase_view.xml',
		'views/account_view.xml',
		'views/product_view.xml',
		'report/sale_report_template.xml',
	],
	'demo': [],
	"qweb":  ['static/src/xml/branch_menu.xml'],
	'installable': True,
	'auto_install': False,
	'application': True,
	"sequence": 1,
}