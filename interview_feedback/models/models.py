# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
from odoo.exceptions import UserError
from odoo.tools.translate import _

class interview_feedback(models.Model):
    _name = 'interview_feedback'
    _description = 'interview_feedback'
    name=fields.Char(string="Acceptance Reason")

class applicant(models.Model):
    _inherit='hr.applicant'
    black_listed = fields.Boolean()
    age_calculated = fields.Float(compute="_compute_age_calculated")
    emp_project=fields.Many2one('rcc.project',compute="compute_emp_project",string="Employee Project")
    final= fields.Boolean(compute='compute_final')

    def compute_final(self):
        if self.is_final or self.is_o_final:
            self.final=True
        else:
            self.final=False

    def compute_emp_project(self):
        for this in self:
            this.emp_project=this.emp_id.project.id

    @api.onchange('date_of_birth')
    def _compute_age_calculated(self):
        for this in self:
            if this.date_of_birth:
                birth_date = this.date_of_birth
                end_date = datetime.datetime.now().date()
                time_difference = end_date - birth_date
                age = time_difference.days / 365
                this.age_calculated = age
                this.age = age

            else:
                this.age_calculated = 0.00
                this.age = 0.00
    hr_id = fields.Char("HR ID",sorted=True)
    @api.onchange('hr_id')
    def check_hr_id_douplicate(self):
        hr_ids=self.env['hr.employee'].search([('hr_id','=',self.hr_id),('id','!=',self.emp_id.id)])
        if len(hr_ids)>0:
            raise UserError(_("You can't use the same HR ID of a current Employee for this applicant!"))

    @api.onchange('emp_id')
    def _compute_hr_id_get(self):
        for this in self:
            this.hr_id = this.emp_id.hr_id or False

    accepted_first_interview=fields.Boolean(string="Accepted First Interview")
    accepted_second_interview=fields.Boolean(string="Accepted Second Interview")
    accepted_client_interview=fields.Boolean(string="Accepted Client Interview")
    accepted_first_interview_reason=fields.Many2one('interview_feedback',string="Acceptance Reason")
    accepted_second_interview_reason=fields.Many2one('interview_feedback',string="Acceptance Reason")
    accepted_client_interview_reason=fields.Many2one('interview_feedback',string="Acceptance Reason")

    @api.onchange('national_id')
    def get_national_id_emp(self):
        lines=self.env['hr.employee'].search([('identification_id','=',self.national_id)],limit=1)
        if len(lines)>=1:
            self.emp_id=lines
