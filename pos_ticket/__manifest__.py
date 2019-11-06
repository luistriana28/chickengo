# Copyright 2019(S), Cybrosys Techno Solutions & Luis Triana
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Company Logo In POS Receipt',
    'summary': 'Company Logo In POS Receipt',
    'version': '12.0.1.0.0',
    'category': 'Point of Sale',
    'website': 'https://odoo-community.org/',
    'author': 'Cybrosys Techno Solutions, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'depends': [
        'base',
        'point_of_sale'
    ],
    'data': [
    ],
    'demo': [
    ],
    'qweb': [
        'static/src/xml/pos_ticket_view.xml',
    ],
    'application': True,
    'installable': True
}
