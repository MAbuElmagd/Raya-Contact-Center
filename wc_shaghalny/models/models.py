# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    date_of_screening = fields.Date()
    external_referrals = fields.Boolean()
    walk_ins = fields.Boolean()

    @api.onchange('stage_id')
    def check_dos_when_change(self):
        # after_one_stage = self.env['hr.recruitment.stage'].search(['|', ('job_category', '=', False), ('job_category', '=', self.job_category)], order='sequence asc')[1]
        initial_stage = self.env['hr.recruitment.stage'].search([('job_category','=','operational'),('is_o_initial','=',True)])
        if self.stage_id != initial_stage and not self.date_of_screening and self.job_id.job_category == 'operational':
            raise ValidationError(_('You must enter the date of screening!'))


class wc_applicant_shaghlny(models.Model):
    _name = 'wc.applicant.shaghlny'
    _description = 'wc.applicant.shaghlny'
    _auto = False

    def action_view_summary(self):
        return self.env.ref('wc_shaghalny.action_report_shaghalny_summary').id

    id = fields.Integer()
    date_of_screening = fields.Date()
    referred_by_employee = fields.Many2one('hr.employee')
    referred_by_hr_id = fields.Char()
    referred_by_employee_grade = fields.Many2one('employee.grade')
    english_language = fields.Many2one('lang.levels')
    partner_name = fields.Char()
    partner_phone = fields.Char()
    three_days_training = fields.Char()
    national_id = fields.Char()
    ninty_days_training = fields.Date()
    tarinee_status = fields.Selection([('active','Active'),('dropped','Dropped'),('certified','Certified'),('join','Join'),('re_join','Re-Join')])
    project = fields.Many2one('rcc.project')
    fifty_three_days_training = fields.Selection([('eligible','Eligible'),('not_eligible','Not Eligible'),('paid','Paid')],'50% 3 Days Training')
    fifty_ninty_days_training = fields.Selection([('eligible','Eligible'),('not_eligible','Not Eligible'),('paid','Paid')],'50% 90 Days Training')
    # total = fields.Float()

    def init(self):
        """ Shaghlny main report """
        self.env.cr.execute('DROP VIEW IF EXISTS wc_applicant_shaghlny')
        self.env.cr.execute(""" CREATE VIEW wc_applicant_shaghlny AS (
        SELECT
          row_number() OVER () as id,
          applicant.date_of_screening as date_of_screening,
          applicant.referred_by_employee as referred_by_employee,
          applicant.referred_by_hr_id as referred_by_hr_id,
          applicant.referred_by_employee_grade as referred_by_employee_grade,
          (
            SELECT
              levels
            FROM
              emp_lang_skills2
            WHERE
              (
                SELECT
                  name
                FROM
                  lang_tech
                WHERE
                  id = emp_lang_skills2.tech_id
              )= 'English'
              AND applicant_id = applicant.id
          ) AS english_language,
          applicant.partner_name as partner_name,
          applicant.partner_phone as partner_phone,
          split_part(
            to_char(
              applicant.three_days_training, 'YYYY MON'
            ),
            ' ',
            2
          ) AS three_days_training,
          applicant.national_id as national_id,
          applicant.ninty_days_training as ninty_days_training,
          applicant.tarinee_status as tarinee_status,
          applicant.project as project,
          CASE WHEN applicant.fifty_three_days_training_payment = true THEN 'paid'
          ELSE applicant.fifty_three_days_training
          END as fifty_three_days_training,
          CASE WHEN applicant.fifty_ninty_days_training_payment = true THEN 'paid'
          ELSE applicant.fifty_ninty_days_training
          END as fifty_ninty_days_training
        FROM
          hr_applicant applicant
        WHERE
          applicant.referred_by_employee is not null
          AND applicant.joined_training = 'yes'
          AND applicant.tarinee_status != 'dropped'
          AND (applicant.fifty_ninty_days_training_payment = false OR applicant.fifty_three_days_training_payment = false)
          AND active = True
        )""")

        # GROUP BY date_of_screening,referred_by_employee,referred_by_hr_id,referred_by_employee_grade,english_language,partner_name,partner_phone,three_days_training,national_id,ninty_days_training,tarinee_status,project,fifty_three_days_training,fifty_ninty_days_training,total
