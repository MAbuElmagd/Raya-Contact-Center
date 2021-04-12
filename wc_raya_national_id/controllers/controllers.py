# -*- coding: utf-8 -*-
# from odoo import http


# class WcRayaNationalId(http.Controller):
#     @http.route('/wc_raya_national_id/wc_raya_national_id/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/wc_raya_national_id/wc_raya_national_id/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('wc_raya_national_id.listing', {
#             'root': '/wc_raya_national_id/wc_raya_national_id',
#             'objects': http.request.env['wc_raya_national_id.wc_raya_national_id'].search([]),
#         })

#     @http.route('/wc_raya_national_id/wc_raya_national_id/objects/<model("wc_raya_national_id.wc_raya_national_id"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('wc_raya_national_id.object', {
#             'object': obj
#         })
