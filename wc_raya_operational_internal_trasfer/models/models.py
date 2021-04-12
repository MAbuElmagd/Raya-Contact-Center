# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError


class wc_raya_operational_internal_trasfer(models.Model):
    _name = 'wc_raya_operational_internal_trasfer'
    _description = 'wc_raya_operational_internal_trasfer'

    name = fields.Char()
    stage=fields.Selection([('draft','Draft'),('accepted','Accepted'),('rejected','Rejected')])
    emp_id = fields.Many2one('hr.employee',string="Employee Name")
    job_id =fields.Many2one('hr.job',string="Job Position")
    current_project = fields.Many2one('rcc.project',string="Current Project")
    new_project = fields.Many2one('rcc.project',string="New Project")
    internal_transfer=fields.Selection([('a','Accepted'),('b','Rejected')],)

    desc = fields.Text('Description')

    def app_name_doamin(self):
        apps=[]
        lines=self.env['hr.applicant'].search([('job_category','=','operational'),('internal_transfer_hold','=',True)])
        for line in lines:
            apps.append(line.id)
        return [('id', 'in', apps)]

    app_name=fields.Many2one('hr.applicant',string="Application",force_save=True,domain=app_name_doamin)
    active = fields.Boolean("Active", default=True, help="If the active field is set to false, it will allow you to hide the case without removing it.")

    @api.onchange('app_name')
    def check_data(self):
            line=self.env['hr.applicant'].search([('name','=',self.app_name.name)], limit=1)
            self.job_id=line.job_id.id
            self.emp_id=line.emp_id.id
            self.current_project=line.emp_project.id
            self.new_project=line.project.id
            self.app_name=line.id

    @api.model
    def create(self, vals):
        res = super(wc_raya_operational_internal_trasfer, self).create(vals)
        res.stage='draft'
        return res

    def internal_transfer_approve(self):
        self.app_name.internal_transfer_hold=False
        self.app_name.internal_transfer_request='a'
        self.internal_transfer='a'
        self.stage='accepted'
        self.app_name.internal_transfer=True

    def internal_transfer_reject(self):
        self.app_name.internal_transfer_request='b'
        self.internal_transfer='b'
        self.stage='rejected'
        self.app_name.internal_transfer=True

    def unlink(self):
        for this in self:
            if this.app_name:
                if self.stage!='draft':
                    raise UserError(
                        _('This Request is connected to an application you can not delete it right now.')
                    )
        return super(wc_raya_operational_internal_trasfer, self).unlink()

    
class Applicant(models.Model):
    _inherit = "hr.applicant"

    internal_transfer_hold=fields.Boolean(string="Internal Transfer Hold")
    internal_transfer_request=fields.Selection([('a','Accepted'),('b','Rejected')],string="Internal Transfer Request")
    internal_transfer=fields.Boolean(string="Internal Transfer")
    internal_transfer_counts = fields.Integer(compute="_compute_internal_transfer_counts")

    def _compute_internal_transfer_counts(self):
        for this in self:
            internal_transfers = self.env['wc_raya_operational_internal_trasfer'].search([('app_name','=',this.id)])
            this.internal_transfer_counts = len(internal_transfers)

    def action_view_internal_transfer_counts(self):
        action = self.env["ir.actions.actions"]._for_xml_id('wc_raya_operational_internal_trasfer.action_window')
        asses = self.env['wc_raya_operational_internal_trasfer'].search([('app_name','=',self.id)])
        action['domain'] = [('id','in',asses.ids)]
        return action
    
    @api.model
    def create(self, vals):
        res = super(Applicant, self).create(vals)
        if res.job_id==res.emp_id.job_id and res.job_category=='operational':
            res.internal_transfer_hold=True
        return res
    
    @api.constrains('stage_id')
    def internal_transfer_hold_stage_constrain(self):
        if self.internal_transfer_hold==True and self.is_initial!=True:
             raise UserError(
                    _('This Application is under Internal Transfer Hold you Can not Procees on it now.')
                )
    def unlink(self):
        for this in self:
            asses = self.env['wc_raya_operational_internal_trasfer'].search([('app_name','=',this.id)])
            if asses.stage!='draft':
                if this.internal_transfer_counts>0:
                    raise UserError(
                        _('This Application has proccessed Internal Transfer Request.')
                    )
            else:
                if this.internal_transfer_counts>0:
                    asses.unlink()
        return super(Applicant, self).unlink()

class internal_transfer_desc(models.TransientModel):
    _name = 'internal_transfer_desc'
    _description = "Create Meeting from Task"

    desc = fields.Text('Description' ,required=True)

    def get_data(self):
        applicant= self.env['hr.applicant'].browse(self._context.get('active_ids'))
        if applicant.job_category=='operational':
            self.env['wc_raya_operational_internal_trasfer'].create({
            'app_name':applicant.id,
                    'name':applicant.name,
                    'job_id':applicant.job_id.id,
                    'new_project':applicant.project.id,
                    'emp_id':applicant.emp_id.id,
                    'current_project':applicant.emp_id.project.id,
                    'desc':self.desc,
            })
        return True