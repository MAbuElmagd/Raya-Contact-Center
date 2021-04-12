# -*- coding: utf-8 -*-
# from odoo import http


# class TechnicalInterviewerExt(http.Controller):
#     @http.route('/technical_interviewer_ext/technical_interviewer_ext/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/technical_interviewer_ext/technical_interviewer_ext/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('technical_interviewer_ext.listing', {
#             'root': '/technical_interviewer_ext/technical_interviewer_ext',
#             'objects': http.request.env['technical_interviewer_ext.technical_interviewer_ext'].search([]),
#         })

#     @http.route('/technical_interviewer_ext/technical_interviewer_ext/objects/<model("technical_interviewer_ext.technical_interviewer_ext"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('technical_interviewer_ext.object', {
#             'object': obj
#         })
