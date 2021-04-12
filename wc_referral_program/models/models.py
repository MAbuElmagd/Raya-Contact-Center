# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta,datetime





# class HrJob(models.Model):
#     _inherit = 'hr.job'
#
#     bonus = fields.Float()


class CandidateReferral(models.Model):
    _name = 'referral.candidate'

    name = fields.Char()
    mobile = fields.Char()
    note = fields.Text()
    applicant_id = fields.Many2one('hr.applicant')

class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    referral_candidate = fields.One2many('referral.candidate','applicant_id')
    application_for = fields.Selection([('myself','Apply for myself'),('refer','Refer a Friend')])
    referred_by_hr_id = fields.Char(website_form_blacklisted=False)
    referred_by_employee = fields.Many2one('hr.employee')
    referred_by_employee_grade = fields.Many2one('employee.grade')
    three_days_training  = fields.Date()
    ninty_days_training  = fields.Date()
    fifty_three_days_training = fields.Selection([('eligible','Eligible'),('not_eligible','Not Eligible')],'50% 3 Days Training')
    fifty_three_days_training_payment = fields.Boolean('50% 3 Days Training Paid', default = False)
    fifty_ninty_days_training = fields.Selection([('eligible','Eligible'),('not_eligible','Not Eligible')],'50% 90 Days Training')
    fifty_ninty_days_training_payment = fields.Boolean('50% 90 Days Training Paid', default = False)

    compute_fields = fields.Boolean(compute="_compute_compute_fields")
    def _compute_compute_fields(self):
        for this in self:
            this._get_bonus_and_date()
            if this.training_start_date:
                this.three_days_training = this.training_start_date + timedelta(days=3)
                this.ninty_days_training = this.training_start_date + timedelta(days=90)
            this.compute_fields = True

    tarinee_status = fields.Selection([('active','Active'),('dropped','Dropped'),('certified','Certified'),('join','Join'),('re_join','Re-Join')],string="Trainee Status")

    @api.onchange('referred_by_employee')
    def _compute_referred_by_hr_id(self):
        if self.referred_by_employee:
            self.referred_by_hr_id = self.referred_by_employee.hr_id
            self.referred_by_employee_grade = self.referred_by_employee.employee_grade.id

    @api.onchange('fifty_three_days_training','fifty_ninty_days_training','training_start_date')
    def _get_bonus_and_date(self):
        for this in self:
            if this.training_start_date:
                if this.referred_by_employee:
                    if datetime.now().date() >= this.training_start_date + timedelta(days=3):
                        this.fifty_three_days_training = 'eligible'
                    else:
                        this.fifty_three_days_training = 'not_eligible'
                    if datetime.now().date() >= this.training_start_date + timedelta(days=90):
                        this.fifty_ninty_days_training = 'eligible'
                    else:
                        this.fifty_ninty_days_training = 'not_eligible'
                if this.agency:
                    if datetime.now().date() >= this.training_start_date + timedelta(days=3):
                        this.a50_certified = 'eligible'
                    else:
                        this.a50_certified = 'not_eligible'
                    if datetime.now().date() >= this.training_start_date + timedelta(days=90):
                        this.a50a90_days_hired = 'eligible'
                    else:
                        this.a50a90_days_hired = 'not_eligible'
            else:
                this.fifty_three_days_training = 'not_eligible'
                this.fifty_ninty_days_training = 'not_eligible'
                this.a50_certified = 'not_eligible'
                this.a50a90_days_hired = 'not_eligible'
