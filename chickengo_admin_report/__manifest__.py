# -*- coding: utf-8 -*-

{
    "name": "Chickengo Admon Report",
    "category": "Hidden",
    "author": "",
    "summary": "Admon summary report",
    "version": "1.0",
    "description": """
        Sample custom report for Chickengo Admon
    """,
    "depends": [
        "point_of_sale"
    ],
    "data": [
        'data/data.xml',
        'report/admon_summary.xml',
        'wizard/admon_order_summary_wizard.xml',
    ],
    "installable": True,
}
