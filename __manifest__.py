# -*- coding: utf-8 -*-
{
    'name': "Etiqueta de cliente personalizada",

    'summary': """
        Módulo para generar la etiqueta de cliente con datos personalizados.
       """,

    'description': """
        Módulo para generar la etiqueta de cliente con datos personalizados. 
    """,

    'author': "GonzaOdoo",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['stock'],

    # always loaded
    "data": ["security/ir.model.access.csv",
             "views/report.xml",
            ],
}
