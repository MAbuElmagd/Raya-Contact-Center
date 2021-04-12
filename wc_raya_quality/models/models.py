# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError,UserError

class Partner(models.Model):
    _inherit = "res.partner"

    quality_hold_applications = fields.Many2many('hr.applicant','partner_user_applicant_rel','partner_id','applicant_id', compute="_compute_hold_applicants")
    def _compute_hold_applicants(self):
        for this in self:
            this.quality_hold_applications = False
            partner_user = self.env['res.users'].search([('partner_id','=',this.id)])
            if partner_user and len(partner_user) > 0:
                if partner_user.has_group('wc_raya_quality.system_hr_recruitment_quality_team'):
                    hold_applicants = self.env['hr.applicant'].search([('quality_hold','=',True)])
                    if hold_applicants and len(hold_applicants) > 0:
                        this.quality_hold_applications = [(6,0,hold_applicants.ids)]

class PositionHold(models.Model):
    _inherit = "hr.job"
    quality_hold = fields.Boolean()

class MailTemplate(models.Model):
    _inherit = "mail.template"

    quality_hold_notification = fields.Boolean()
    @api.constrains('quality_hold_notification')
    def _constrains_quality_hold_notification(self):
        for rec in self:
            mail = self.search([('quality_hold_notification', '=', True),
                                   ('id', '!=', rec.id)])
            if mail and rec.quality_hold_notification:
                raise UserError(
                    _('Quality Hold Notification Template Already Marked in %s.' % mail.name)
                )

class ApplicantRefuseReason(models.Model):
    _inherit = "hr.applicant"

    def notify_quality_hold(self):
        ta_quality_team = self.env.ref('wc_raya_quality.system_hr_recruitment_quality_team').users
        ir_model_data = self.env['ir.model.data']
        template_id = ir_model_data.get_object_reference('wc_raya_quality', 'email_template_quality_hold_notify')[1]
        for user in ta_quality_team:
            if user.partner_id.quality_hold_applications and len(user.partner_id.quality_hold_applications) > 0:
                self.env['mail.template'].browse(template_id).send_mail(user.id)

    quality_hold= fields.Boolean('Quality Hold', default=False, track_visibility="onchange")
    def quality_hold_release(self):
        self.quality_hold=False
    @api.onchange('emp_id','job_id')
    def check_quality_hold(self):
         for this in self:
             print("###################################################")
             print(this)
             print(this.job_id)
             print(this.job_id.quality_hold)
             print(this.emp_id)
             print("###################################################")
             if this.job_id and this.job_id.quality_hold and this.emp_id:
                 this.quality_hold=True

    @api.onchange('stage_id')
    def check_stage_hold(self):
        if self.job_category=='talent':
            stage_line=self.env['hr.recruitment.stage'].search([('job_category','=','talent'),('is_initial','=',True)],limit=1)
            if self.quality_hold==True and not self.stage_id.id == stage_line.id:
                raise ValidationError('This applicant currently on Quality Hold')
