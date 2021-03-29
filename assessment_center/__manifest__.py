# -*- coding: utf-8 -*-
{
    'name': "ًWC Assessment Center",

    'summary': """
        HR Applicant Assessment MAnagment APP""",

    'description': """
         Assessment MAnagment APP
    """,

    'author': "White Code",
    'website': "http://www.white-code.co.uk",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Generic module',
    'version': '14.0',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','hr_recruitment','survey','employee_enhancement','wc_hiring_request','wc_ta_extention',
        'fetchmail',
        'utm',
        'attachment_indexation',
        'web_tour',
        'digest','calendar',],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'wizard/assessment_test.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'qweb': ['static/src/xml/base_calendar.xml'],
    "installable": True,
    "application": True,
}
