# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from odoo.exceptions import ValidationError,UserError

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    identification_id = fields.Char(string="National ID", required=True ,size=14)
    
    @api.constrains('identification_id')
    def _constrains_identification_id(self):
        if self.identification_id:
            id_length = len(self.identification_id.replace(" ", ""))
            if id_length != 14 or not self.identification_id.isnumeric() or not self.identification_id.isascii() or len(self.search([('identification_id','=',self.identification_id),('id', '!=', self.id)])) > 0:
                raise ValidationError(_('National ID Shoud Be 14, English Numeric Only & Unique!'))

class hrApplicant(models.Model):
    _inherit = "hr.applicant"

    national_id = fields.Char(string="National id", required=True ,size=14)

    @api.constrains('national_id')
    def _constrains_national_id(self):
        if self.national_id:
            id_length = len(self.national_id.replace(" ", ""))
            if id_length != 14 or not self.national_id.isnumeric() or not self.national_id.isascii():
                raise ValidationError(_('National ID Shoud Be 14, English Numeric Only & Unique!'))