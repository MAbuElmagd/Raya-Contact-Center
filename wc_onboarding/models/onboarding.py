# -*- coding: utf-8 -*-

import json
import random
import uuid
import werkzeug
from random import randint

from odoo import api, fields, exceptions, models, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.exceptions import UserError
import re
from odoo.exceptions import AccessError
from odoo.osv import expression
from odoo.tools import is_html_empty
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError

AVAILABLE_PRIORITIES = [
    ('0', 'Normal'),
    ('1', 'Good'),
    ('2', 'Very Good'),
    ('3', 'Excellent')
]
class bulkonboarding(models.Model):
    _name='onboarding.bulk'

    name=fields.Char(string="Title",required=True)
    employees=fields.Many2many('hr.employee',string='Employees')
    user_id=fields.Many2one('res.users',compute='_compute_user',tracking=True, store=True, readonly=False)
    is_draft=fields.Boolean(default=True)
    is_in_progress=fields.Boolean(default=False)
    created=fields.Boolean(default=False)
    @api.depends('name')
    def _compute_user(self):
        for applicant in self:
            applicant.user_id = self.env.uid

    def start_onboarding(self):
        onboardings=self.env['onboarding.onboarding'].search([('bulk_id','=',self.id)])
        for onboarding in onboardings:
            onboarding.stage_id = self.env['onboarding.stage'].search([('in_progress','=',True)])[0].id
        self.is_draft=False
        self.is_in_progress=True

    def create_onboardings(self):
        self.created=True
        if self.employees:
            for employee in self.employees:
                plan_id=False
                if employee.job_id:
                    palns_positions = employee.env['onboarding.plans'].search([('application_on','=','position')])
                    if palns_positions:
                        for plan in palns_positions:
                            if plan.position_ids:
                                for value in plan.position_ids:
                                    if employee.job_id.id == value.id:
                                        plan_id=plan.id
                    palns_grades = employee.env['onboarding.plans'].search([('application_on','=','grade')])
                    if palns_grades:
                        for plan in palns_grades:
                            if plan.grade_ids:
                                for value in plan.grade_ids:
                                    if employee.job_id.employee_grade.id == value.id:
                                        plan_id=plan.id
                self.env['onboarding.onboarding'].create({
                    'name':self.name+" - "+employee.name,
                    'employee_id':employee.id,
                    'user_id' : employee.user_id.id,
                    'email' : employee.work_email,
                    'job_id' : employee.job_id.id,
                    'bulk_id':self.id,
                    'onboarding_plan':plan_id
                })
                self.env['onboarding.onboarding'].search([('name','=',self.name+" - "+employee.name,)]).update_checklist_data()

    # @api.model
    # def create(self, vals):
    #     res = super(bulkonboarding, self).create(vals)
    #     res.created=True
    #     if res.employees:
    #         for employee in res.employees:
    #             res.env['onboarding.onboarding'].create({
    #                 'name':res.name+" - "+employee.name,
    #                 'employee_id':employee.id,
    #                 'user_id' : employee.user_id.id,
    #                 'email' : employee.work_email,
    #                 'job_id' : employee.job_id.id,
    #                 'bulk_id':res.id
    #             })
    #     return res

    def unlink(self):
        for this in self:
            if this:
                raise UserError(
                    _('you can not delete this record.')
                )
        return super(bulkonboarding, self).unlink()

    def send_email(self):
        # self.ensure_one()

        ir_model_data = self.env['ir.model.data']
        onboardings=self.env['onboarding.onboarding'].search([('bulk_id','=',self.id)])
        template_id = ir_model_data.get_object_reference('wc_onboarding', 'email_template_onboarding')[1]
        for onboarding in onboardings:
            if onboarding.is_email:
                self.env['mail.template'].browse(template_id).send_mail(onboarding.id)
        
    def online_share(self):
        ir_model_data = self.env['ir.model.data']
        onboardings=self.env['onboarding.onboarding'].search([('bulk_id','=',self.id)])
        template_id = ir_model_data.get_object_reference('wc_onboarding', 'email_template_online_onboarding')[1]
        for onboarding in onboardings:
            if onboarding.is_online_share:
                self.env['mail.template'].browse(template_id).send_mail(onboarding.id)



class OnboardingOnboarding(models.Model):
    _name = 'onboarding.onboarding'
    _description = 'Raya Onboarding'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char()
    stage_id = fields.Many2one('onboarding.stage',string="Project", tracking=True,
                               compute='_compute_stage', store=True, readonly=False,copy=False, index=True,group_expand='_read_group_stage_ids')
    meeting_count = fields.Integer('Meeting',compute='_compute_meeting')

    is_shared=fields.Boolean(compute='compute_online_shared')
    bulk_id=fields.Many2one('onboarding.bulk')
    targeted_partners = fields.Many2many('res.partner','partner_ass_rel', compute="_compute_targeted_partners")

    def unlink(self):
        for this in self:
            if this.is_done:
                raise UserError(
                    _('you can not delete this record.')
                )
        return super(OnboardingOnboarding, self).unlink()

    def mass_send_email(self):
        for onboarding in self:
            if onboarding.is_in_progress:
                ir_model_data = self.env['ir.model.data']
                template_id = ir_model_data.get_object_reference('wc_onboarding', 'email_template_onboarding')[1]
                if onboarding.is_email:
                    self.env['mail.template'].browse(template_id).send_mail(onboarding.id)
        
    def mass_online_share(self):
        for onboarding in self:
            if onboarding.is_in_progress:
                ir_model_data = self.env['ir.model.data']
                template_id = ir_model_data.get_object_reference('wc_onboarding', 'email_template_online_onboarding')[1]
                if onboarding.is_online_share:
                    self.env['mail.template'].browse(template_id).send_mail(onboarding.id)

    @api.onchange('stage_id')
    def double_onboarding_check(self):
        for this in self:
            if this.is_in_progress:
                lines=this.env['onboarding.onboarding'].search([('employee_id','=',this.employee_id.id),('is_in_progress','=',True)])
                # for line in lines:
                if len(lines)>=1:
                    raise UserError(_('the same person can not have more than one onboarding in progress.'))

    @api.onchange('emp_id','manager')
    def _compute_targeted_partners(self):
        for this in self:
            this.targeted_partners = False
            ids = []
            ids.append(this.user_id.partner_id.id)
            if this.bulk_id:
                ids.append(this.bulk_id.user_id.partner_id.id)
            if len(ids) > 0:
                this.targeted_partners = [(6,0,ids)]
                
    def compute_online_shared(self):
        if self.is_online_share or self.is_grade_6 or self.is_options:
            self.is_shared=True
        else:
            self.is_shared=False

    @api.depends('meeting_id')
    def _compute_meeting(self):
        self.meeting_count = self.env['calendar.event'].search_count([('onboarding_id','=',self.id)])

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        search_domain = []
        stage_ids = self.env['onboarding.stage']._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return self.env['onboarding.stage'].browse(stage_ids)

    def _compute_stage(self):
        for applicant in self:
            if not applicant.stage_id:
                stage_ids = self.env['onboarding.stage'].search([()], order='sequence asc', limit=1).ids
                applicant.stage_id = stage_ids[0] if stage_ids else False

    employee_id = fields.Many2one('hr.employee')

    user_id = fields.Many2one(
        'res.users', "User", compute='_compute_user',
        tracking=True, store=True, readonly=False)
    
    @api.depends('name')
    def _compute_user(self):
        for applicant in self:
            applicant.user_id = applicant.job_id.user_id.id or self.env.uid

    email = fields.Char()
    job_id = fields.Many2one('hr.job')

    onboarding_plan = fields.Many2one('onboarding.plans')#,compute='update_onboarding_plan')

    # application_on = fields.Selection([('grade','Grade '),('position','Position')], related="onboarding_plan.application_on")
    # grade_ids = fields.Many2many('employee.grade','onboarding_grade_rel','onboarding_id','grade_id')
    # position_ids = fields.Many2many('hr.job','onboarding_position_rel','onboarding_id','position_id')

    is_grade_6 = fields.Boolean('Grade 6', related="onboarding_plan.is_grade_6")
    is_entry_checklist = fields.Boolean('Entry Checklist', related="onboarding_plan.is_entry_checklist")

    grade_6_ids = fields.One2many('g.checklist.clone.onboarding', 'onboard_onboarding_id')
    entry_checklist_ids = fields.One2many('entry.checklist.clone.onboarding', 'onboard_onboarding_id')


    is_meetings = fields.Boolean('Meetings', related="onboarding_plan.is_meetings")
    meetings_ids = fields.One2many('onboarding.meeting.clone.onboarding', 'onboard_onboarding_id')

    is_options = fields.Boolean('Options', related="onboarding_plan.is_options")
    options_ids = fields.One2many('onboarding.option.clone.onboarding', 'onboard_onboarding_id')

    is_email = fields.Boolean('Email', related="onboarding_plan.is_email")
    email_ids = fields.One2many('onboarding.email.clone.onboarding', 'onboard_onboarding_id')

    is_online_share = fields.Boolean('Online Share', related="onboarding_plan.is_online_share")
    online_share_ids = fields.One2many('onboarding.online.share.clone.onboarding', 'onboard_onboarding_id')


    attachment_number = fields.Integer(compute='_get_attachment_number', string="Number of Attachments")
    priority = fields.Selection(AVAILABLE_PRIORITIES, "Appreciation", default='0')

    is_draft = fields.Boolean(related="stage_id.draft")
    is_in_progress = fields.Boolean(related="stage_id.in_progress")
    is_done = fields.Boolean(related="stage_id.done")


    stage_id_new = fields.Many2one('onboarding.stage',  'Stage New', ondelete='restrict',store=True, readonly=False,
                               copy=False, index=True) # This custom field.
    stage_id_old = fields.Many2one('onboarding.stage',  'Stage Old', ondelete='restrict',store=True, readonly=False,
                               copy=False, index=True) # This custom field.


    meeting_id = fields.Many2one('calendar.event', string="Meeting", readonly=True)
    meeting_date=fields.Datetime('Meeting Date',compute='compute_meeting_date')

    def compute_meeting_date(self):
        line=self.env['calendar.event'].search([('id','=',self.meeting_id.id)])[-1]
        self.meeting_date=line.start

    def _get_attachment_number(self):
        read_group_res = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'hr.applicant'), ('res_id', 'in', self.ids)],
            ['res_id'], ['res_id'])
        attach_data = dict((res['res_id'], res['res_id_count']) for res in read_group_res)
        for record in self:
            record.attachment_number = attach_data.get(record.id, 0)

    def start_onboarding(self):
        for this in self:
            lines=this.env['onboarding.onboarding'].search([('employee_id','=',this.employee_id.id),('is_in_progress','=',True)])
            # for line in lines:
            if len(lines)>=1:
                raise UserError(_('the same person can not have more than one onboarding in progress.'))
            elif this.is_draft:
                this.stage_id = this.env['onboarding.stage'].search([('in_progress','=',True)])[0].id

    @api.onchange('employee_id')
    def update_user_data(self):
        if self.employee_id:
            self.user_id = self.employee_id.user_id.id
            self.email = self.employee_id.work_email
            self.job_id = self.employee_id.job_id.id

    @api.onchange('job_id')
    def update_onboarding_plan(self):
        for this in self:
            if this.job_id:
                this.onboarding_plan = False

                palns_positions = this.env['onboarding.plans'].search([('application_on','=','position')])
                if palns_positions:
                    for plan in palns_positions:
                        if plan.position_ids:
                            for value in plan.position_ids:
                                if this.job_id.id == value.id:
                                    this.onboarding_plan = plan


                palns_grades = this.env['onboarding.plans'].search([('application_on','=','grade')])
                if palns_grades:
                    for plan in palns_grades:
                        if plan.grade_ids:
                            for value in plan.grade_ids:
                                if this.job_id.employee_grade.id == value.id:
                                    this.onboarding_plan = plan
            if this.onboarding_plan:
                this.update_checklist_data()

    @api.onchange('onboarding_plan')
    def update_checklist_data(self):
        if self.onboarding_plan:
            self.grade_6_ids = [(5,0,0)]
            self.entry_checklist_ids = [(5,0,0)]
            self.meetings_ids = [(5,0,0)]
            self.options_ids = [(5,0,0)]
            self.email_ids = [(5,0,0)]
            self.online_share_ids = [(5,0,0)]

            if self.onboarding_plan.grade_6_ids:
                lines = []
                for line in self.onboarding_plan.grade_6_ids:
                    vals = (0, 0, {'name': line.name.id,})
                    lines.append(vals)

                self.grade_6_ids = lines

            if self.onboarding_plan.entry_checklist_ids:
                lines = []
                for line in self.onboarding_plan.entry_checklist_ids:
                    vals = (0, 0, {
                                    'name': line.name.id,
                                    'type':line.type,
                                    })
                    lines.append(vals)

                self.entry_checklist_ids = lines

            if self.onboarding_plan.meetings_ids:
                lines = []
                for line in self.onboarding_plan.meetings_ids:
                    vals = (0, 0, {
                                    'name': line.name,
                                    'description':line.description,
                                    })
                    lines.append(vals)

                self.meetings_ids = lines
            if self.onboarding_plan.options_ids:
                lines = []
                for line in self.onboarding_plan.options_ids:
                    vals = (0, 0, {
                                    'name': line.name,
                                    'description':line.description,
                                    })
                    lines.append(vals)

                self.options_ids = lines
            if self.onboarding_plan.email_ids:
                lines = []
                for line in self.onboarding_plan.email_ids:
                    vals = (0, 0, {
                                    'name': line.name,
                                    'type':line.type,
                                    'attachment':line.attachment,
                                    'url':line.url,
                                    })
                    lines.append(vals)

                self.email_ids = lines
            if self.onboarding_plan.online_share_ids:
                lines = []
                for line in self.onboarding_plan.online_share_ids:
                    vals = (0, 0, {
                                    'name': line.name,
                                    'type':line.type,
                                    'attachment':line.attachment,
                                    'url':line.url,
                                    })
                    lines.append(vals)

                self.online_share_ids = lines

    @api.onchange('stage_id')
    def entry_checklist_check(self):
        if self.stage_id.done:
            for value in self.grade_6_ids:
                if not value.done :
                    raise UserError(_('You must Finish all Grade 6 Checklist.'))
            for value in self.entry_checklist_ids:
                if not value.done :
                    raise UserError(_('You must Finish all Entry Checklists.'))

            for value in self.meetings_ids:
                if not value.done:
                    raise UserError(_('You must Finish all Meetings.'))

    def send_email(self):
        """
        This function opens a window to compose an email, with the template message loaded by default
        """

        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            """
            Find the email template that we've created in data/mail_template_data.xml
            get_object_reference first needs the module name where the template is build and then the name
            of the email template (the record id in XML).
            """
            template_id = ir_model_data.get_object_reference('wc_onboarding', 'email_template_onboarding')[1]
        except ValueError:
            template_id = False

        try:
            """
            Load the e-mail composer to show the e-mail template in
            """
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        attaches = []
        for value in self.email_ids:
            if value.attachment:
                attaches.append(value.attachment.id)
            print(value)
        for value in self.online_share_ids:
            if value.attachment:
                attaches.append(value.attachment.id)
        ctx = {
            'default_model': 'onboarding.onboarding',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'default_attachment_ids':[(6,0,attaches)],
            # 'default_partner_ids':[(6,0,self.targeted_partners.ids)],
            'force_email': True
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

    def online_share(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            """
            Find the email template that we've created in data/mail_template_data.xml
            get_object_reference first needs the module name where the template is build and then the name
            of the email template (the record id in XML).
            """
            template_id = ir_model_data.get_object_reference('wc_onboarding', 'email_template_online_onboarding')[1]
        except ValueError:
            template_id = False

        try:
            """
            Load the e-mail composer to show the e-mail template in
            """
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'onboarding.onboarding',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'force_email': True
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




    @api.model
    def create(self, vals):
        stage = self.env['onboarding.stage'].search([('draft','=',True)])[0].id
        vals['stage_id'] = stage

        res = super(OnboardingOnboarding, self).create(vals)
        return res


class OnboardingStage(models.Model):
    _name = 'onboarding.stage'
    _description = 'Raya Onboarding Stage'

    name = fields.Char()
    sequence = fields.Integer()

    draft = fields.Boolean('Draft')
    in_progress = fields.Boolean('In Progress')
    done = fields.Boolean('Done')
    requirements = fields.Text("Requirements")

    @api.constrains('draft')
    def _constrains_onboarding_draf_stage(self):
        for rec in self:
            stager = self.search([('draft', '=', True),
                                   ('id', '!=', rec.id)])
            if stager and rec.draft:
                raise UserError(
                    _('there is one Draft stage overall')
                )
    @api.onchange('draft')
    def check_draft(self):
        if self.draft:

            drafts = self.env['onboarding.stage'].search([('draft','=',True)])
            if len(drafts) > 1:
                self.draft = False
                return {
                        'warning': {'title': _('ValidationError'),
                                    'message': _('There is another draft.'),
                                    },
                        }


    @api.onchange('done')
    def check_done(self):
        if self.done:

            drafts = self.env['onboarding.stage'].search([('done','=',True)])
            if len(drafts) > 0:
                self.done = False
                return {
                        'warning': {'title': _('ValidationError'),
                                    'message': _('There is another done.'),
                                    },
                        }


    @api.model
    def create(self, vals):
        res = super(OnboardingStage, self).create(vals)

        if res.draft:
            if res.in_progress:
                raise ValidationError(_('You can only do one check.'))
            elif res.done:
                raise ValidationError(_('You can only do one check.'))
        elif res.in_progress:
            if res.draft:
                raise ValidationError(_('You can only do one check.'))
            elif res.done:
                raise ValidationError(_('You can only do one check.'))
        elif res.done:
            if res.in_progress:
                raise ValidationError(_('You can only do one check.'))
            elif res.draft:
                raise ValidationError(_('You can only do one check.'))

        return res

    def write(self, vals):
        res = super(OnboardingStage, self).write(vals)

        if self.draft:
            if self.in_progress:
                raise ValidationError(_('You can only do one check.'))
            elif self.done:
                raise ValidationError(_('You can only do one check.'))
        elif self.in_progress:
            if self.draft:
                raise ValidationError(_('You can only do one check.'))
            elif self.done:
                raise ValidationError(_('You can only do one check.'))
        elif self.done:
            if self.in_progress:
                raise ValidationError(_('You can only do one check.'))
            elif self.draft:
                raise ValidationError(_('You can only do one check.'))

        return res

class Onboarding(models.Model):
    _name = 'onboarding.checklists'
    _description = 'Raya Onboarding Checklists'

    name = fields.Char(required=True)
    is_grade_6 = fields.Boolean('Grade 6')
    is_entry_checklist = fields.Boolean('Entry Checklist')

    grade_6_ids = fields.One2many('g.checklist','onboard_checklist_id')
    entry_checklist_ids = fields.One2many('entry.checklist','onboard_checklist_id')


class Onboarding(models.Model):
    _name = 'g.checklist'
    _description = 'Raya G6 Checklist'

    name = fields.Many2one('g.description', required=True)
    onboard_checklist_id = fields.Many2one('onboarding.checklists')

class Onboarding(models.Model):
    _name = 'g.description'
    _description = 'Raya G6 Description'

    name = fields.Char(required=True)

class Onboarding(models.Model):
    _name = 'entry.checklist'
    _description = 'Raya Entry Checklist'

    name = fields.Many2one('entry.checklist.description', required=True)
    type = fields.Selection([('action','Action'),('giving','Giving'),('custody','Custody')], required=True)
    onboard_checklist_id = fields.Many2one('onboarding.checklists')

class Onboarding(models.Model):
    _name = 'entry.checklist.description'
    _description = 'Raya Entry Checklist Description'

    name = fields.Char(required=True)

class Onboarding(models.Model):
    _name = 'g.checklist.clone'
    _description = 'Raya G6 Checklist Clone'

    name = fields.Many2one('g.description', required=True)
    onboard_plans_id = fields.Many2one('onboarding.plans')

class Onboarding(models.Model):
    _name = 'entry.checklist.clone'
    _description = 'Raya Entry Checklist Clone'

    name = fields.Many2one('entry.checklist.description', required=True)
    type = fields.Selection([('action','Action'),('giving','Giving'),('custody','Custody')], required=True)
    onboard_plans_id = fields.Many2one('onboarding.plans')


class Onboarding(models.Model):
    _name = 'g.checklist.clone.onboarding'
    _description = 'Raya G6 Checklist Clone'

    name = fields.Many2one('g.description', required=True)
    done = fields.Boolean()
    onboard_onboarding_id = fields.Many2one('onboarding.onboarding')

class Onboarding(models.Model):
    _name = 'entry.checklist.clone.onboarding'
    _description = 'Raya Entry Checklist Clone'

    name = fields.Many2one('entry.checklist.description', required=True)
    type = fields.Selection([('action','Action'),('giving','Giving'),('custody','Custody')], required=True)
    done = fields.Boolean()
    onboard_onboarding_id = fields.Many2one('onboarding.onboarding')



class Onboarding(models.Model):
    _name = 'onboarding.plans'
    _description = 'Raya Onboarding Plans'

    name = fields.Char(required=True)
    application_on = fields.Selection([('grade','Grade '),('position','Position')], required=True, default='grade')

    grade_ids = fields.Many2many('employee.grade','plans_grade_rel','plans_id','grade_id')
    position_ids = fields.Many2many('hr.job','plans_position_rel','plans_id','position_id')

    checklists = fields.Many2one('onboarding.checklists')

    is_grade_6 = fields.Boolean('Grade 6', related="checklists.is_grade_6")
    is_entry_checklist = fields.Boolean('Entry Checklist', related="checklists.is_entry_checklist")

    grade_6_ids = fields.One2many('g.checklist.clone','onboard_plans_id')
    entry_checklist_ids = fields.One2many('entry.checklist.clone','onboard_plans_id')

    is_meetings = fields.Boolean('Meetings')
    meetings_ids = fields.One2many('onboarding.meeting' , 'onboard_plans_id')

    is_options = fields.Boolean('Options')
    options_ids = fields.One2many('onboarding.option', 'onboard_plans_id')

    is_email = fields.Boolean('Email')
    email_ids = fields.One2many('onboarding.email', 'onboard_plans_id')

    is_online_share = fields.Boolean('Online Share')
    online_share_ids = fields.One2many('onboarding.online.share', 'onboard_plans_id')


    @api.onchange('checklists')
    def update_g6_entry(self):
        if self.checklists:
            self.entry_checklist_ids = [(5,0,0)]
            self.grade_6_ids = [(5,0,0)]

            if self.checklists.grade_6_ids:
                lines = []
                for line in self.checklists.grade_6_ids:
                    vals = (0, 0, {'name': line.name,})
                    lines.append(vals)

                self.grade_6_ids = lines

            if self.checklists.entry_checklist_ids:
                lines = []
                for line in self.checklists.entry_checklist_ids:
                    vals = (0, 0, {
                                    'name': line.name,
                                    'type':line.type,
                                    })
                    lines.append(vals)

                self.entry_checklist_ids = lines


class Onboarding(models.Model):
    _name = 'onboarding.meeting'
    _description = 'Raya Onboarding Plans Meetings'

    name = fields.Char('Subject', required=True)
    description = fields.Text()
    onboard_plans_id = fields.Many2one('onboarding.plans')

class Onboarding(models.Model):
    _name = 'onboarding.option'
    _description = 'Raya Onboarding Plans Options'

    name = fields.Char('Option', required=True)
    description = fields.Text()
    onboard_plans_id = fields.Many2one('onboarding.plans')

class Onboarding(models.Model):
    _name = 'onboarding.email'
    _description = 'Raya Onboarding Plans Options'

    name = fields.Char('Name', required=True)
    type = fields.Selection([('document','Document'),('video','Video')],default='document', required=True)
    attachment = fields.Many2many(comodel_name="ir.attachment",
                                relation="m2m_ir_mails_attach_rel",
                                column1="m2m_id",
                                column2="attachment_id",)
    url = fields.Char()
    onboard_plans_id = fields.Many2one('onboarding.plans')
    
    @api.constrains('attachment')
    def _constrains_onboarding_email_attachment(self):
        attaches = self.search([('type', '=', 'document')])
        if len(attaches.attachment)==0:
            raise UserError(
                _('You should add an attachment to the email record')
            )

    @api.onchange('type')
    def validation_type(self):
        if self.type:
            self.attachment = [(5,0,0)]
            self.url = ""

class Onboarding(models.Model):
    _name = 'onboarding.online.share'
    _description = 'Raya Onboarding Plans Online Share'

    name = fields.Char('Name', required=True)
    type = fields.Selection([('document','Document'),('video','Video')],default='document', required=True)
    attachment = fields.Many2many(comodel_name="ir.attachment",
                                relation="m2m_ir_online_share_attach_rel",
                                column1="m2m_id",
                                column2="attachment_id",)
    url = fields.Char()
    onboard_plans_id = fields.Many2one('onboarding.plans')

    @api.onchange('type')
    def validation_type(self):
        if self.type:
            self.attachment = [(5,0,0)]
            self.url = ""

    @api.constrains('attachment')
    def _constrains_onboarding_email_attachment(self):
        attaches = self.search([('type', '=', 'document')])
        if len(attaches.attachment)==0:
            raise UserError(
                _('You should add an attachment to the email record')
            )


class OnboardingMeetingClone(models.Model):
    _name = 'onboarding.meeting.clone.onboarding'
    _description = 'Raya Onboarding Plans Meetings'

    name = fields.Char('Subject', required=True)
    description = fields.Text()
    date = fields.Datetime()
    done = fields.Boolean()
    onboard_onboarding_id = fields.Many2one('onboarding.onboarding')

class CalenderEvent(models.Model):
    _inherit = 'calendar.event'
    onboarding_id = fields.Many2one('onboarding.onboarding', string="Task", readonly=True)

    @api.depends('onboarding_id')
    def _compute_onboarding_meeting(self):
        self.task_count = self.env['onboarding.onboarding'].search_count([('meeting_id','=',self.id)])

class MeetingDate(models.TransientModel):
    _name = 'onboarding_meeting.date'
    _description = "Create Meeting for onboarding"

    start_date = fields.Datetime('Meeting Date', required=True)

    def get_data(self):
        meeting_obj= self.env['onboarding.meeting.clone.onboarding'].browse(self._context.get('active_ids'))
        meeting_obj.date=self.start_date
        meeting_obj=meeting_obj.onboard_onboarding_id.id
        task_obj= self.env['onboarding.onboarding'].search([('id','=',meeting_obj)])
        calendar_obj = self.env['calendar.event'].create({
        'name':"Meeting from : "+task_obj.name ,
        'start':str(self.start_date),
        'duration':1,
        'stop':self.start_date + timedelta(hours=1),
        'onboarding_id':task_obj.id,
        'partner_ids':[(6,0,task_obj.targeted_partners.ids)],
        'res_model':'onboarding.onboarding',
        'res_model_id':self.env['ir.model'].search([('model','=','onboarding.onboarding')]).id,
        'res_id':task_obj.id
         })
        task_obj.write({'meeting_id':calendar_obj.id})

class OnboardingOptionClone(models.Model):
    _name = 'onboarding.option.clone.onboarding'
    _description = 'Raya Onboarding Plans Options'

    name = fields.Char('Option', required=True)
    description = fields.Text()
    select = fields.Boolean()
    onboard_onboarding_id = fields.Many2one('onboarding.onboarding')

class OnboardingEmailClone(models.Model):
    _name = 'onboarding.email.clone.onboarding'
    _description = 'Raya Onboarding Plans Options'

    name = fields.Char('Name', required=True)
    type = fields.Selection([('document','Document'),('video','Video')], required=True)
    attachment = fields.Many2many(comodel_name="ir.attachment",
                                relation="m2m_ir_mails_attach_clon_rel",
                                column1="m2m_id",
                                column2="attachment_id",)
    url = fields.Char()
    onboard_onboarding_id = fields.Many2one('onboarding.onboarding')

class OnboardingOnlineShareClone(models.Model):
    _name = 'onboarding.online.share.clone.onboarding'
    _description = 'Raya Onboarding Plans Online Share'

    name = fields.Char('Name', required=True)
    type = fields.Selection([('document','Document'),('video','Video')], required=True)
    attachment = fields.Many2many(comodel_name="ir.attachment",
                                relation="m2m_ir_online_share_attach_clon_rel",
                                column1="m2m_id",
                                column2="attachment_id",)
    url = fields.Char()
    onboard_onboarding_id = fields.Many2one('onboarding.onboarding')
