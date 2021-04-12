# -*- coding: utf-8 -*-
# from odoo import http


# class WcRayaHcStatus(http.Controller):
#     @http.route('/wc_raya_hc_status/wc_raya_hc_status/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/wc_raya_hc_status/wc_raya_hc_status/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('wc_raya_hc_status.listing', {
#             'root': '/wc_raya_hc_status/wc_raya_hc_status',
#             'objects': http.request.env['wc_raya_hc_status.wc_raya_hc_status'].search([]),
#         })

#     @http.route('/wc_raya_hc_status/wc_raya_hc_status/objects/<model("wc_raya_hc_status.wc_raya_hc_status"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('wc_raya_hc_status.object', {
#             'object': obj
#         })
