# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools



class qoh_report(models.Model):
    _name = 'wc_raya_qoh.report'
    _description = 'wc_raya_qoh.report'
    _auto = False

    id=fields.Integer()
    x_tower=fields.Many2one('wc_raya_qoh.tower',string="Tower")
    x_working_location = fields.Many2one('work.locations',string="Site")
    x_sector = fields.Many2one('sector.sector',string="Sector" )
    x_partner_id = fields.Many2one("res.partner",string="Contact")
    x_project = fields.Many2one("rcc.project",string="Project")
    x_level_name = fields.Many2one('lang.levels',"English level")
    x_request_id = fields.Many2one("hiring.request",string="Request")
    x_batch = fields.Integer(string="Batch Numbers")
    x_month=fields.Char(string="Month")
    x_training_start_date = fields.Date("Training Start Date")
    x_source_id = fields.Many2one("utm.source",string="Source")
    x_medium_id = fields.Many2one("main.utm.source",string="Main Source")
    x_name = fields.Char("Name")
    x_phone = fields.Char("Phone")
    x_national_id = fields.Char("National ID")
    x_age = fields.Integer("Age")
    x_faculty = fields.Many2one("university.fac",string="Faculty")
    x_area_id = fields.Many2one("city.area",string="Area")
    x_graduated = fields.Char(string="Graduation Status")
    x_hc_date = fields.Date("Last HC date")
    x_days = fields.Float("Days")
    x_qoh=fields.Selection([('1','Yes'),('0','No')],string="QOH")
    x_tarinee_status=fields.Selection([('active','Active'),('dropped','Dropped')],string="Trainee Status")
    x_reason_id = fields.Many2one("drop.reasons",string="Reason")
    x_hc_status=fields.Many2one("wc_raya_qoh.hc_status",string="HC Status")
    x_user_id=fields.Many2one("res.users",string="Assigned Recruiter")
    def init(self):
        """ QOH main report """
        # tools.drop_view_if_exists(self._cr, 'wc_raya_qoh_report')

                   # level.name as x_level_name, ##################################### not ready yet

                   # inner join emp_lang_skills skill on  skill.applicant_id = applicant.id
                   # inner join lang_levels level on  level.id = skill.applicant_level

        self.env.cr.execute('DROP VIEW IF EXISTS wc_raya_qoh_report')
        self.env.cr.execute(""" CREATE VIEW wc_raya_qoh_report AS (
           SELECT row_number() OVER () as id,
           applicant.tower as x_tower,
           applicant.working_location as x_working_location,
           applicant.sector as x_sector,
           applicant.partner_id as x_partner_id,
           applicant.project as x_project,
           (SELECT levels FROM emp_lang_skills2 WHERE (SELECT name FROM lang_tech WHERE id = emp_lang_skills2.tech_id)= 'English' AND applicant_id=applicant.id) AS x_level_name, 
           applicant.hiring_request as x_request_id,
           applicant.batch_numbers as x_batch,
           split_part(to_char(applicant.training_start_date, 'YYYY MON'),' ', 2) AS x_month,
           applicant.training_start_date as x_training_start_date,
           applicant.source_id as x_source_id,
           applicant.main_source_n_c as x_medium_id,
           applicant.name as x_name,
           applicant.partner_phone as x_phone,
           applicant.national_id as x_national_id,
           applicant.age as x_age,
           applicant.faculty as x_faculty,
           applicant.area as x_area_id,
                      applicant.user_id as x_user_id,
CASE WHEN applicant.graduation_status = 'graduated' THEN 'Yes'
           WHEN applicant.graduation_status = 'notgraduated' THEN 'No'
           Else ''
END as x_graduated,
applicant.hc_date as x_hc_date,
TRUNC(DATE_PART('day',(CASE WHEN (applicant.tarinee_status='active') THEN
            CASE WHEN (applicant.quality_of_hiring_date > CURRENT_DATE)   THEN applicant.training_start_date
            WHEN (applicant.quality_of_hiring_date < CURRENT_DATE )  THEN applicant.quality_of_hiring_date
            END
    WHEN (applicant.tarinee_status='dropped') THEN applicant.drop_date

END-applicant.training_start_date::timestamp))) as x_days,
applicant.qoh as x_qoh,
applicant.tarinee_status as x_tarinee_status,
applicant.drop_reason as x_reason_id,
applicant.hc_status as x_hc_status
FROM hr_applicant applicant
WHERE applicant.job_category = 'operational' and applicant.active=True and applicant.joined_training='yes'
        )""")

class drp_report(models.Model):
    _name = 'wc_raya_qoh.reason'
    _description = 'wc_raya_qoh.reason'
    _auto = False

    id = fields.Integer()
    x_dropout_reason=fields.Char("Drop out reason")
    x_sector = fields.Many2one('sector.sector',string="Sector" )
    x_project = fields.Many2one("rcc.project",string="Project")
    x_reason_id = fields.Many2one("drop.reasons",string="Reason")

    def init(self):
        """ QOH main report """
        self.env.cr.execute('DROP VIEW IF EXISTS wc_raya_qoh_reason')
        self.env.cr.execute("""
        CREATE VIEW wc_raya_qoh_reason AS (
        SELECT row_number() OVER () as id,

         CASE WHEN applicant.drop_reason IS Not NULL THEN 'Reached'
            Else 'unreachable'
         END as x_dropout_reason,
           applicant.sector as x_sector,
           applicant.drop_reason as x_reason_id,
           applicant.project as x_project

         From hr_applicant applicant

where applicant.job_category='operational' and applicant.active=True and applicant.tarinee_status= 'dropped'

        );
        """)
