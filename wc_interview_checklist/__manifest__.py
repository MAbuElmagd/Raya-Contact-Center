# -*- coding: utf-8 -*-
{
    'name': "wc_interview_checklist",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_recruitment','wc_ta_extention','hr_recruitment_double_hiring', 'hr_recruitment_survey', 'hr_skill_qualification', 'wc_hiring_request', 'wc_sourcing_extension', 'wc_updates', 'website_hr_recruitment','employee_enhancement', 'hr', 'wc_applicat_extention','wc_screening_excel'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
