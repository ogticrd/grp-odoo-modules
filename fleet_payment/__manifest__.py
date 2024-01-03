# -*- coding: utf-8 -*-
{
    'name': "Fleet Payment",

    'summary': "Payment management for vehicle fleets",

    'description': """
        This module provides functionalities for managing payments related to vehicle fleets.
    """,

    'author': "Estarling Polanco",
    'website': "",
    'category': 'Fleet/Management',
    'version': '15.0.0.1.2',
    'depends': ['base','fleet','l10n_do_accounting'],
    'data': [
        'security/ir.model.access.csv',
        'views/method_payment.xml',
        'views/fleet_vehicle_log_services.xml',
        'report/report_fleet_vehicle_log_services.xml',
    ],
    'demo': [
        # 'demo/demo.xml',
    ],
    
    'installable': True,
    'license': 'LGPL-3',
}