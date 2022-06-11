{
    'name': """
        Rendicion de Gastos con Facturas de Proveedor |
    """,

    'summary': """
        SUMMARY. |
    """,

    'description': """
        DESCRIPTION. |
    """,

    'author': 'Develogers',
    'website': 'https://develogers.com',
    'support': 'especialistas@develogers.com',
    'live_test_url': 'https://demo.develogers.com',
    'license': 'LGPL-3',

    'category': 'Invoice',
    'version': '14.0',

    'price': 199.99,
    'currency': 'EUR',
    
    'depends': [
        'base',
        'account',
        'hr_expense',
    ],

    'data': [
        #'security/ir.model.access.csv',
        'views/hr_expense_sheet_views.xml',
        'views/hr_expense_views.xml',
    ],

    'images': ['static/description/banner.gif'],
    
    'application': True,
    'installable': True,
    'auto_install': False,
}
