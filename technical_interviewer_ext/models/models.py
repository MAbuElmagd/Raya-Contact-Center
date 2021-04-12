# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError,UserError

class Partner(models.Model):
    _inherit = "res.partner"

    technical_interview_applications = fields.Many2many('hr.applicant','partner_user_tech_applicant_rel','partner_id','applicant_id', compute="_compute_technical_interview_applications")
    def _compute_technical_interview_applications(self):
        for this in self:
            this.technical_interview_applications = False
            partner_user = self.env['res.users'].search([('partner_id','=',this.id)])
            if partner_user and len(partner_user) > 0:
                technical_stage = self.env['hr.recruitment.stage'].search([('job_category','=','operational'),('technical','=','true')])
                if technical_stage:
                    technical_applicants = self.env['hr.applicant'].search([('stage_id','=',technical_stage.id),('technical_interviewer','=',partner_user.id),('technical_done','=',False)])
                    if technical_applicants and len(technical_applicants) > 0:
                        this.technical_interview_applications = [(6,0,technical_applicants.ids)]

class MailTemplate(models.Model):
    _inherit = "mail.template"
    technical_notify = fields.Boolean(string="Single Technical Interviewer Notification")
    technical_interview_notification = fields.Boolean(string="Mass Technical Interviewer Notification")

    @api.constrains('technical_notify')
    def _constrains_technical_notify(self):
        for rec in self:
            mail = self.search([('technical_notify', '=', True),
                                   ('id', '!=', rec.id)])
            if mail and rec.technical_notify:
                raise UserError(
                    _('Technical Interview Notification Template Already Marked in %s.' % mail.name)
                )
    @api.constrains('technical_interview_notification')
    def _constrains_technical_interview_notification(self):
        for rec in self:
            mail = self.search([('technical_interview_notification', '=', True),
                                   ('id', '!=', rec.id)])
            if mail and rec.technical_interview_notification:
                raise UserError(
                    _('Technical Interview Notification Template Already Marked in %s.' % mail.name)
                )

class Stages(models.Model):
    _inherit = 'hr.recruitment.stage'

    technical = fields.Boolean()

    @api.constrains('technical')
    def _constrains_technical(self):
        for rec in self:
            stage = self.search([('technical', '=', True),
                                   ('id', '!=', rec.id),
                                   ('job_category','=','operational')])
            if stage and rec.technical:
                raise UserError(
                    _('Technical Stage Already Marked in %s.' % stage.name)
                )
class Applicant(models.Model):
    _inherit = 'hr.applicant'

    def send_technical_notify(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('technical_interviewer_ext', 'email_template_tech_single_notify')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'force_email': True,
            'default_partner_ids':[(6,0,[self.technical_interviewer.partner_id.id])]
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def notify_technical_interview(self):
        technical_interviewer_ids = []
        for user in self.env['res.users'].search([]):
            technical_stage = self.env['hr.recruitment.stage'].search([('job_category','=','operational'),('technical','=','true')])
            if technical_stage:
                technical_applicants = self.env['hr.applicant'].search([('stage_id','=',technical_stage.id),('technical_interviewer','=',user.id),('technical_done','=',False)])
                if technical_applicants and len(technical_applicants) > 0:
                    technical_interviewer_ids.append(user.id)
        technical_interviewers = self.env['res.users'].browse(technical_interviewer_ids)
        ir_model_data = self.env['ir.model.data']
        template_id = ir_model_data.get_object_reference('technical_interviewer_ext', 'email_template_tech_notify')[1]
        for user in technical_interviewers:
            if user.partner_id.technical_interview_applications and len(user.partner_id.technical_interview_applications) > 0:
                self.env['mail.template'].browse(template_id).send_mail(user.id)
# ,('sel_groups_1_9_10','in',['1','9','10'])
    @api.onchange('stage_id')
    def check_interviewer(self):
        if self.job_category == 'operational':
            technical_stage = self.env['hr.recruitment.stage'].search([('job_category','=','operational'),('technical','=','true')])
            if technical_stage:
                if self.stage_id.sequence >= technical_stage.sequence and not self.technical_interviewer:
                    raise UserError(_('Please Select Technical Interviewer & Finish It'))
    technical_interviewer = fields.Many2one('res.users',domain="[('id','!=',0)]")

    second_interview_description = fields.Text('Second Interview Description')
    technical = fields.Boolean(compute="_compute_technical")
    technical_done = fields.Boolean(default=False)
    def _compute_technical(self):
        for this in self:
            if this.stage_id.technical:
                this.technical = True
            else:
                this.technical = False
