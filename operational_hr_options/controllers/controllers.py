# -*- coding: utf-8 -*-
# from odoo import http


# class OperationalHrOptions(http.Controller):
#     @http.route('/operational_hr_options/operational_hr_options/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/operational_hr_options/operational_hr_options/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('operational_hr_options.listing', {
#             'root': '/operational_hr_options/operational_hr_options',
#             'objects': http.request.env['operational_hr_options.operational_hr_options'].search([]),
#         })

#     @http.route('/operational_hr_options/operational_hr_options/objects/<model("operational_hr_options.operational_hr_options"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('operational_hr_options.object', {
#             'object': obj
#         })
