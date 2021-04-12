# -*- coding: utf-8 -*-

from odoo import models,exceptions,fields, api,_
from datetime import date
from datetime import datetime
from dateutil.relativedelta import relativedelta
from datetime import timedelta
from odoo.exceptions import ValidationError,UserError
import http.client
import json
import tempfile
import xlrd
import binascii
import logging
import io
from odoo.exceptions import Warning

class ISAgency(models.Model):
    _inherit = 'res.partner'
    is_agency = fields.Boolean(string="Is Agency ")

class AgenciesData(models.Model):
    _name = 'agency.data'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name= fields.Char(string="Agency Code")
    agency_name =  fields.Char(string="Agency Name")
    pin_code = fields.Char(string="Agency PIN Code")
    partner_id = fields.Many2one('res.partner',string="Related Partners")

class USERS(models.Model):
    _inherit = 'res.users'
    is_agency = fields.Boolean(string="Is Agency ")

class EMPLOYEE(models.Model):
    _inherit = 'hr.employee'
    hiring_date = fields.Date(string="Hiring Date",required=True)

    @api.model
    def create(self, vals):
        res = super(EMPLOYEE, self).create(vals)
        vals['hiring_date'] = date.today()
        return res
        
class APPLICANT(models.Model):
    _inherit = 'hr.job'
    address_id = fields.Many2one('res.partner',domain="['|',('type','=','contact'),('type','=','private'),('company_type','=','company')]")
    
class APPLICANT(models.Model):
    _inherit = 'hr.applicant'
    agency = fields.Many2one('agency.data',string=" Agency ")
    agency_name = fields.Char(string=" Agency Name ")
    text_area = fields.Char("Area from Agency import")
    text_age = fields.Char("Age from Agency")
    text_faculty =  fields.Char("Faculty from Agency")
    text_project = fields.Char("Agency Recommended Project")
    
    
    a50_certified = fields.Selection([('eligible','Eligible'),('not_eligible','Not Eligible')],'50% Certified')
    a50_certified_payment = fields.Boolean('50% Certified Paid', default = False)
    a50a90_days_hired = fields.Selection([('eligible','Eligible'),('not_eligible','Not Eligible')],'50% 90 Days Hired')
    a50a90_days_hired_payment = fields.Boolean('50% 90 Days Hired Paid', default = False)

class AgencyPayment(models.Model):
    _name = 'agency_payment'
    _description = 'agency_payment'
    _auto = False

    id = fields.Integer()
    partner_name = fields.Char()
    applicant_name = fields.Char()
    job_id = fields.Many2one('hr.job')
    agency = fields.Many2one('agency.data')
    project = fields.Many2one('rcc.project')
    sector = fields.Many2one('sector.sector')
    user_id = fields.Many2one('res.users')
    a50_certified = fields.Selection([('eligible','Eligible'),('not_eligible','Not Eligible'),('paid','Paid')],'50% Certified')
    a50a90_days_hired = fields.Selection([('eligible','Eligible'),('not_eligible','Not Eligible'),('paid','Paid')],'50% 90 Days Hired')

    def init(self):
        """ Agency Payment report """
        self.env.cr.execute('DROP VIEW IF EXISTS agency_payment')
        self.env.cr.execute(""" CREATE VIEW agency_payment AS (
            SELECT row_number() OVER () as id,
            partner_name as partner_name,
            name as applicant_name,
            job_id as job_id,
            agency as agency,
            project as project,
            sector as sector,
            user_id as user_id,
            CASE WHEN applicant.a50_certified_payment = true THEN 'paid'
            ELSE applicant.a50_certified
            END as a50_certified,
            CASE WHEN applicant.a50a90_days_hired_payment = true THEN 'paid'
            ELSE applicant.a50a90_days_hired
            END as a50a90_days_hired
            FROM hr_applicant applicant
            WHERE agency is not null
            AND job_category = 'operational'
            AND (applicant.a50_certified_payment = false OR applicant.a50a90_days_hired_payment = false)
            AND active = True
            ) """)


class AgencyWizard(models.TransientModel):
    _name = "agency.import_wizard"
    _description= 'Agency Import Applications'

    agency = fields.Many2one('agency.data', string = "Select Your Agency")
    pin = fields.Char(string = "Enter your PIN Code")
    file = fields.Binary('File')
    job_id = fields.Many2one('hr.job',domain="[('job_category','=','operational')]",string = "Select job")
    hiring_request = fields.Many2one('hiring.request',domain="[('category','=','operational'),('job','=',job_id)]",string="Select Hiring Request ")

    def import_data(self):
        if self.agency.id:
            if self.pin:
                if self.pin != self.agency.pin_code:
                    raise ValidationError(_('Please Enter Valid Bin Code.'))
                else:
#                    try:
                    fp = tempfile.NamedTemporaryFile(delete= False,suffix=".xlsx")
                    fp.write(binascii.a2b_base64(self.file))
                    fp.seek(0)
                    values = {}
                    workbook = xlrd.open_workbook(fp.name)
                    sheet = workbook.sheet_by_index(0)

                    for row_no in range(sheet.nrows):
                        if row_no <= 0:
                            fields = map(lambda row:row.value.encode('utf-8'), sheet.row(row_no))
                            print("Field Name")
                        else:
                            line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
                            values.update( {'name':line[0],
                                            'partner_phone': line[1],
                                            'national_id': line[2],
                                            'text_age': line[3],
                                            'text_area': line[6],
                                            'military_status': line[7],
                                            'graduation_status': line[4],
                                            'text_faculty': line[5],
                                            'english_status': line[8],
                                            'text_project':line[9],
                                            })
                                            
                            res = self._create_timesheet(values)
                            
            else:
                raise ValidationError(_('Please use the correct excel format!'))


    def _create_timesheet(self,val):
        job_id = self.job_id.id
        hiring_request_id = ''
        batch_numbers = 0
        if self.hiring_request.id:
            hiring_request_id = self.hiring_request.id
            batch_numbers = self.hiring_request.batch_numbers    
        kanban_state = "normal"
        referral_state = "progress"
        agency = self.agency.id

        gender = val.get('gender')
        if gender:
            if gender == "Male":
                gender = "male"
            elif gender == "Female":
                gender = "female"
            else:
                raise exceptions.Warning(_('Please use correct Graduation Status, use Male or Female.'))
            
        area = val.get('text_area')

        military_status = val.get('military_status')
        if military_status:
            if military_status =="Completed":
                military_status = "Completed"
            elif military_status =="Will serve":
                military_status = "Will serve"
            elif military_status =="Exempted":
                military_status = "Exempted"
            elif military_status =="Postponed":
                military_status = "Postponed"
            elif military_status =="Female":
                military_status = "Female"
            else:
                raise ValidationError('Please use correct military status Status, use Completed or Will serve or Exempted or Postponed or Female .')
        graduation_status = val.get('graduation_status')
        print("FGGGGGGGGGGGGGGGGGGGGGGG")
        print("FGGGGGGGGGGGGGGGGGGGGGGG")
        print(graduation_status)
        print("FGGGGGGGGGGGGGGGGGGGGGGG")
        print("FGGGGGGGGGGGGGGGGGGGGGGG")
        
        if graduation_status: 
            if graduation_status =="Graduated":
                graduation_status = "graduated"
            elif graduation_status =="Under Grade":
                graduation_status = "notgraduated"
            else:
                raise ValidationError('Please use correct Graduation Status, use Graduated or Under Grade.')
                

        faculty =  val.get('text_faculty')


        english_status = val.get('english_status')
        if english_status: 
            if english_status =="Fluent":
                english_status = "Fluent"
            elif english_status =="Excellent":
                english_status = "Excellent"
            elif english_status =="V.Good":
                english_status = "V.Good"
            elif english_status =="Fair":
                english_status = "Fair"
            elif english_status =="Good":
                english_status = "Good"
            else:
                raise ValidationError('Please use correct English level, use  Fluent	or Excellent or V.Good or Good	or Fair')


        name = val.get('name')
        national_id = val.get('national_id')
        age = val.get('text_age')
        email_from = val.get('email_from')
        partner_phone = val.get('partner_phone')
        agency = self.agency.id
        stage_id = self.env['hr.recruitment.stage'].search([('is_o_initial','=',True)],limit=1)

        print("############ Values ###################")
        
        try:
            self.env['hr.applicant'].create({
                "name":name,
                "partner_name":name,
                "job_category":"operational",
                "stage_id":1,
                "job_id":job_id,
                "national_id":national_id,
                "email_from":name,
                "partner_phone":partner_phone,
                'text_age': age,
                'text_area': area,
                'military_status':military_status,
                'graduation_status':graduation_status,
                'text_faculty': faculty,
                'english_status': english_status,
                'text_project' : val.get('text_project'),
                "agency" : agency,
                "kanban_state":kanban_state,
                "hiring_request":hiring_request_id,
                "job_id":job_id,
                "batch_numbers":batch_numbers,
                "agency_name":self.agency.agency_name,
              #  "referral_state":referral_state
            })
        
            return True
        except Exception:
            raise ValidationError('Please use the correct excel format!')