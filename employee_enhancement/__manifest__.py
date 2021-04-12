# -*- coding: utf-8 -*-
{
    'name': "Employee Enhancement",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "White Code",
    'website': "http://www.white-code.co.uk",

    'category': 'Generic module',
    'version': '14.0',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','wc_hiring_request','hr_recruitment'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/employee_enhancement_security.xml',
        'views/employee.xml',
        'views/employee_grade.xml',
        'views/head_count.xml',
        'views/misconduct.xml',
    ],
}
