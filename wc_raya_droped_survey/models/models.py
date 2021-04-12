# -*- coding: utf-8 -*-


from odoo import api, fields, exceptions, models, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.exceptions import UserError
import werkzeug


class Survey(models.Model):
    _inherit = 'survey.survey'

    dropped_survey=fields.Boolean(string='Dropped Survey')

    @api.constrains('dropped_survey')
    def _constrains_dropped_survey(self):
        for rec in self:
            survey = self.search([('dropped_survey', '=', True),
                                   ('id', '!=', rec.id)])
            if survey and rec.dropped_survey:
                raise UserError(
                    _('Dropped Survey Already Marked in !!')
                )

class Applicant(models.Model):
    _inherit = "hr.applicant"

    dropped_survey=fields.Many2one('survey.survey',stored=True, compute="get_dropped_survey",string="Dropped Survey")
    dropped_answer_id = fields.Many2one('survey.user_input',compute="_compute_dropped_answer_id")
    trainer_id = fields.Many2one('hr.employee')
    training_session = fields.Selection([('online','Online'),('onsite','On Site')])
    def _compute_dropped_answer_id(self):
        for this in self:
            this.dropped_answer_id = False
            if this.dropped_survey:
                dropped_answer_id = self.env['survey.user_input'].search([('applicant_id','=',this.id),('survey_id','=',this.dropped_survey.id),('state','=','done')])
                if len(dropped_answer_id) == 1:
                    this.dropped_answer_id = dropped_answer_id.id


    @api.onchange('tarinee_status')
    def get_dropped_survey(self):
        for rec in self:
            survey = self.env['survey.survey'].search([('dropped_survey', '=', True)],limit=1)
            rec.dropped_survey = survey.id or False

    def action_send_survey(self):
        """ Open a window to compose an email, pre-filled with the survey message """
        # Ensure that this survey has at least one page with at least one question.
        if (not self.dropped_survey.page_ids and self.dropped_survey.questions_layout == 'page_per_section') or not self.dropped_survey.question_ids:
            raise exceptions.UserError(_('You cannot send an invitation for a survey that has no questions.'))

        if self.dropped_survey.state == 'closed':
            raise exceptions.UserError(_("You cannot send invitations for closed surveys."))

        template = self.env.ref('wc_raya_droped_survey.mail_template_user_input_invite', raise_if_not_found=False)
        if self.partner_id.id:
            local_context = dict(
                self.env.context,
                default_survey_id=self.dropped_survey.id,
                default_use_template=bool(template),
                default_template_id=template and template.id or False,
                default_partner_ids=[(6,0,[self.partner_id.id])],
                notif_layout='mail.mail_notification_light',
                default_applicant_id=self.id,
            )
        else:
            local_context = dict(
                self.env.context,
                default_survey_id=self.dropped_survey.id,
                default_use_template=bool(template),
                default_template_id=template and template.id or False,
                notif_layout='mail.mail_notification_light',
                default_applicant_id=self.id,
            )
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'dropped_survey_invite',
            'target': 'new',
            'context': local_context,
        }


class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    applicant_id=fields.Many2one('hr.applicant')
    project_id=fields.Many2one('rcc.project')
    recruiter_id=fields.Many2one('res.users')

    def get_dropped_survey_start_url(self):
        self.ensure_one()
        if self.applicant_id:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            for invite in self:
                return werkzeug.urls.url_join(base_url, invite.survey_id.get_start_url()) + '?app_id='+str(self.applicant_id.id)
        else:
            return '%s?answer_token=%s' % (self.survey_id.get_start_url(), self.access_token)


class MailTemplate(models.Model):
    _inherit = 'mail.template'


    dropped_survey = fields.Boolean()

    @api.constrains('dropped_survey')
    def _constrains_internal_sourcing_template(self):
        for rec in self:
            mail = self.search([('dropped_survey', '=', True),
                                   ('id', '!=', rec.id)])
            if mail and rec.dropped_survey:
                raise UserError(
                    _('Assessment Test Template Already Marked in %s.' % mail.name)
                )


# class wahy_report(models.Model):
#     _name = 'wc_raya_droped_survey.report'
#     _description = 'wc_raya_droped_survey.report'
#     _auto = False
#
#     id=fields.Integer()
#
#     def init(self):
#         """ QOH main report """
#         # tools.drop_view_if_exists(self._cr, 'wc_raya_qoh_report')
#         self.env.cr.execute('DROP VIEW IF EXISTS wc_raya_qoh_report')
#         self.env.cr.execute(""" CREATE VIEW wc_raya_qoh_report AS (
#            SELECT row_number() OVER () as id,

# class SurveyUserInputLine(models.Model):
#     _inherit = 'survey.user_input.line'
#
#     applicant_id = fields.Many2one('hr.applicant', related="user_input_id.applicant_id")
#     dropped_survey = fields.Boolean(string='Dropped Survey', related="survey_id.dropped_survey")
#     project_id = fields.Many2one('rcc.project', related="user_input_id.project_id")
#     applicant_number = fields.Char(related='applicant_id.partner_phone')
#     recruiter_id = fields.Many2one('res.users', related='applicant_id.user_id')
#     trainer_id = fields.Many2one('hr.employee', related='applicant_id.trainer_id')
#     training_session = fields.Selection([('online','Online'),('onsite','On Site')], related='applicant_id.training_session')



class WeHearYourVoice(models.Model):
    _name = 'we_hear_your_voice.report'
    _description = 'we_hear_your_voice.report'
    _auto = False

    id = fields.Integer()
    timestamp_date = fields.Datetime()
    applicant_id = fields.Many2one('hr.applicant')
    project_id = fields.Many2one('rcc.project')
    applicant_number = fields.Char()
    recruiter_id = fields.Many2one('res.users')
    trainer_id = fields.Many2one('hr.employee')
    training_session = fields.Selection([('online','Online'),('onsite','On Site')])
    question_id = fields.Many2one('survey.question')
    value_text_box = fields.Text()
    suggested_answer_id = fields.Many2one('survey.question.answer')

    def init(self):
        """ WE HEAR YOUR VOICE report """
        self.env.cr.execute('DROP VIEW IF EXISTS we_hear_your_voice_report')
        self.env.cr.execute(""" CREATE VIEW we_hear_your_voice_report AS (
            SELECT row_number() OVER () as id,
            create_date as timestamp_date,
            (select applicant_id from survey_user_input input_id where input_id.id = input_line_id.user_input_id) as applicant_id,
            (select project_id from survey_user_input input_id where input_id.id = input_line_id.user_input_id) as project_id,
            (select partner_phone from hr_applicant applicant where applicant.id = (select applicant_id from survey_user_input input_id where input_id.id = input_line_id.user_input_id)) as applicant_number,
            (select id from res_users user_id where user_id.id = (select user_id from hr_applicant applicant where applicant.id = (select applicant_id from survey_user_input input_id where input_id.id = input_line_id.user_input_id))) as recruiter_id,
            (select id from hr_employee employee where employee.id = (select trainer_id from hr_applicant applicant where applicant.id = (select applicant_id from survey_user_input input_id where input_id.id = input_line_id.user_input_id))) as trainer_id,
            (select training_session from hr_applicant applicant where applicant.id = (select applicant_id from survey_user_input input_id where input_id.id = input_line_id.user_input_id)) as training_session,
            question_id as question_id,
            value_text_box as value_text_box,
            suggested_answer_id as suggested_answer_id
            FROM survey_user_input_line input_line_id WHERE (select dropped_survey from survey_survey survey where survey.id = input_line_id.survey_id) = True
            ) """)
