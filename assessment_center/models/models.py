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

class AssessmentDocs(models.Model):
    _name = 'assessment.docs'
    _description = 'Asseessment Docs'

    name = fields.Char('Name', required=True)
    attachment = fields.Many2many(comodel_name="ir.attachment",
                                relation="m2m_ir_docs_attach_rel",
                                column1="m2m_id",
                                column2="attachment_id",)
    assessment_center_id = fields.Many2one('assessment_center.assessment_center')

    @api.onchange('doc_type')
    def validation_doc_type(self):
        if self.doc_type:
            self.attachment = [(5,0,0)]
            self.url = ""

class Templates(models.Model):
    _name = 'templates'
    _description = "Templates"

    name  = fields.Char('Name', required=True)
    attachement = fields.Many2many(comodel_name="ir.attachment",
                                relation="m2m_ir_attachement_rel",
                                column1="m2m_id",
                                column2="attachment_id",
                                string="Attachement")

    def write(self, vals):
        res = super(Templates, self).write(vals)
        if len(self.attachement) > 1:
            raise UserError(_('You can only upload one attachement !'))
        return res

class HrJob(models.Model):
    _inherit = 'hr.job'

    has_assessment = fields.Boolean(string="Has Assessment")
    grade_has_assessment = fields.Boolean(compute="get_has_assessment")

    @api.onchange('employee_grade')
    def get_has_assessment(self):
        for this in self:
            this.grade_has_assessment = False
            if this.employee_grade:
                if this.employee_grade.has_assessment:
                    this.grade_has_assessment = True

class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    assessment_id = fields.Many2one('assessment_center.assessment_center', 'Assessment')

    def get_assessment_start_url(self):
        self.ensure_one()
        if self.assessment_id:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            for invite in self:
                return werkzeug.urls.url_join(base_url, invite.survey_id.get_start_url()) + '?ass_id='+str(self.assessment_id.id)
        else:
            return '%s?answer_token=%s' % (self.survey_id.get_start_url(), self.access_token)

class MailActivity(models.Model):
    _inherit = 'mail.activity'

    def action_create_calendar_event(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("calendar.action_calendar_event")
        action['context'] = {
            'default_activity_type_id': self.activity_type_id.id,
            'default_res_id': self.env.context.get('default_res_id'),
            'default_res_model': self.env.context.get('default_res_model'),
            'default_name': self.summary or self.res_name,
            'default_description': self.note and tools.html2plaintext(self.note).strip() or '',
            'default_activity_ids': [(6, 0, self.ids)],
        }
        active_id = self.env.context.get('default_res_id')
        active_model = self.env.context.get('default_res_model')
        if active_model == 'assessment_center.assessment_center' and active_id:
            rec = self.env[active_model].browse(active_id)
            action['context'] = {
                'default_activity_type_id': self.activity_type_id.id,
                'default_res_id': self.env.context.get('default_res_id'),
                'default_res_model': self.env.context.get('default_res_model'),
                'default_name': self.summary or self.res_name,
                'default_description': self.note and tools.html2plaintext(self.note).strip() or '',
                'default_activity_ids': [(6, 0, self.ids)],
                'default_assign_to':rec.assign_to.id,
                'default_assessment_id':rec.id,
            }
        return action

class assessment_center(models.Model):
    _name = 'assessment_center.assessment_center'
    _description = 'Assessant'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin', 'utm.mixin']

    readonly_user = fields.Boolean(default=False, compute="_compute_readonly_user")

    def _compute_readonly_user(self):
        for this in self:
            flag = self.env.user.has_group('assessment_center.group_assessment_viewer')
            if flag:
                this.readonly_user = True
            else:
                this.readonly_user = False

    def domain_assign_to(self):
        users = self.env.ref('assessment_center.group_assessment_team').users
        return [('id','in',users.ids)]

    assign_to=fields.Many2one('res.users', "Assessment Responsible",domain=domain_assign_to, copy=False)
    name=fields.Char(string="Assessment's Name",required=True)

    def app_name_doamin(self):
        apps=[]
        lines=self.env['hr.applicant'].search([])
        for line in lines:
            if line.has_assessment ==True and line.is_shortlisting_assessment:
                apps.append(line.id)
        return [('id', 'in', apps)]

    dos_ids = fields.One2many('assessment.docs', 'assessment_center_id', string="Documents")
    app_name=fields.Many2one('hr.applicant',string="Application",required=True,force_save=True,domain=app_name_doamin)
    partner_id = fields.Many2one('res.partner', "Applicant Name", copy=False)
    active = fields.Boolean("Active", default=True, help="If the active field is set to false, it will allow you to hide the case without removing it.")
    mobile=fields.Char(string="Mobile")
    email=fields.Char(string="Email")
    job_id =fields.Many2one('hr.job',string="Job Position")
    department_id = fields.Many2one('hr.department',string="Department")
    project = fields.Many2one('rcc.project',string="Project")
    has_assessment_test=fields.Boolean(string="Assessment Test")
    emp_id = fields.Many2one('hr.employee',string="Employee Name")
    hr_id=fields.Char(string="HR ID")
    manager = fields.Many2one('hr.employee',string="Employee Manager")
    manager_email=fields.Char(string="Manager Email")
    emp_project=fields.Many2one('rcc.project',string="Employee Project")
    stage_id = fields.Many2one('assessment_center.stage', 'Stage', ondelete='restrict', tracking=True,
                               compute='_compute_stage', store=True, readonly=False,
                               copy=False, index=True,
                               group_expand='_read_group_stage_ids')

    attachements = fields.Many2many(comodel_name="ir.attachment",
                                relation="m2m_ir_attachements_rel",
                                column1="m2m_id",
                                column2="attachments_id",
                                string="Attachements")
    templates_ids = fields.Many2many("templates",string="Templates")

    @api.onchange('stage_id')
    def check_assign(self):
        if self.assign_to==False:
            raise exceptions.UserError(_('You cannot go to the next stage without adding Assign To.'))
        
    answer_id = fields.Many2one('survey.user_input')
    # , compute="_compute_answer_id"
    # def _compute_answer_id(self):
    #     for this in self:
    #         this.answer_id = False
    #         if this.assessment_test:
    #             answers = self.env['survey.user_input'].search([('survey_id','=',this.assessment_test.id),('assessment_id','=',this.id),('state','=','done')])
    #             if len(answers) == 1:
    #                 this.answer_id = answers.id

    def action_survey_user_input_completed(self):
        action = self.env['ir.actions.act_window']._for_xml_id('survey.action_survey_user_input')
        action['res_id'] = self.answer_id.id
        res = self.env.ref('survey.survey_user_input_view_form', False)
        form_view = [(res and res.id or False, 'form')]
        if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
        else:
            action['views'] = form_view
        return action

    score=fields.Float(string="Score (%)", compute="_compute_score")
    def _compute_score(self):
        for this in self:
            this.score = this.answer_id.scoring_percentage or 0.00

    assessment_test=fields.Many2one('survey.survey', string="Assessment Test",domain="[('assessment_test','=',True)]")
    meeting_location=fields.Selection([('on','Online'),('off','Offline')],string="Meeting Location") # radio widget
    final_result=fields.Selection([('accepted','Accepted'),('refused','Not Accepted')],string="Final Result")
    assessment_report=fields.Many2many(comodel_name="ir.attachment",
                                relation="m2m_ir_assessment_report_rel",
                                column1="m2m_id",
                                column2="attachments_id", string="Assessment Report")

    @api.constrains('assessment_report')
    def constrain_assessment_test(self):
        if len(self.assessment_report) > 1 :
                raise UserError(_('You can only upload one Assessment Report !'))

    date_last_stage_update = fields.Datetime("Last Stage Update", index=True, default=fields.Datetime.now)
    last_stage_id = fields.Many2one('hr.recruitment.stage', "Last Stage",
                                    help="Stage of the applicant before being in the current stage. Used for lost cases analysis.")
    legend_blocked = fields.Char(related='stage_id.legend_blocked', string='Kanban Blocked')
    legend_done = fields.Char(related='stage_id.legend_done', string='Kanban Valid')
    legend_normal = fields.Char(related='stage_id.legend_normal', string='Kanban Ongoing')
    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'assessment_center.assessment_center')], string='Attachments')
    draft=fields.Boolean(compute="check_stage_state")
    in_progress=fields.Boolean(compute="check_stage_state")
    done=fields.Boolean(compute="check_stage_state")

    @api.onchange('stage_id')
    def check_assessment_test(self):
        if self.stage_id and not self.assessment_test and self.has_assessment_test:
            raise UserError(_('You should choose Assessment Test'))
        
    @api.onchange('stage_id.id')
    def check_stage_state(self):
        self.draft=self.stage_id.draft
        self.in_progress=self.stage_id.in_progress
        self.done=self.stage_id.done

    kanban_state = fields.Selection([
        ('normal', 'Grey'),
        ('done', 'Green'),
        ('blocked', 'Red')], string='Kanban State',
        copy=False, default='normal', required=True)
    color = fields.Integer("Color Index", default=0)
    priority = fields.Selection(AVAILABLE_PRIORITIES, "Appreciation", default='0')
    user_id = fields.Many2one(
        'res.users', "Assessant", compute='_compute_user',
        tracking=True, store=True, readonly=False)
    user_email = fields.Char(related='user_id.email', string="User Email", readonly=True)
    attachment_number = fields.Integer(compute='_get_attachment_number', string="Number of Attachments")

    def send_final_report(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            """
            Find the email template that we've created in data/mail_template_data.xml
            get_object_reference first needs the module name where the template is build and then the name
            of the email template (the record id in XML).
            """
            template_id = ir_model_data.get_object_reference('assessment_center', 'email_template_final_report')[1]
        except ValueError:
            template_id = False

        try:
            """
            Load the e-mail composer to show the e-mail template in
            """
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False

        else:
            ir_attachements_ids = []
            for att in self.assessment_report:
                ir_attachements_ids.append(att.id)
            # for temp in self.templates_ids:
            #     ir_attachements_ids.append(temp.attachement.id)

            ctx = {
                'default_model': 'assessment_center.assessment_center',
                'default_res_id': self.ids[0],
                'default_use_template': bool(template_id),
                'default_template_id': template_id,
                'default_composition_mode': 'comment',
                'default_attachment_ids':[(6,0,ir_attachements_ids)],
                'default_partner_ids':[(6,0,self.targeted_partners.ids)],
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

    def action_send_survey(self):
        """ Open a window to compose an email, pre-filled with the survey message """
        # Ensure that this survey has at least one page with at least one question.
        if (not self.assessment_test.page_ids and self.assessment_test.questions_layout == 'page_per_section') or not self.assessment_test.question_ids:
            raise exceptions.UserError(_('You cannot send an invitation for a survey that has no questions.'))

        if self.assessment_test.state == 'closed':
            raise exceptions.UserError(_("You cannot send invitations for closed surveys."))

        template = self.env.ref('assessment_center.mail_template_user_input_invite', raise_if_not_found=False)

        local_context = dict(
            self.env.context,
            default_survey_id=self.assessment_test.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_partner_ids=[(6,0,[self.app_name.partner_id.id])],
            notif_layout='mail.mail_notification_light',
            default_assessment_id=self.id,
        )
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'assessment_test_invite',
            'target': 'new',
            'context': local_context,
        }

    @api.onchange('app_name')
    def check_data(self):
            line=self.env['hr.applicant'].search([('name','=',self.app_name.name)], limit=1)
            self.partner_id=line.partner_id
            self.mobile=line.partner_phone
            self.email=line.email_from
            self.job_id=line.job_id.id
            self.department_id=line.department_id.id
            self.project=line.project.id
            self.hr_id=line.emp_id.hr_id
            if line.manager.id!=False:
                self.manager=line.manager.id
                self.manager_email=line.manager.work_email
            if line.emp_id.id!=False:
                self.emp_id=line.emp_id.id
                line2=self.env['hr.employee'].search([('name','=',self.emp_id.name)], limit=1)
                self.emp_project=line2.project.id
            self.assign_to=self.env.user.id

    @api.depends('name')
    def _compute_user(self):
        for applicant in self:
            applicant.user_id = applicant.job_id.user_id.id or self.env.uid

    def _get_attachment_number(self):
        read_group_res = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'assessment_center.assessment_center'), ('res_id', 'in', self.ids)],
            ['res_id'], ['res_id'])
        attach_data = dict((res['res_id'], res['res_id_count']) for res in read_group_res)
        for record in self:
            record.attachment_number = attach_data.get(record.id, 0)

    meeting_id = fields.Many2one('calendar.event', string="Meeting", readonly=True)
    meeting_count = fields.Integer('Meeting',compute='_compute_meeting')
    meeting_date=fields.Datetime('Meeting Date',compute='compute_meeting_date')

    targeted_partners = fields.Many2many('res.partner','partner_ass_rel', compute="_compute_targeted_partners")
    @api.onchange('emp_id','manager')
    def _compute_targeted_partners(self):
        for this in self:
            this.targeted_partners = False
            ids = []
            ids.append(this.app_name.partner_id.id)
            if this.assign_to.partner_id.id:
                ids.append(this.assign_to.partner_id.id)
            if len(ids) > 0:
                this.targeted_partners = [(6,0,ids)]

    def compute_meeting_date(self):
        line=self.env['calendar.event'].search([('id','=',self.meeting_id.id)])[-1]
        self.meeting_date=line.start

    @api.depends('meeting_id')
    def _compute_meeting(self):
        self.meeting_count = self.env['calendar.event'].search_count([('task_id','=',self.id)])

    def action_send_assessment_meeting_email(self):
        """
        This function opens a window to compose an email, with the Schaduled Assessment Meeting template message loaded by default
        """
        self._compute_targeted_partners()
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            """
            Find the email template that we've created in data/mail_template_data.xml
            get_object_reference first needs the module name where the template is build and then the name
            of the email template (the record id in XML).
            """
            template_id = ir_model_data.get_object_reference('assessment_center', 'email_template_assessment_meeting')[1]
        except ValueError:
            template_id = False

        try:
            """
            Load the e-mail composer to show the e-mail template in
            """
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False

        else:
            ir_attachements_ids = []
            for att in self.attachements:
                ir_attachements_ids.append(att.id)
            for temp in self.templates_ids:
                ir_attachements_ids.append(temp.attachement.id)

            ctx = {
                'default_model': 'assessment_center.assessment_center',
                'default_res_id': self.ids[0],
                'default_use_template': bool(template_id),
                'default_template_id': template_id,
                'default_composition_mode': 'comment',
                'default_attachment_ids':[(6,0,ir_attachements_ids)],
                'default_partner_ids':[(6,0,self.targeted_partners.ids)],
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

    def action_print_answers(self):
        """ Open the website page with the survey form """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'name': "View Answers",
            'target': 'self',
            'url': '/survey/print/%s?answer_token=%s' % (self.assessment_test.access_token, self.answer_id.access_token)
        }

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):

        search_domain = []

        stage_ids = self.env['assessment_center.stage']._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return self.env['assessment_center.stage'].browse(stage_ids)

    def _compute_stage(self):
        for applicant in self:
            if not applicant.stage_id:
                stage_ids = self.env['assessment_center.stage'].search([
                    ('fold', '=', False)
                ], order='sequence asc', limit=1).ids
                applicant.stage_id = stage_ids[0] if stage_ids else False

    @api.model
    def create(self, vals):
        res = super(assessment_center, self).create(vals)
        result_new=[]
        existing_documents = self.env['ir.attachment'].search([('res_model', '=', 'hr.applicant'),('res_id','=', res.app_name.id)])
        for attaches in existing_documents:
            hoh1 = (0, 0, {'name': attaches.name ,'res_name': self.name,'type': 'binary','datas': attaches.datas,'res_model': 'assessment_center.assessment_center','res_id': self.id,})
            result_new.append(hoh1)
        res.update({'attachment_ids': result_new})
        res.stage_id=self.env['assessment_center.stage'].search([('draft','=',True)])
        return res

    def write(self, vals):
        if vals.get('user_id'):
            vals['date_open'] = fields.Datetime.now()
        if vals.get('email_from'):
            vals['email_from'] = vals['email_from'].strip()
        # stage_id: track last stage before update
        if 'stage_id' in vals:
            vals['date_last_stage_update'] = fields.Datetime.now()
            if 'kanban_state' not in vals:
                vals['kanban_state'] = 'normal'
            for applicant in self:
                vals['last_stage_id'] = applicant.stage_id.id
                res = super(assessment_center, self).write(vals)
        else:
            res = super(assessment_center, self).write(vals)
        return res

    def unlink(self):
        for this in self:
            if this.done:
                raise UserError(
                    _('you can not delete this record.')
                )
            if this.answer_id:
                raise UserError(
                    _('you can not delete this record(Delete connected Answer First).')
                )
        return super(assessment_center, self).unlink()

class stage(models.Model):
    _name = 'assessment_center.stage'
    _description = 'Assessment Center stages'
    _order = 'sequence'

    name = fields.Char("Stage Name", required=True, translate=True)
    sequence = fields.Integer(
        "Sequence", default=10,
        help="Gives the sequence order when displaying a list of stages.")
    requirements = fields.Text("Requirements")
    template_id = fields.Many2one('mail.template', "Email Template",)
    fold = fields.Boolean("Folded in Kanban")
    legend_blocked = fields.Char(
        'Red Kanban Label', default=lambda self: _('draft'), translate=True, required=True)
    legend_done = fields.Char(
        'Green Kanban Label', default=lambda self: _('Done'), translate=True, required=True)
    legend_normal = fields.Char(
        'Grey Kanban Label', default=lambda self: _('In Progress'), translate=True, required=True)
    draft=fields.Boolean(string="Draft",default=False)
    in_progress=fields.Boolean(string="In progress",default=False)
    done=fields.Boolean(string="Done",default=False)

class Survey(models.Model):
     _inherit = 'survey.survey'

     assessment_test=fields.Boolean(string='Assessment Test')

class HrEmployeePrivate(models.Model):
    _inherit = "hr.employee"

    assessment_count=fields.Integer(string='Assessments', compute='_compute_assessment')

    def _compute_assessment(self):
        for this in self:
            this.assessment_count=self.env['assessment_center.assessment_center'].search_count([('emp_id', '=', this.id)])
    def action_open_assessments(self):
        self.ensure_one()
        return {
        'type': 'ir.actions.act_window',
        'name': 'Assissments',
        'view_mode': 'tree',
        'res_model': 'assessment_center.assessment_center',
        'domain': [('emp_id.id', '=', self.id)],
        'context': "{'create': False}"
        }

class CalenderEvent(models.Model):
    _inherit = 'calendar.event'

    task_id = fields.Many2one('assessment_center.assessment_center', string="Task", readonly=True)
    assessment_id = fields.Many2one('assessment_center.assessment_center',string="Assessment")
    task_count = fields.Integer('Assessments', compute='_compute_task',)

    assign_to=fields.Many2one('res.users', "Assessment Responsible", copy=False)


    @api.depends('task_id')
    def _compute_task(self):
        self.task_count = self.env['assessment_center.assessment_center'].search_count([('meeting_id','=',self.id)])

class MeetingDate(models.TransientModel):
    _name = 'meeting.date'
    _description = "Create Meeting from Task"

    start_date = fields.Datetime('Meeting Date', required=True)

    def get_data(self):
        task_obj= self.env['assessment_center.assessment_center'].browse(self._context.get('active_ids'))
        calendar_obj = self.env['calendar.event'].create({
        'name':"Meeting from : "+task_obj.name ,
        'start':str(self.start_date),
        'duration':1,
        'stop':self.start_date + timedelta(hours=1),
        'task_id':task_obj.id,
        'assessment_id':task_obj.id,
        'partner_ids':[(6,0,task_obj.targeted_partners.ids)],
        'assign_to':task_obj.assign_to.id,
         })
        task_obj.write({'meeting_id':calendar_obj.id})
        return task_obj.action_send_assessment_meeting_email()

class EmployeeGrade(models.Model):
    _inherit = 'employee.grade'

    has_assessment=fields.Boolean(string="Has Assessment")

class RecruitmentStage(models.Model):
    _inherit = "hr.recruitment.stage"

    shortlisting_assessment=fields.Boolean(string="Shortlisting/Assessment")

class Applicant(models.Model):
    _inherit = "hr.applicant"

    ass_counts = fields.Integer(compute="_compute_ass_counts")

    def _compute_ass_counts(self):
        for this in self:
            asses = self.env['assessment_center.assessment_center'].search([('app_name','=',this.id)])
            this.ass_counts = len(asses)

    def action_view_assessment(self):
        action = self.env["ir.actions.actions"]._for_xml_id('assessment_center.assessment_center_dashboard_action')
        # action['res_id'] = self.assessment_id.id
        asses = self.env['assessment_center.assessment_center'].search([('app_name','=',self.id)])
        action['domain'] = [('id','in',asses.ids)]
        return action

    is_shortlisting_assessment=fields.Boolean(compute="compute_assessment")
    has_assessment=fields.Boolean(compute="compute_assessment")

    @api.onchange('stage_id')
    def compute_assessment(self):
        for this in self:
            this.is_shortlisting_assessment=this.stage_id.shortlisting_assessment
            if this.job_id.has_assessment or this.job_id.employee_grade.has_assessment:
                this.has_assessment=True
            else:
                this.has_assessment=False


    def create_assessment_from_applicant(self):
        for applicant in self:
            ass = self.env['assessment_center.assessment_center'].sudo().create({
            'app_name':applicant.id,
            'name':applicant.name,
            'partner_id':applicant.partner_id.id,
            'job_id':applicant.job_id.id,
            'email':applicant.email_from,
            'mobile':applicant.partner_mobile,
            'department_id':applicant.department_id.id,
            'project':applicant.project.id,
            'hr_id':applicant.hr_id,
            'manager':applicant.manager.id,
            'manager_email':applicant.manager.work_email,
            'emp_id':applicant.emp_id.id,
            'emp_project':applicant.emp_id.project.id,
            })
            if ass:
                users = self.env.ref('assessment_center.group_assessment_team').users
                mail_obj = self.env['mail.mail']
                body_html ="<div><p>The Assessment "+ass.name+" for the application "+ass.app_name.name+" has been created on "+str(ass.create_date)+" by "+ass.create_uid.name+" </p></div>"
                for user in users:
                    mail = mail_obj.create({
                    'subject':"Assessment Notification",
                    'body_html':body_html,
                    'email_to':user.partner_id.email,
                    })
                    mail.send()
            return True

    def unlink(self):
        for this in self:
            if this.ass_counts>0:
                raise UserError(
                    _('you can not delete this record delete (Delete connected Assessment First).')
                )
        return super(Applicant, self).unlink()
    
class MailTemplate(models.Model):
    _inherit = 'mail.template'

    assessment_test = fields.Boolean()
    assessment_meeting = fields.Boolean()

    @api.constrains('assessment_test')
    def _constrains_internal_sourcing_template(self):
        for rec in self:
            mail = self.search([('assessment_test', '=', True),
                                   ('id', '!=', rec.id)])
            if mail and rec.internal_sourcing_template:
                raise UserError(
                    _('Assessment Test Template Already Marked in %s.' % mail.name)
                )

    @api.constrains('assessment_meeting')
    
    def _constrains_internal_sourcing_template(self):
        for rec in self:
            mail = self.search([('assessment_test', '=', True),
                                   ('id', '!=', rec.id)])
            if mail and rec.internal_sourcing_template:
                raise UserError(
                    _('Assessment Meeting Template Already Marked in %s.' % mail.name)
                )
