# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _

class applicant_religion(models.Model):
    _name = 'applicant_religion'
    _description = 'wc_raya_updates2.applicant_religion'

    name=fields.Char(string="Name",required=True)

class hrApplicant(models.Model):
    _inherit = "hr.applicant"

    religion=fields.Many2one('applicant_religion',string="Religion")
    tower=fields.Many2one('wc_raya_qoh.tower',string="Tower")
    working_location = fields.Many2one('work.locations',string="Working Location")
    sector = fields.Many2one('sector.sector',string="Sector" )
    batch_numbers = fields.Integer(string="Batch Numbers",required=True)

    @api.onchange('hiring_request')
    def get_tower(self):
        self.tower=self.hiring_request.tower.id or False
        self.working_location=self.hiring_request.working_location.id or False
        self.sector=self.hiring_request.sector.id or False
        self.batch_numbers=self.hiring_request.batch_numbers


class Employee(models.Model):
    _inherit = 'hr.employee'

    @api.onchange('address_home_id')
    def check_national_id_match(self):
        if self.address_home_id.national_id:
            if self.address_home_id.national_id != self.identification_id:
                raise UserError(_('The National ID on the Address is not the same National ID on the Employee!'))

class wc_raya_qoh(models.Model):
    _name = 'wc_raya_qoh.tower'
    _description = 'wc_raya_qoh.tower'

    name = fields.Char()



class WorkLocations(models.Model):
    _inherit = "work.locations"
    _description = "Working Locations"

    tower=fields.Many2one('wc_raya_qoh.tower',string="Tower")

class HiringRequest(models.Model):
    _inherit = "hiring.request"

    tower=fields.Many2one('wc_raya_qoh.tower',string="Tower")
