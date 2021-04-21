{
    'name': "L10n DO Government Products",

    'summary': """
        This module adds the default product catalog used by government.
        """,

    'author': "Kevin Jiménez, OPTIC",
    'website': "https://optic.gov.do",

    'category': 'Localization',
    'version': '0.1',

    'depends': ['base', 'l10n_do'],

    'data': [
        'data/account.analytic.account.csv',
        'data/product.category.xml',
        'data/product.product.xml',
    ],
}
