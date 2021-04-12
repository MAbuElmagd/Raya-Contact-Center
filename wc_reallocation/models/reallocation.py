# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import float_compare
from odoo.exceptions import UserError


REALLOCATION_STATE = [('draft','Draft'),('approved','Approved'),('terminate','Terminate')]

class Application(models.Model):
    _inherit = 'hr.applicant'
    _description = "hr.applicant"

    is_reallocation = fields.Boolean()
    reallocation_reason=fields.Many2one('reallocation.reason',string="Reallocation reason")
    reallocation_desc=fields.Text(string="Reallocation Description")
    terminated=fields.Boolean(string="Terminated")

    def terminate_employment(self):


        # message_id = self.env['message.wizard'].create({'message':"You must Terminate the Employee on Connect Zone and Confirm"})

        return {
            'name': _('Terminate'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'message.wizard',
            # # pass the id
            # 'res_id': message_id.id,
            'target': 'new'
        }

class ReallocationReason(models.Model):
    _name = 'reallocation.reason'
    _description = "reallocation.reason"

    name = fields.Char(required=True)

class Reallocation(models.Model):
    _name = 'reallocation.reallocation'
    _description = "reallocation.reallocation"
    name = fields.Char(required=True)
    state = fields.Selection(REALLOCATION_STATE,default="draft")
    employee = fields.Many2one('hr.employee',required=True)

    department_id = fields.Many2one('hr.department')
    job_id = fields.Many2one('hr.job','Job Position', domain="[('job_category', '=', 'operational')]")
    project_id = fields.Many2one('rcc.project')
    hr_id = fields.Char('HR ID')
    manager_id = fields.Many2one('hr.employee')

    reallocation_reason = fields.Many2one('reallocation.reason','Reallocation Reason',required=True)
    description = fields.Text(required=True)

    job_to = fields.Many2one('hr.job','Position allocated To',required=True, domain="[('job_category', '=', 'operational')]")
    project_to = fields.Many2one('rcc.project','Project allocated To',required=True)


    application_id = fields.Many2one('hr.applicant')
    terminated = fields.Boolean('Terminated on Connect Zone')
    reallocation_approved = fields.Boolean('Reallocation Approved')

    @api.onchange('state')
    def state_change(self):
        if self.state == 'terminate':
            if not self.terminated:
                mess= {
                        'title': _('WARNING!'),
                        'message' : "You must terminate the Employee on Connect Zone and Confirm."
                    }
                return {'warning': mess}



    @api.onchange('employee')
    def employee_change(self):
        if self.employee:
            if self.name == "" or self.name == False :
                self.name = "Reallocation to "+self.employee.name

            self.department_id = self.employee.department_id.id
            self.job_id = self.employee.job_id.id
            self.project_id = self.employee.project.id
            self.hr_id = self.employee.hr_id
            self.manager_id = self.employee.parent_id.id
        else:
            self.department_id = False
            self.job_id = False
            self.project_id = False
            self.hr_id = ""
            self.manager_id = False

    def approve_reallocation(self):
        print('Approve Reallocation')
        self.state = "approved"
        self.reallocation_approved = True

    def create_application(self):
        print('Create Application')
        application = self.env['hr.applicant'].create({
            "name":self.employee.name+"'s Application",
            "partner_name":self.employee.name,
            "job_category":"operational",
            "stage_id":1,
            "department_id": self.employee.department_id.id,
            "job_id":self.job_to.id,
            "national_id":self.employee.identification_id,
            "partner_id":self.employee.address_home_id.id,
            "email_from":self.employee.work_email,
            "project": self.project_to.id,
            "partner_phone": "",
            "is_reallocation": True,
            "reallocation_id": self.id,
            "hr_id": self.hr_id,
            "emp_id": self.employee.id,
            'date_of_birth': self.employee.birthday,
            'nationality':self.employee.country_id.id,
            'gender': self.employee.gender,
            'military_status':self.employee.military_status,
        })
        self.application_id = application

    def terminate_employment(self):


        # message_id = self.env['message.wizard'].create({'message':"You must Terminate the Employee on Connect Zone and Confirm"})

        return {
            'name': _('Terminate'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'message.wizard',
            # # pass the id
            # 'res_id': message_id.id,
            'target': 'new'
        }

class HrEmployeePrivate(models.Model):
    _inherit = "hr.employee"

    job_category = fields.Selection([('talent','Talent'),('operational','Operational')], compute="compute_job_category")
    job_category_n_c = fields.Selection([('talent','Talent'),('operational','Operational')])
    reallocation_count=fields.Integer(string='Reallocations', compute='_compute_reallocations')

    def _compute_reallocations(self):
        for this in self:
            this.reallocation_count=self.env['hr.applicant'].search_count([('emp_id.id', '=', self.id),('is_reallocation','=',True)])

    def compute_job_category(self):
        for this in self :
            if this.job_id.job_category=='talent':
                this.job_category='talent'
                this.job_category_n_c='talent'
            elif this.job_id.job_category=='operational':
                this.job_category='operational'
                this.job_category_n_c='operational'
            else:
                this.job_category=False

    def action_open_reallocations(self):
        self.ensure_one()
        return {
        'type': 'ir.actions.act_window',
        'name': 'Reallocations',
        'view_mode': 'tree',
        'res_model': 'hr.applicant',
        'domain': [('emp_id.id', '=', self.id),('is_reallocation','=',True)],
        'context': "{'create': False}"
        }

    def create_reallocation(self):
        for this in self:
            if this.job_category=='operational':
                this.env['hr.applicant'].create({
                "name":this.name+"'s Application",
                "partner_name":this.name,
                "job_category":"operational",
                'stage_id':this.env['hr.recruitment.stage'].search([('job_category','=','operational'),('is_o_initial','=',True)],limit=1).id,
                "department_id": this.department_id.id,
                "job_id":this.job_id.id,
                "national_id":this.identification_id,
                "partner_id":this.address_home_id.id,
                "email_from":this.work_email,
                "partner_phone": "",
                "is_reallocation": True,
                # "reallocation_id": this.id,
                "hr_id": this.hr_id,
                "emp_id": this.id,
                'date_of_birth': this.birthday,
                'nationality':this.country_id.id,
                'gender': this.gender,
                'military_status':this.military_status,
                })
