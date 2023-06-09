# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Real Estate',
    'summary': 'Practicing developing Odoo modules',
    'description': "",
    'website': 'https://www.odoo.com/page/crm',
    'depends': [
        'base'
    ],
    'data': [
        'security/ir.model.access.csv',

        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_property_offer_views.xml',
        'views/estate_property_views.xml',
        'views/res_users_views.xml',

        'views/estate_menus.xml',
    ],
    'installable': True,
    'application': True
}