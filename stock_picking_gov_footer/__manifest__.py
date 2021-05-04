{
    'name': "Stock Picking Gov Footer",

    'summary': """
        This module add a header with standard government footer style with approbals fields
    """,

    'author': "Kevin Jiménez, OPTIC",
    'website': "https://optic.gob.do",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base', 'stock', 'company_report_gov_header'],

    'data': [
        'views/templates.xml',
    ],
    'auto_install': True,
}
