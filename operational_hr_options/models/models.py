# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HiringRequest(models.Model):
    _inherit = 'hiring.request'

    options = fields.Selection([('campaign','Campaign'),('permanent','Permanent')])

class Applicant(models.Model):
    _inherit = 'hr.applicant'

    options = fields.Selection([('campaign','Campaign'),('permanent','Permanent')])

    @api.onchange('hiring_request')
    def get_options(self):
        if self.hiring_request:
            self.options = self.hiring_request.options
