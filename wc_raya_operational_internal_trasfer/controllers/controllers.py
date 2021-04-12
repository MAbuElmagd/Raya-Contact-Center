# -*- coding: utf-8 -*-
# from odoo import http


# class WcRayaOperationalInternalTrasfer(http.Controller):
#     @http.route('/wc_raya_operational_internal_trasfer/wc_raya_operational_internal_trasfer/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/wc_raya_operational_internal_trasfer/wc_raya_operational_internal_trasfer/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('wc_raya_operational_internal_trasfer.listing', {
#             'root': '/wc_raya_operational_internal_trasfer/wc_raya_operational_internal_trasfer',
#             'objects': http.request.env['wc_raya_operational_internal_trasfer.wc_raya_operational_internal_trasfer'].search([]),
#         })

#     @http.route('/wc_raya_operational_internal_trasfer/wc_raya_operational_internal_trasfer/objects/<model("wc_raya_operational_internal_trasfer.wc_raya_operational_internal_trasfer"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('wc_raya_operational_internal_trasfer.object', {
#             'object': obj
#         })
