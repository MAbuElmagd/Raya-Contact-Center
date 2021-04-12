# -*- coding: utf-8 -*-
# from odoo import http


# class WcShaghalny(http.Controller):
#     @http.route('/wc_shaghalny/wc_shaghalny/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/wc_shaghalny/wc_shaghalny/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('wc_shaghalny.listing', {
#             'root': '/wc_shaghalny/wc_shaghalny',
#             'objects': http.request.env['wc_shaghalny.wc_shaghalny'].search([]),
#         })

#     @http.route('/wc_shaghalny/wc_shaghalny/objects/<model("wc_shaghalny.wc_shaghalny"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('wc_shaghalny.object', {
#             'object': obj
#         })
