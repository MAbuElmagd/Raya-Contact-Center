# -*- coding: utf-8 -*-
# from odoo import http


# class EmployeeEnhancement(http.Controller):
#     @http.route('/employee_enhancement/employee_enhancement/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/employee_enhancement/employee_enhancement/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('employee_enhancement.listing', {
#             'root': '/employee_enhancement/employee_enhancement',
#             'objects': http.request.env['employee_enhancement.employee_enhancement'].search([]),
#         })

#     @http.route('/employee_enhancement/employee_enhancement/objects/<model("employee_enhancement.employee_enhancement"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('employee_enhancement.object', {
#             'object': obj
#         })
