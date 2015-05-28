# -*- coding: utf-8 -*-
{
    'name': "Табель",

    'summary': """Табель учета рабочего времени""",

    'description': """
        Позволяет:
            - импортировать данные из базы данных парус
            - подписывать простой электронной подписью
            - печать и все другие действия с документами
    """,

    'author': "Artem Shurshilov",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Test',
    'version': '1.0.0.2',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        #'templates.xml',
	'security/security.xml',
        'security/ir.model.access.csv',
	'views/tabel.xml',
 	'views/tabel_workflow.xml',

    ],
    # only loaded in demonstration mode
    #'demo': [
    #   'demo.xml',
    #],
}


