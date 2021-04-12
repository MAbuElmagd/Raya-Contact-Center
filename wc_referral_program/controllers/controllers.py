# -*- coding: utf-8 -*-
# from odoo import http


# class WcReferralProgram(http.Controller):
#     @http.route('/wc_referral_program/wc_referral_program/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/wc_referral_program/wc_referral_program/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('wc_referral_program.listing', {
#             'root': '/wc_referral_program/wc_referral_program',
#             'objects': http.request.env['wc_referral_program.wc_referral_program'].search([]),
#         })

#     @http.route('/wc_referral_program/wc_referral_program/objects/<model("wc_referral_program.wc_referral_program"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('wc_referral_program.object', {
#             'object': obj
#         })
