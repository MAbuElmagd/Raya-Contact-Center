# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
from itertools import groupby
from pytz import timezone, UTC
from werkzeug.urls import url_encode

from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_is_zero
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
# from odoo import api, fields, models, tools,_
# from datetime import datetime
from odoo.tools import pycompat, sql
import uuid
from psycopg2 import ProgrammingError
import base64
import logging
import re
from io import BytesIO
# from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)

class WcRecruitmentDaily(models.TransientModel):
    _name = 'wc_recruitment_daily'
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)

    def action_print_report_excel_wiz(self):
        data_form = {}
        data_form['form'] = self.read(['date_from', 'date_to'])[0]
        return self.action_print_report_excel(data_form)

    def action_print_report_excel(self, data_form):
        data_form['form'].update(self.read(['date_from', 'date_to'])[0])
        data_dict = {}
        data_dict['data_form'] = data_form
        doc_ids = self
        return self.env.ref('wc_recruitment_daily.report_wc_recruitment_daily').report_action(docids=doc_ids,data=data_dict)

class WcRecruitmentDailyABS(models.AbstractModel):
    _name = 'report.wc_recruitment_daily.report_daily_tracker'
    _inherit = 'report.report_xlsx.abstract'

    def sql_call(self):
        LANG_COLUMNS_SQL = []
        HR_COLUMNS_SQL = []
        TECH_COLUMNS_SQL = []
        LANG_COLUMNS_EXCEL = []
        HR_COLUMNS_EXCEL = []
        TECH_COLUMNS_EXCEL = []
        self.env.cr.execute('DROP TABLE if EXISTS x_wc_recruitment_daily_report_sql')
        self.env.cr.execute(""" CREATE TABLE x_wc_recruitment_daily_report_sql AS (
SELECT applicant.id                                             AS applicant_id,
       applicant.create_date                                    AS x_create_date
       ,
       (SELECT job_code
        FROM   hr_job
        WHERE  id = applicant.job_id)                           AS x_job_code,
       applicant.partner_name                                   AS
       x_applicant_name,
       applicant.partner_phone                                  AS x_phone,
       applicant.national_id                                    AS x_national_id
       ,
       (SELECT name
        FROM   res_country
        WHERE  id = applicant.nationality)                      AS x_nationality
       ,
       CASE
         WHEN applicant.gender = 'male' THEN 'Male'
         WHEN applicant.gender = 'female' THEN 'Female'
         ELSE ''
       END                                                      AS x_gender,
       applicant.age                                            AS x_age,
       (SELECT name
        FROM   res_country_state
        WHERE  id = applicant.state)                            AS x_governorate
       ,
       (SELECT name
        FROM   city_area
        WHERE  id = applicant.area)                             AS x_city_area,
       applicant.military_status                                AS
       x_military_status,
       CASE
         WHEN applicant.graduation_status = 'graduated' THEN 'Graduated'
         WHEN applicant.graduation_status = 'notgraduated' THEN
         'Under Graduated'
         ELSE ''
       END                                                      AS
       x_graduation_status,
       (SELECT name
        FROM   hr_institute
        WHERE  id = applicant.university)                       AS x_university,
       (SELECT name
        FROM   university_fac
        WHERE  id = applicant.faculty)                          AS x_faculty,
       applicant.social_insurance                               AS
       x_social_insurance,
       applicant.email_from                                     AS x_email,
       applicant.pc_laptop                                      AS x_pc_laptop,
       applicant.internet_con                                   AS
       x_internet_con,
       CASE
         WHEN applicant.con_speed = 'less_10' THEN 'Less than 10 Mbps'
         WHEN applicant.con_speed = '10 Mbps' THEN '10 Mbps'
         WHEN applicant.con_speed = 'More10Mbps' THEN 'More than 10 Mbps'
         ELSE ''
       END                                                      AS x_con_speed,
       applicant.internet_provider                              AS
       x_internet_provider,
       applicant.indebendancy                                   AS
       x_indebendancy,
       applicant.prev_work_experience                           AS
       x_prev_work_experience,
       applicant.prev_work_experience_what                      AS
       x_prev_work_experience_what,
       applicant.why_leave                                      AS x_why_leave,
       applicant.why_join                                       AS x_why_join,
       applicant.salary_expected                                AS
       x_salary_expections,
       applicant.rotational_shifts                              AS
       x_relational_shifts,
       applicant.english_status                                 AS
       x_english_level,
       applicant.worked_4_raya                                  AS
       x_worked_4_raya,
       applicant.ready_work_from_home                           AS
       x_ready_work_from_home,
       applicant.operating_sys                                  AS
       x_operating_sys,
       (SELECT name
        FROM   main_utm_source
        WHERE  id = applicant.main_source_n_c)                  AS x_main_source
       ,
       (SELECT name
        FROM   utm_source
        WHERE  id = applicant.source_id)                        AS x_source,
       (SELECT name
        FROM   res_partner
        WHERE  id = (SELECT partner_id
                     FROM   res_users
                     WHERE  id = applicant.user_id))            AS x_recruiter,
       To_timestamp(To_char(applicant.hr_interviwe_date, 'YYYY-MM-DD'),
       'YYYY-MM-DD HH:MI:SS')                                   AS
       x_hr_interviwe_date,
       applicant.sales_experience                               AS
       x_sales_experience,
       applicant.years_of_experience                            AS
       x_years_of_experience,
       CASE
         WHEN applicant.first_interview_feedback = 'accepted' THEN 'Accepted'
         WHEN applicant.first_interview_feedback = 'rejected' THEN 'Rejected'
         WHEN applicant.first_interview_feedback = 'refuse' THEN 'Refuse'
         WHEN applicant.first_interview_feedback = 'lost_interest' THEN
         'Lost Interest'
         WHEN applicant.first_interview_feedback = 'not_matching_criteria' THEN
         'Not Matching Criteria'
         WHEN applicant.first_interview_feedback = 'no_show' THEN 'No Show'
         ELSE ''
       END                                                      AS
       x_first_interview_feedback,
       (SELECT name
        FROM   interview_feedback
        WHERE  id = applicant.first_interview_feedback_reason)  AS
       x_first_interview_feedback_reason,
       (SELECT name
        FROM   sector_sector
        WHERE  id = applicant.sector)                           AS x_sector,
       (SELECT name
        FROM   rcc_project
        WHERE  id = applicant.project)                          AS x_project,
       CASE
         WHEN applicant.second_interview_feedback = 'accepted' THEN 'Accepted'
         WHEN applicant.second_interview_feedback = 'rejected' THEN 'Rejected'
         WHEN applicant.second_interview_feedback = 'refuse' THEN 'Refuse'
         WHEN applicant.second_interview_feedback = 'lost_interest' THEN
         'Lost Interest'
         WHEN applicant.second_interview_feedback = 'not_matching_criteria' THEN
         'Not Matching Criteria'
         WHEN applicant.second_interview_feedback = 'no_show' THEN 'No Show'
         ELSE ''
       END                                                      AS
       x_second_interview_feedback,
       (SELECT name
        FROM   interview_feedback
        WHERE  id = applicant.second_interview_feedback_reason) AS
       x_second_interview_feedback_reason,
       applicant.english_test_result                            AS
       x_english_test_result,
       applicant.typing_test_result                             AS
       x_typing_test_result,
       CASE
         WHEN applicant.job_offer_feedback = 'accepted' THEN 'Yes'
         ELSE 'No'
       END                                                      AS
       x_job_offer_feedback,
       To_timestamp(To_char(applicant.date_of_signing, 'YYYY-MM-DD'),
       'YYYY-MM-DD HH:MI:SS')                                   AS
       x_date_of_signing,
       (SELECT name
        FROM   interview_feedback
        WHERE  id = applicant.job_offer_feedback_reason)        AS
       x_job_offer_feedback_reason,
       CASE
         WHEN applicant.hired = 'yes' THEN 'Yes'
         ELSE 'No'
       END                                                      AS x_hired,
       To_timestamp(To_char(applicant.date_of_hiring, 'YYYY-MM-DD'),
       'YYYY-MM-DD HH:MI:SS')                                   AS
       x_date_of_hiring,
       (SELECT name
        FROM   interview_feedback
        WHERE  id = applicant.reason_if_not_hired)              AS
       x_reason_if_not_hired,
       CASE
         WHEN (SELECT sector_projects_type
               FROM   sector_sector
               WHERE  id = applicant.sector) = 'banking' THEN 'Banking'
         WHEN (SELECT sector_projects_type
               FROM   sector_sector
               WHERE  id = applicant.sector) = 'etisalat' THEN 'Etisalat'
         WHEN (SELECT sector_projects_type
               FROM   sector_sector
               WHERE  id = applicant.sector) = 'non_etisalat' THEN
         'Non-Etisalat'
         ELSE ''
       END                                                      AS
       x_sector_projects_type
FROM   hr_applicant applicant
WHERE  job_category = 'operational'
       AND active = TRUE
ORDER  BY applicant_id ASC           );""")
        non_technical = self.env['nontech.nontech'].search([])
        for non in non_technical:
            col_name = non.name.lower().replace(' ','_').replace('-','_').replace('&','').replace("'","").replace('__','_')
            HR_COLUMNS_EXCEL.append(non.name)
            HR_COLUMNS_SQL.append(col_name)
            self.env.cr.execute('ALTER TABLE x_wc_recruitment_daily_report_sql ADD COLUMN IF NOT EXISTS '+col_name+' VARCHAR;')
            applicants_data = self.env['emp.nontech.skills'].search([('nontech_id','=',non.id)], order="applicant_id asc")
            for applicant_non in applicants_data:
                if applicant_non.applicant_id.id:
                    level = "null"
                    if applicant_non.levels == 'basic':
                        level = "'1'"
                    elif applicant_non.levels == 'medium':
                        level = "'2'"
                    elif applicant_non.levels == 'advance':
                        level = "'3'"
                    elif applicant_non.levels == '4_advance':
                        level = "'4'"
                    elif applicant_non.levels == '5_advance':
                        level = "'5'"
                    self.env.cr.execute('UPDATE x_wc_recruitment_daily_report_sql SET '+col_name+' = '+level+' WHERE applicant_id = '+str(applicant_non.applicant_id.id)+';')
        #####################################################################################################################################################################
        technical = self.env['tech.tech'].search([])
        for tec in technical:
            col_name = tec.name.lower().replace(' ','_').replace('-','_').replace('&','').replace("'","").replace('__','_')
            TECH_COLUMNS_EXCEL.append(tec.name)
            TECH_COLUMNS_SQL.append(col_name)
            self.env.cr.execute('ALTER TABLE x_wc_recruitment_daily_report_sql ADD COLUMN IF NOT EXISTS '+col_name+' VARCHAR;')
            applicants_data = self.env['emp.tech.skills'].search([('tech_id','=',tec.id)], order="applicant_id asc")
            for applicant_tec in applicants_data:
                if applicant_tec.applicant_id.id:
                    level = "null"
                    if applicant_tec.levels == 'basic':
                        level = "'Basic'"
                    elif applicant_tec.levels == 'medium':
                        level = "'Medium'"
                    elif applicant_tec.levels == 'advance':
                        level = "'Advance'"
                    self.env.cr.execute('UPDATE x_wc_recruitment_daily_report_sql SET '+col_name+' = '+level+' WHERE applicant_id = '+str(applicant_tec.applicant_id.id)+';')
        #####################################################################################################################################################################
        language = self.env['lang.tech'].search([])
        for lang in language:
            col_name = lang.name.lower().replace(' ','_').replace('-','_').replace('&','').replace("'","").replace('__','_')
            LANG_COLUMNS_EXCEL.append(lang.name)
            LANG_COLUMNS_SQL.append(col_name)
            if col_name == 'english':
                LANG_COLUMNS_SQL.append('pronunciation')
                LANG_COLUMNS_SQL.append('grammer')
                LANG_COLUMNS_SQL.append('fluency')
                LANG_COLUMNS_SQL.append('understanding_vocab')
                LANG_COLUMNS_EXCEL.append("Pronunciation")
                LANG_COLUMNS_EXCEL.append("Grammer")
                LANG_COLUMNS_EXCEL.append("Fluency")
                LANG_COLUMNS_EXCEL.append("Understanding Vocab")

            self.env.cr.execute('ALTER TABLE x_wc_recruitment_daily_report_sql ADD COLUMN IF NOT EXISTS '+col_name+' VARCHAR;')
            self.env.cr.execute('ALTER TABLE x_wc_recruitment_daily_report_sql ADD COLUMN IF NOT EXISTS pronunciation VARCHAR;')
            self.env.cr.execute('ALTER TABLE x_wc_recruitment_daily_report_sql ADD COLUMN IF NOT EXISTS grammer VARCHAR;')
            self.env.cr.execute('ALTER TABLE x_wc_recruitment_daily_report_sql ADD COLUMN IF NOT EXISTS fluency VARCHAR;')
            self.env.cr.execute('ALTER TABLE x_wc_recruitment_daily_report_sql ADD COLUMN IF NOT EXISTS understanding_vocab VARCHAR;')
            applicants_data = self.env['emp.lang.skills2'].search([('tech_id','=',lang.id)], order="applicant_id asc")
            for applicant_lang in applicants_data:
                if applicant_lang.applicant_id.id:
                    level = "null"
                    if applicant_lang.levels.name:
                        level = "'"+applicant_lang.levels.name+"'"
                    self.env.cr.execute('UPDATE x_wc_recruitment_daily_report_sql SET '+col_name+' = '+level+' WHERE applicant_id = '+str(applicant_lang.applicant_id.id)+';')
                    self.env.cr.execute('UPDATE x_wc_recruitment_daily_report_sql SET pronunciation = '+str(applicant_lang.pronunciation)+' WHERE applicant_id = '+str(applicant_lang.applicant_id.id)+';')
                    self.env.cr.execute('UPDATE x_wc_recruitment_daily_report_sql SET grammer = '+str(applicant_lang.grammer)+' WHERE applicant_id = '+str(applicant_lang.applicant_id.id)+';')
                    self.env.cr.execute('UPDATE x_wc_recruitment_daily_report_sql SET fluency = '+str(applicant_lang.fluency)+' WHERE applicant_id = '+str(applicant_lang.applicant_id.id)+';')
                    self.env.cr.execute('UPDATE x_wc_recruitment_daily_report_sql SET understanding_vocab = '+str(applicant_lang.understanding_vocab)+' WHERE applicant_id = '+str(applicant_lang.applicant_id.id)+';')
        self.env.cr.execute("ALTER TABLE x_wc_recruitment_daily_report_sql DROP COLUMN IF EXISTS applicant_id;")
        return LANG_COLUMNS_SQL,HR_COLUMNS_SQL,TECH_COLUMNS_SQL,LANG_COLUMNS_EXCEL,HR_COLUMNS_EXCEL,TECH_COLUMNS_EXCEL

    # @api.model
    # def _get_report_values(self, docids, data=None):
    #     self.sql_call()
    #     self.env.cr.execute('SELECT * FROM x_wc_recruitment_daily_report_sql')
    #     data = self.env.cr.fetchall()
    #     print("يا رب يشتغل ")
    #     print(data)
    #     print("يا رب يشتغل ")
    #
    #     docargs = {
    #         'doc_ids': self.ids,
    #         'doc_model': self.model,
    #         'docs': self.env['hr.applicant'].search([],limit=1),
    #         'data':data,
    #     }
    #     return {'lines':docids.get_lines()}
    def generate_xlsx_report(self, workbook, data, objects):
        # print("data")
        # print(data)
        # print("data")
        # print("data_form")
        # print(data_form)
        # print("data_form")
        # return True
        # self.env['res.partner'].search([],limit=1)
        date_from = data['data_form']['form']['date_from']
        date_to = data['data_form']['form']['date_to']

        # date_date_from = date_from.strptime("%m-%b-%Y")
        # date_date_to = date_to.strptime("%m-%b-%Y")
        # print(type(date_from))
        # print(date_from)
        # print(type(date_to))
        # print(date_to)
        # print("SELECT * FROM x_wc_recruitment_daily_report_sql WHERE x_create_date >= TO_DATE('"+str(date_from)+"','YYYY/MM/DD') AND x_create_date <= TO_DATE('"+str(date_to)+"','YYYY/MM/DD');")
        LANG_COLUMNS_SQL,HR_COLUMNS_SQL,TECH_COLUMNS_SQL,LANG_COLUMNS_EXCEL,HR_COLUMNS_EXCEL,TECH_COLUMNS_EXCEL = self.sql_call()
        sql_item =['x_create_date','x_job_code','x_applicant_name','x_phone','x_national_id','x_nationality','x_gender','x_age','x_governorate','x_city_area','x_military_status','x_graduation_status','x_university','x_faculty','x_social_insurance','x_email','x_pc_laptop','x_internet_con','x_con_speed','x_internet_provider','x_indebendancy','x_prev_work_experience','x_prev_work_experience_what','x_why_leave','x_why_join','x_salary_expections','x_relational_shifts','x_english_level','x_worked_4_raya','x_ready_work_from_home','x_operating_sys','x_main_source','x_source','x_recruiter','x_hr_interviwe_date']
        for lang in LANG_COLUMNS_SQL:
            print(lang)
            sql_item.append(lang)
        # ###########################
        sql_item.append('x_sales_experience')
        sql_item.append('x_years_of_experience')
        # ###########################

        for h in HR_COLUMNS_SQL:
            sql_item.append(h)
        for tec in TECH_COLUMNS_SQL:
            sql_item.append(tec)
        sql_item.append('x_first_interview_feedback')
        sql_item.append('x_first_interview_feedback_reason')
        sql_item.append('x_sector')
        sql_item.append('x_project')
        sql_item.append('x_second_interview_feedback')
        sql_item.append('x_second_interview_feedback_reason')
        sql_item.append('x_english_test_result')
        sql_item.append('x_typing_test_result')
        sql_item.append('x_job_offer_feedback')
        sql_item.append('x_date_of_signing')
        sql_item.append('x_job_offer_feedback_reason')
        sql_item.append('x_hired')
        sql_item.append('x_date_of_hiring')
        sql_item.append('x_reason_if_not_hired')
        sql_item.append('x_sector_projects_type')
        select_str = ""
        for item in sql_item:
            select_str += item + ','
        select_str = select_str[0:-1]
        print("SELECT "+select_str+" FROM x_wc_recruitment_daily_report_sql WHERE x_create_date::date >= TO_DATE('"+str(date_from)+"','YYYY/MM/DD') AND x_create_date::date <= TO_DATE('"+str(date_to)+"','YYYY/MM/DD');")
        self.env.cr.execute("SELECT "+select_str+" FROM x_wc_recruitment_daily_report_sql WHERE x_create_date::date >= TO_DATE('"+str(date_from)+"','YYYY/MM/DD') AND x_create_date::date <= TO_DATE('"+str(date_to)+"','YYYY/MM/DD');")
        # self.env.cr.execute("SELECT * FROM x_wc_recruitment_daily_report_sql WHERE cast(\"x_create_date\" as DATE) >= cast('"+str(date_from)+"' as date) and cast(\"x_create_date\" as DATE) <= cast('"+str(date_to)+"' as date)")

        data = self.env.cr.fetchall()
        # print(data)
        # objects = self.env['hr.applicant'].browse(1142)

        head1 = ['Timestamp', 'Job Code', "Full Name", 'Mobile number', 'National ID', 'Nationality', 'Gender', 'Age', 'Your Governorate', 'Where do you live / Area', 'Military Status', 'Graduation status', 'University', 'Faculty of', 'Do You have Social insurance?', 'E-mail Address', 'Do You Have PC or Laptop?', 'Do You have Internet Connection?', 'What is your Connection Speed?', 'Connection Provider Name?', 'Do You Prefer Working Independently or within a Team?', 'Do you have Previous Work Experience?', 'What is your Previous work Experience?', 'Why do you want to leave your work?', 'Why do you want this Job?', 'Salary Expections', 'Are you fine with rotational shifts?', 'English Level', 'Did You work before at Raya?', 'Are You ready to work from home?', 'Your Operating System ?', 'Main Source', 'Source', 'Rec Name','HR Interview Date',]
        LANG_COLUMNS_EXCEL = LANG_COLUMNS_EXCEL
        head2 = ['Sales Experience', 'Years of Experience',]
        HR_COLUMNS_EXCEL = HR_COLUMNS_EXCEL
        TECH_COLUMNS_EXCEL = TECH_COLUMNS_EXCEL
        head3 = ['First Interview Feedback', 'First Interview Feedback Reason', 'Sector', 'Project', 'Second Interview Feedback', 'Second Interview Feedback Reason', 'English Test Result', 'Typing Test Result', 'Job Offer Feedback', 'Date of Signing', 'Job Offer Feedback Reason', 'Hired', 'Date of Hiring', 'Reason if Not Hired', 'Sector Projects Type']

        head = []
        for h1 in head1:
            head.append(h1)
        for lang in LANG_COLUMNS_EXCEL:
            head.append(lang)
        for h2 in head2:
            head.append(h2)
        for hr in HR_COLUMNS_EXCEL:
            head.append(hr)
        for tech in TECH_COLUMNS_EXCEL:
            head.append(tech)
        for h3 in head3:
            head.append(h3)

        sheet = workbook.add_worksheet("Recruitment Daily Tracker")
        bold = workbook.add_format({'bold': True})
        i = 0
        for obj in head:
            # One sheet by partner
            sheet.write(0, i, obj, bold)
            i +=1
        i=1
        for row in data:
            # print(row)
            j=0
            for col in row:
                # if j == 0 or j == 34 or j == 46 or j == 49:
                try:
                    col = col.date().strftime("%Y-%m-%d")
                except Exception as e:
                    col = col
                    # tmp = ""
                    # for value in col.split(','):
                    #     tmp += value+'/'
                    # col = tmp.split(')')[0]
                    # print(col)

                sheet.write(i, j, col)
                j +=1
            i+=1
# class rdt_report(models.Model):
#     _name = 'x_wc_recruitment_daily_report_sql'
#     _description = 'x_wc_recruitment_daily_report_sql'
#     _auto = False
#     _TTYPE_SELECTION = [
#         ("boolean", "boolean"),
#         ("char", "char"),
#         ("date", "date"),
#         ("datetime", "datetime"),
#         ("float", "float"),
#         ("integer", "integer"),
#         ("many2one", "many2one"),
#         ("selection", "selection"),
#     ]
#     _SQL_MAPPING = {
#         "boolean": "boolean",
#         "bigint": "integer",
#         "integer": "integer",
#         "double precision": "float",
#         "numeric": "float",
#         "text": "char",
#         "character varying": "char",
#         "date": "date",
#         "timestamp without time zone": "datetime",
#     }
#     _FIELDS = []
#
#     def init(self):
#         print("INIT")
#         print("INIT")
#         print("INIT")
#         print("INIT")
#         print("INIT")
#         # self.create_sql_view_and_model_btn()
#         field_id = []
#         field_ids = []
#         columns = [(1, 'x_create_date', 'timestamp without time zone'), (2, 'x_job_code', 'integer'), (3, 'x_applicant_name', 'character varying'), (4, 'x_phone', 'character varying(32)'), (5, 'x_national_id', 'character varying(14)'), (6, 'x_nationality', 'character varying'), (7, 'x_gender', 'character varying'), (8, 'x_age', 'integer'), (9, 'x_governorate', 'character varying'), (10, 'x_city_area', 'character varying'), (11, 'x_military_status', 'character varying'), (12, 'x_graduation_status', 'character varying'), (13, 'x_university', 'character varying'), (14, 'x_faculty', 'character varying'), (15, 'x_social_insurance', 'character varying'), (16, 'x_email', 'character varying(128)'), (17, 'x_pc_laptop', 'character varying'), (18, 'x_internet_con', 'character varying'), (19, 'x_con_speed', 'character varying'), (20, 'x_internet_provider', 'character varying'), (21, 'x_indebendancy', 'character varying'), (22, 'x_prev_work_experience', 'character varying'), (23, 'x_prev_work_experience_what', 'character varying'), (24, 'x_why_leave', 'character varying'), (25, 'x_why_join', 'character varying'), (26, 'x_salary_expections', 'character varying'), (27, 'x_relational_shifts', 'character varying'), (28, 'x_english_level', 'character varying'), (29, 'x_worked_4_raya', 'character varying'), (30, 'x_ready_work_from_home', 'character varying'), (31, 'x_operating_sys', 'character varying'), (32, 'x_main_source', 'character varying'), (33, 'x_source', 'character varying'), (34, 'x_recruiter', 'character varying'), (35, 'x_hr_interviwe_date', 'date'), (36, 'x_sales_experience', 'character varying'), (37, 'x_years_of_experience', 'integer'), (38, 'x_first_interview_feedback', 'character varying'), (39, 'x_interview_feedback_reason', 'character varying'), (40, 'x_sector', 'character varying'), (41, 'x_project', 'character varying'), (42, 'x_second_interview_feedback', 'character varying'), (43, 'x_second_interview_feedback_reason', 'character varying'), (44, 'x_english_test_result', 'character varying'), (45, 'x_pronunciation', 'integer'), (46, 'x_grammer', 'integer'), (47, 'x_fluency', 'integer'), (48, 'x_understanding_vocab', 'integer'), (49, 'x_typing_test_result', 'character varying'), (50, 'x_job_offer_feedback', 'text'), (51, 'x_date_of_signing', 'timestamp without time zone'), (52, 'x_job_offer_feedback_reason', 'character varying'), (53, 'x_hired', 'character varying'), (54, 'x_date_of_hiring', 'timestamp without time zone'), (55, 'x_reason_if_not_hired', 'character varying'), (56, 'x_sector_projects_type', 'character varying')]
#         for column in columns:
#             if column[1][:2] == "x_":
#                 field_ids.append({
#                             "sequence": column[0],
#                             "name": column[1],
#                             "sql_type": column[2],
#                         })
#                 self._FIELDS.append({
#                             "sequence": column[0],
#                             "name": column[1],
#                             "sql_type": column[2],
#                         })
#         field_ids = [{
#                     "sequence": 1,
#                     "name": 'x_test_add_fielddddddddddd_1',
#                     "sql_type": 'character varying',
#                 }]
#         for field in field_ids:
#             ttype = False
#             for k, v in self._SQL_MAPPING.items():
#                 if k in field["sql_type"]:
#                     ttype = v
#             print("{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{{}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}")
#             print(self._name)
#             print(self.env['ir.model'].search([('model','=',self._name)]).id)
#             if self.env['ir.model'].search([('model','=',self._name)]).id:
#                 field_id.append({
#                     "name": field['name'],
#                     "field_description": field['name'],
#                     "model_id": self.env['ir.model'].search([('model','=',self._name)]).id,
#                     "ttype": ttype,
#                     "selection": False,
#                     "relation": False,
#                     "state": 'manual'
#                 })
#         for fld in field_id:
#             old_one = self.env['ir.model.fields'].search([('name','=',fld['name'])])
#             print("old_one")
#             print(old_one)
#             print("old_one")
#             new = self.env['ir.model.fields']
#             if len(old_one)>0:
#                 pass
#             else:
#                 print("fld")
#                 print(fld)
#                 print("fld")
#                 new=self.env['ir.model.fields'].create(fld)
#             if len(new)>0:
#                 print(new)
#             else:
#                 print(old_one)
#
#         self.env.cr.execute('DROP VIEW IF EXISTS x_wc_recruitment_daily_report_sql')
#         self.env.cr.execute(""" CREATE VIEW x_wc_recruitment_daily_report_sql AS (
#         select  row_number() OVER () as id,
# 		applicant.create_date as x_create_date,
# 	  	applicant.job_code as x_job_code,
# 		applicant.partner_name as x_applicant_name,
# 		applicant.partner_phone as x_phone,
# 		applicant.national_id as x_national_id,
# 		applicant.nationality as x_nationality,
# 		applicant.gender as x_gender,
# 		applicant.age as x_age,
# 		applicant.state as x_governorate,
# 		applicant.area as x_city_area,
# 		applicant.military_status as x_military_status,
# 		applicant.graduation_status as x_graduation_status,
# 		applicant.university as x_university,
# 		applicant.faculty as x_faculty,
# 		applicant.social_insurance as x_social_insurance,
# 		applicant.email_from as x_email,
# 		applicant.pc_laptop as x_pc_laptop,
# 		applicant.internet_con as x_internet_con,
# 		applicant.con_speed as x_con_speed,
# 		applicant.internet_provider as x_internet_provider,
# 		applicant.indebendancy as x_indebendancy,
# 		applicant.prev_work_experience as x_prev_work_experience,
# 		applicant.prev_work_experience_what as x_prev_work_experience_what,
# 		applicant.why_leave as x_why_leave,
# 		applicant.why_join as x_why_join,
# 		applicant.salary_expections as x_salary_expections,
# 		applicant.rotational_shifts as x_relational_shifts,
# 		applicant.english_status as x_english_level,
# 		applicant.worked_4_raya as x_worked_4_raya,
# 		applicant.ready_work_from_home as x_ready_work_from_home,
# 		applicant.operating_sys as x_operating_sys,
# 		applicant.main_source as x_main_source,
# 		applicant.source_id as x_source,
# 		applicant.hr_interviwe_date as x_hr_interviwe_date,
# 		applicant.user_id as x_recruiter,
# 		applicant.sales_experience as x_sales_experience,
# 		applicant.years_of_experience as x_years_of_experience,
# 		applicant.first_interview_feedback as x_first_interview_feedback,
# 		applicant.first_interview_feedback_reason as x_first_interview_feedback_reason,
# 		applicant.sector as x_sector,
# 		applicant.project as x_project,
# 		applicant.second_interview_feedback as x_second_interview_feedback,
# 		applicant.second_interview_feedback_reason as x_second_interview_feedback_reason,
# 		applicant.english_test_result as x_english_test_result,
# 		applicant.pronunciation as x_pronunciation,
# 		applicant.grammer as x_grammer,
# 		applicant.fluency as x_fluency,
# 		applicant.understanding_vocab as x_understanding_vocab,
# 		applicant.typing_test_result as x_typing_test_result,
# 		CASE WHEN applicant.job_offer_feedback = 'accepted' THEN 'Yes'
#          ELSE 'No' END AS x_job_offer_feedback,
# 		applicant.date_of_signing as x_date_of_signing,
# 		applicant.job_offer_feedback_reason as x_job_offer_feedback_reason,
# 		applicant.hired as x_hired,
# 		applicant.date_of_hiring as x_date_of_hiring,
# 		applicant.reason_if_not_hired as x_reason_if_not_hired,
# 		applicant.sector_projects_type as x_sector_projects_type
# 		from hr_applicant applicant
# 		where job_category = 'operational' and active = true
# -- 		inner join res_partner partner on applicant.partner_id = partner.id and applicant.job_category = 'operational'
# -- 		inner join res_country country on applicant.nationality = country.id
# -- 		inner join res_country_state state_id on applicant.state = state_id.id
# -- 		inner join city_area area_id on applicant.area = area_id.id
# -- 		inner join hr_institute university_id on applicant.university = university_id.id
# -- 		inner join university_fac faculty_id on applicant.faculty = faculty_id.id
# -- 		inner join utm_source source_id on applicant.source_id = source_id.id
# -- 		inner join res_users recruit_id on applicant.user_id = recruit_id.id
# -- 		inner join interview_feedback interview_feedback_reason_id on applicant.first_interview_feedback_reason = interview_feedback_reason_id.id
# -- 		inner join  hiring_request request on applicant.hiring_request = request.id
# -- 		inner join rcc_project project_id on applicant.project = project_id.id
# -- 		inner join interview_feedback sec_interview_feedback_reason_id on applicant.second_interview_feedback_reason = sec_interview_feedback_reason_id.id
# -- 		inner join interview_feedback job_offer_feedback_reason on applicant.job_offer_feedback_reason = job_offer_feedback_reason.id
# -- 		inner join interview_feedback reason_if_not_hired on applicant.reason_if_not_hired = reason_if_not_hired.id
#         )""")
#         print("############################################")
#         print("############################################")
#         print("############################################")
#
#         # model = self.env['ir.model'].search([('model','=',self._name)])
#         # for fld in field_id:
#         #     field_created = self.env['ir.model.fields'].create(fld)
#         #     print("FLD")
#         #     print(field_created)
#         #     print("FLD")
#
#
#         # self._create_view_btn()
#
#     def create_sql_view_and_model_btn(self):
#         print("create_sql_view_and_model_btn")
#         self._create_model_and_fields_btn()
#         self._create_model_access_btn()
#         # self._create_view_btn()
#
#     def _create_model_and_fields_btn(self):
#         print("_create_model_and_fields_btn")
#         model_vals = self._prepare_model_btn()
#         model_id = self.env["ir.model"].create(model_vals).id
#         print("OOOOOOOOOOOOOOOOOOOOOO")
#         rule_id = self.env["ir.rule"].create(self._prepare_rule_btn(model_id)).id
#     def _prepare_request_check_execution_btn(self):
#         print("_prepare_request_check_execution_btn")
#         """Overload me to replace some part of the query, if it contains
#         parameters"""
#         query = ("""select  row_number() OVER () as id,
# 		applicant.create_date as x_create_date,
# 	  	applicant.job_code as x_job_code,
# 		applicant.partner_name as x_applicant_name,
# 		applicant.partner_phone as x_phone,
# 		applicant.national_id as x_national_id,
# 		applicant.nationality as x_nationality,
# 		applicant.gender as x_gender,
# 		applicant.age as x_age,
# 		applicant.state as x_governorate,
# 		applicant.area as x_city_area,
# 		applicant.military_status as x_military_status,
# 		applicant.graduation_status as x_graduation_status,
# 		applicant.university as x_university,
# 		applicant.faculty as x_faculty,
# 		applicant.social_insurance as x_social_insurance,
# 		applicant.email_from as x_email,
# 		applicant.pc_laptop as x_pc_laptop,
# 		applicant.internet_con as x_internet_con,
# 		applicant.con_speed as x_con_speed,
# 		applicant.internet_provider as x_internet_provider,
# 		applicant.indebendancy as x_indebendancy,
# 		applicant.prev_work_experience as x_prev_work_experience,
# 		applicant.prev_work_experience_what as x_prev_work_experience_what,
# 		applicant.why_leave as x_why_leave,
# 		applicant.why_join as x_why_join,
# 		applicant.salary_expections as x_salary_expections,
# 		applicant.rotational_shifts as x_relational_shifts,
# 		applicant.english_status as x_english_level,
# 		applicant.worked_4_raya as x_worked_4_raya,
# 		applicant.ready_work_from_home as x_ready_work_from_home,
# 		applicant.operating_sys as x_operating_sys,
# 		applicant.main_source as x_main_source,
# 		applicant.source_id as x_source,
# 		applicant.hr_interviwe_date as x_hr_interviwe_date,
# 		applicant.user_id as x_recruiter,
# 		applicant.sales_experience as x_sales_experience,
# 		applicant.years_of_experience as x_years_of_experience,
# 		applicant.first_interview_feedback as x_first_interview_feedback,
# 		applicant.first_interview_feedback_reason as x_first_interview_feedback_reason,
# 		applicant.sector as x_sector,
# 		applicant.project as x_project,
# 		applicant.second_interview_feedback as x_second_interview_feedback,
# 		applicant.second_interview_feedback_reason as x_second_interview_feedback_reason,
# 		applicant.english_test_result as x_english_test_result,
# 		applicant.pronunciation as x_pronunciation,
# 		applicant.grammer as x_grammer,
# 		applicant.fluency as x_fluency,
# 		applicant.understanding_vocab as x_understanding_vocab,
# 		applicant.typing_test_result as x_typing_test_result,
# 		CASE WHEN applicant.job_offer_feedback = 'accepted' THEN 'Yes'
#          ELSE 'No' END AS x_job_offer_feedback,
# 		applicant.job_offer_feedback_reason as x_job_offer_feedback_reason,
# 		applicant.hired as x_hired,
# 		applicant.date_of_hiring as x_date_of_hiring,
# 		applicant.date_of_signing as x_date_of_signing,
# 		applicant.reason_if_not_hired as x_reason_if_not_hired,
# 		applicant.sector_projects_type as x_sector_projects_type
# 		from hr_applicant applicant
# 		where job_category = 'operational' and active = true
# -- 		inner join res_partner partner on applicant.partner_id = partner.id and applicant.job_category = 'operational'
# -- 		inner join res_country country on applicant.nationality = country.id
# -- 		inner join res_country_state state_id on applicant.state = state_id.id
# -- 		inner join city_area area_id on applicant.area = area_id.id
# -- 		inner join hr_institute university_id on applicant.university = university_id.id
# -- 		inner join university_fac faculty_id on applicant.faculty = faculty_id.id
# -- 		inner join utm_source source_id on applicant.source_id = source_id.id
# -- 		inner join res_users recruit_id on applicant.user_id = recruit_id.id
# -- 		inner join interview_feedback interview_feedback_reason_id on applicant.first_interview_feedback_reason = interview_feedback_reason_id.id
# -- 		inner join  hiring_request request on applicant.hiring_request = request.id
# -- 		inner join rcc_project project_id on applicant.project = project_id.id
# -- 		inner join interview_feedback sec_interview_feedback_reason_id on applicant.second_interview_feedback_reason = sec_interview_feedback_reason_id.id
# -- 		inner join interview_feedback job_offer_feedback_reason on applicant.job_offer_feedback_reason = job_offer_feedback_reason.id
# -- 		inner join interview_feedback reason_if_not_hired on applicant.reason_if_not_hired = reason_if_not_hired.id
#
#                 """)
#         return query
#
#     def _prepare_model_btn(self):
#         print("_prepare_model_btn")
#         field_id = []
#         field_ids = []
#         columns = [(1, 'x_create_date', 'timestamp without time zone'), (2, 'x_job_code', 'integer'), (3, 'x_applicant_name', 'character varying'), (4, 'x_phone', 'character varying(32)'), (5, 'x_national_id', 'character varying(14)'), (6, 'x_nationality', 'character varying'), (7, 'x_gender', 'character varying'), (8, 'x_age', 'integer'), (9, 'x_governorate', 'character varying'), (10, 'x_city_area', 'character varying'), (11, 'x_military_status', 'character varying'), (12, 'x_graduation_status', 'character varying'), (13, 'x_university', 'character varying'), (14, 'x_faculty', 'character varying'), (15, 'x_social_insurance', 'character varying'), (16, 'x_email', 'character varying(128)'), (17, 'x_pc_laptop', 'character varying'), (18, 'x_internet_con', 'character varying'), (19, 'x_con_speed', 'character varying'), (20, 'x_internet_provider', 'character varying'), (21, 'x_indebendancy', 'character varying'), (22, 'x_prev_work_experience', 'character varying'), (23, 'x_prev_work_experience_what', 'character varying'), (24, 'x_why_leave', 'character varying'), (25, 'x_why_join', 'character varying'), (26, 'x_salary_expections', 'character varying'), (27, 'x_relational_shifts', 'character varying'), (28, 'x_english_level', 'character varying'), (29, 'x_worked_4_raya', 'character varying'), (30, 'x_ready_work_from_home', 'character varying'), (31, 'x_operating_sys', 'character varying'), (32, 'x_main_source', 'character varying'), (33, 'x_source', 'character varying'), (34, 'x_recruiter', 'character varying'), (35, 'x_hr_interviwe_date', 'date'), (36, 'x_sales_experience', 'character varying'), (37, 'x_years_of_experience', 'integer'), (38, 'x_first_interview_feedback', 'character varying'), (39, 'x_interview_feedback_reason', 'character varying'), (40, 'x_sector', 'character varying'), (41, 'x_project', 'character varying'), (42, 'x_second_interview_feedback', 'character varying'), (43, 'x_second_interview_feedback_reason', 'character varying'), (44, 'x_english_test_result', 'character varying'), (45, 'x_pronunciation', 'integer'), (46, 'x_grammer', 'integer'), (47, 'x_fluency', 'integer'), (48, 'x_understanding_vocab', 'integer'), (49, 'x_typing_test_result', 'character varying'), (50, 'x_job_offer_feedback', 'text'), (51, 'x_date_of_signing', 'timestamp without time zone'), (52, 'x_job_offer_feedback_reason', 'character varying'), (53, 'x_hired', 'character varying'), (54, 'x_date_of_hiring', 'timestamp without time zone'), (55, 'x_reason_if_not_hired', 'character varying'), (56, 'x_sector_projects_type', 'character varying')]
#         for column in columns:
#             if column[1][:2] == "x_":
#                 field_ids.append({
#                             "sequence": column[0],
#                             "name": column[1],
#                             "sql_type": column[2],
#                         })
#                 self._FIELDS.append({
#                             "sequence": column[0],
#                             "name": column[1],
#                             "sql_type": column[2],
#                         })
#         for field in field_ids:
#             ttype = False
#             for k, v in self._SQL_MAPPING.items():
#                 if k in field["sql_type"]:
#                     ttype = v
#             field_id.append((0, 0, {
#                 "name": field['name'],
#                 "field_description": field['name'],
#                 "model_id": False,
#                 "ttype": ttype,
#                 "selection": False,
#                 "relation": False,
#             }))
#         return {
#             "name": 'x_wc_recruitment_daily_report_sql', # Description Of Model
#             "model": "x_wc_recruitment_daily_report_sql" , # technical_name
#             "access_ids": [],
#             "order": 'id asc',
#             "field_id": field_id, # Fields
#         }
#     def _prepare_rule_btn(self, model_id=None):
#         print("_prepare_rule_btn")
#         return {
#             "name": _("Access %s") % 'x_wc_recruitment_daily_report_sql',
#             "model_id": model_id,
#             "global": True,
#         }
#     def _log_execute_btn(self, req):
#         print("_log_execute_btn")
#         _logger.info("Executing SQL Request %s ..." % req)
#         self.env.cr.execute(req)
#     def _create_model_access(self):
#         print("_create_model_access")
#         for item in self._prepare_model_access_btn(self.env['ir.model'].search([('model','=','x_wc_recruitment_daily_report_sql')]).id):
#             self.env["ir.model.access"].create(item)
#     def _prepare_model_access_btn(self,model_id=None):
#         print("_prepare_model_access_btn")
#         res = []
#         group_id = self.env.ref('base.group_user').id
#         group_name = self.env.ref('base.group_user').full_name
#         res.append(
#             {
#                 "name": _("%s Access %s") % ("x_wc_recruitment_daily_report_sql", group_name),
#                 "model_id": model_id,
#                 "group_id": group_id,
#                 "perm_read": True,
#                 "perm_create": True,
#                 "perm_write": False,
#                 "perm_unlink": False,
#             }
#         )
#         return res
#
#     def _create_view_btn(self):
#         print("_create_view_btn")
#
#         self._drop_view_btn()
#         try:
#             self._log_execute_btn(self._prepare_request_for_execution_btn())
#         except ProgrammingError as e:
#             raise UserError(
#                 _("SQL Error while creating %s VIEW %s :\n %s")
#                 % ("", "x_wc_recruitment_daily_report_sql", str(e))
#             )
#     def _drop_view_btn(self):
#         print("_drop_view_btn")
#
#         print("******************************")
#         print("DROP %s VIEW IF EXISTS %s"
#         % ("", "x_wc_recruitment_daily_report_sql"))
#         print("******************************")
#
#         self._log_execute_btn(
#             "DROP %s VIEW IF EXISTS %s"
#             % ("", "x_wc_recruitment_daily_report_sql")
#         )
#     def _prepare_request_for_execution_btn(self):
#         print("_prepare_request_for_execution_btn")
#         xquery = (""" select  row_number() OVER () as id,
# 		applicant.create_date as x_create_date,
# 	  	applicant.job_code as x_job_code,
# 		applicant.partner_name as x_applicant_name,
# 		applicant.partner_phone as x_phone,
# 		applicant.national_id as x_national_id,
# 		applicant.nationality as x_nationality,
# 		applicant.gender as x_gender,
# 		applicant.age as x_age,
# 		applicant.state as x_governorate,
# 		applicant.area as x_city_area,
# 		applicant.military_status as x_military_status,
# 		applicant.graduation_status as x_graduation_status,
# 		applicant.university as x_university,
# 		applicant.faculty as x_faculty,
# 		applicant.social_insurance as x_social_insurance,
# 		applicant.email_from as x_email,
# 		applicant.pc_laptop as x_pc_laptop,
# 		applicant.internet_con as x_internet_con,
# 		applicant.con_speed as x_con_speed,
# 		applicant.internet_provider as x_internet_provider,
# 		applicant.indebendancy as x_indebendancy,
# 		applicant.prev_work_experience as x_prev_work_experience,
# 		applicant.prev_work_experience_what as x_prev_work_experience_what,
# 		applicant.why_leave as x_why_leave,
# 		applicant.why_join as x_why_join,
# 		applicant.salary_expections as x_salary_expections,
# 		applicant.rotational_shifts as x_relational_shifts,
# 		applicant.english_status as x_english_level,
# 		applicant.worked_4_raya as x_worked_4_raya,
# 		applicant.ready_work_from_home as x_ready_work_from_home,
# 		applicant.operating_sys as x_operating_sys,
# 		applicant.main_source as x_main_source,
# 		applicant.source_id as x_source,
# 		applicant.hr_interviwe_date as x_hr_interviwe_date,
# 		applicant.user_id as x_recruiter,
# 		applicant.sales_experience as x_sales_experience,
# 		applicant.years_of_experience as x_years_of_experience,
# 		applicant.first_interview_feedback as x_first_interview_feedback,
# 		applicant.first_interview_feedback_reason as x_first_interview_feedback_reason,
# 		applicant.sector as x_sector,
# 		applicant.project as x_project,
# 		applicant.second_interview_feedback as x_second_interview_feedback,
# 		applicant.second_interview_feedback_reason as x_second_interview_feedback_reason,
# 		applicant.english_test_result as x_english_test_result,
# 		applicant.pronunciation as x_pronunciation,
# 		applicant.grammer as x_grammer,
# 		applicant.fluency as x_fluency,
# 		applicant.understanding_vocab as x_understanding_vocab,
# 		applicant.typing_test_result as x_typing_test_result,
# 		CASE WHEN applicant.job_offer_feedback = 'accepted' THEN 'Yes'
#          ELSE 'No' END AS x_job_offer_feedback,
# 		applicant.job_offer_feedback_reason as x_job_offer_feedback_reason,
# 		applicant.hired as x_hired,
# 		applicant.date_of_hiring as x_date_of_hiring,
# 		applicant.date_of_signing as x_date_of_signing,
# 		applicant.reason_if_not_hired as x_reason_if_not_hired,
# 		applicant.sector_projects_type as x_sector_projects_type
# 		from hr_applicant applicant
# 		where job_category = 'operational' and active = true
# -- 		inner join res_partner partner on applicant.partner_id = partner.id and applicant.job_category = 'operational'
# -- 		inner join res_country country on applicant.nationality = country.id
# -- 		inner join res_country_state state_id on applicant.state = state_id.id
# -- 		inner join city_area area_id on applicant.area = area_id.id
# -- 		inner join hr_institute university_id on applicant.university = university_id.id
# -- 		inner join university_fac faculty_id on applicant.faculty = faculty_id.id
# -- 		inner join utm_source source_id on applicant.source_id = source_id.id
# -- 		inner join res_users recruit_id on applicant.user_id = recruit_id.id
# -- 		inner join interview_feedback interview_feedback_reason_id on applicant.first_interview_feedback_reason = interview_feedback_reason_id.id
# -- 		inner join  hiring_request request on applicant.hiring_request = request.id
# -- 		inner join rcc_project project_id on applicant.project = project_id.id
# -- 		inner join interview_feedback sec_interview_feedback_reason_id on applicant.second_interview_feedback_reason = sec_interview_feedback_reason_id.id
# -- 		inner join interview_feedback job_offer_feedback_reason on applicant.job_offer_feedback_reason = job_offer_feedback_reason.id
# -- 		inner join interview_feedback reason_if_not_hired on applicant.reason_if_not_hired = reason_if_not_hired.id
#
#                 """)
#         query = (
#             """
#             SELECT
#                 CAST(row_number() OVER () as integer) AS id,
#                 CAST(Null as timestamp without time zone) as create_date,
#                 CAST(Null as integer) as create_uid,
#                 CAST(Null as timestamp without time zone) as write_date,
#                 CAST(Null as integer) as write_uid,
#                 my_query.*
#             FROM
#                 (%s) as my_query
#         """
#             %  xquery
#         )
#
#         print("##############################")
#         print("CREATE {} VIEW {} AS ({});".format(
#             "", "x_wc_recruitment_daily_report_sql", query,
#         ))
#         print("##############################")
#
#         return "CREATE {} VIEW {} AS ({});".format(
#             "", "x_wc_recruitment_daily_report_sql", query,
#         )
#     def _refresh_size_btn(self):
#         print("_refresh_size_btn")
#         req = "SELECT pg_size_pretty(pg_total_relation_size('%s'));" % (
#             "x_wc_recruitment_daily_report_sql"
#         )
#
#     def _prepare_tree_field_btn(self, field={}):
#         print("_prepare_tree_field_btn")
#         res = ""
#         if field['name']:
#             res = """<field name="{}"/>""".format(
#                 field['name']
#             )
#         return res
#     def _prepare_tree_view_btn(self):
#         print("_prepare_tree_view_btn")
#         return {
#             "name": 'x_wc_recruitment_daily_report_sql_tree',
#             "type": "tree",
#             "model": 'x_wc_recruitment_daily_report_sql',
#             "arch": """<?xml version="1.0"?>"""
#             """<tree string="Analysis">{}"""
#             """</tree>""".format(
#                 "".join([self._prepare_tree_field_btn(x) for x in self._FIELDS])
#             ),
#         }
#     def _prepare_action_btn(self, tree_view_id=None):
#         print("_prepare_action_btn")
#         return {
#             "name": self._prepare_action_name_btn(),
#             "res_model": 'x_wc_recruitment_daily_report_sql',
#             "type": "ir.actions.act_window",
#             "view_mode": 'tree',
#             "view_id": tree_view_id,
#         }
#     def _prepare_action_name_btn(self):
#         print("_prepare_action_name_btn")
#         return "{} ({})".format(
#             'x_wc_recruitment_daily_report_sq++++++s', datetime.utcnow().strftime(_("%m/%d/%Y %H:%M:%S UTC")),
#         )
#
#     def _prepare_menu_btn(self, action_id=None):
#         print("_prepare_menu_btn")
#         return {
#             "name": 'x_wc_recruitment_daily_report_sql_menu',
#             "action": action_id,
#         }
#     def button_create_ui_btn(self):
#         print("button_create_ui_btn")
#         tree_view_id = self.env["ir.ui.view"].create(self._prepare_tree_view_btn()).id
#         action_id = self.env["ir.actions.act_window"].create(self._prepare_action_btn(tree_view_id)).id
#         menu_vals = self._prepare_menu_btn(action_id)
#         menu_id = self.env["ir.ui.menu"].create(menu_vals).id
