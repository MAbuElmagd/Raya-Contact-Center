# -*- coding: utf-8 -*-
# from odoo import http


# class WcRayaOperationalDoubleHiring(http.Controller):
#     @http.route('/wc_raya_operational_double_hiring/wc_raya_operational_double_hiring/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/wc_raya_operational_double_hiring/wc_raya_operational_double_hiring/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('wc_raya_operational_double_hiring.listing', {
#             'root': '/wc_raya_operational_double_hiring/wc_raya_operational_double_hiring',
#             'objects': http.request.env['wc_raya_operational_double_hiring.wc_raya_operational_double_hiring'].search([]),
#         })

#     @http.route('/wc_raya_operational_double_hiring/wc_raya_operational_double_hiring/objects/<model("wc_raya_operational_double_hiring.wc_raya_operational_double_hiring"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('wc_raya_operational_double_hiring.object', {
#             'object': obj
#         })
