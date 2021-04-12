# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from datetime import date
from datetime import datetime
from dateutil.relativedelta import relativedelta
from datetime import timedelta
from odoo.exceptions import ValidationError,UserError
import http.client
import json

class HrApplicantAPI(models.Model):
    _inherit = 'hr.applicant'
    apply_survey_id = fields.Many2one('survey.survey', related='job_id.apply_survey_id', string="Apply Survey")
    response_apply_id = fields.Many2one('survey.user_input', "Response Apply", ondelete="set null")
    black_listed = fields.Boolean('Is Blacklisted')
    def conf_blacklist(self):
        return {
            'name': _('Attention'),
            'view_mode': 'form',
            'res_model': 'blacklist.warning.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new'
        }
    def conf_un_blacklist(self):
        return {
            'name': _('Attention'),
            'view_mode': 'form',
            'res_model': 'unblacklist.warning.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new'
        }
    def do_blacklist(self):
        applicant = self.env['hr.applicant'].search([('national_id','=',self.national_id)])
        for app in applicant:
            app.write({'black_listed':True})
            app.partner_id.blacklisted = True
    def do_un_blacklist(self):
        applicant = self.env['hr.applicant'].search([('national_id','=',self.national_id)])
        for app in applicant:
            app.write({'black_listed':False})
            app.partner_id.blacklisted = False

    @api.model
    def create(self, values):
        res = super(HrApplicantAPI, self).create(values)
        if values['partner_phone']:
            if values['partner_phone'].isnumeric() == False:
                raise ValidationError(_("Mobile Number Must Contain numbers only."))
                return
                
        emp = self.env['hr.employee'].search([('identification_id','=',values['national_id'])])
        if emp:
            national_id = values['national_id']
            is_egyption = "true"
            date_from = "2020-12-01"
            date_to = "2021-03-18"
            
            conn = http.client.HTTPSConnection("recruitment-api.rayacx.com")
            payload = ''
            headers = {'Authorization': 'Bearer W9OUSNrAOWDlZlYWoKOHSB9OTGdszSKobtdwoaqduEaOuct9ykv4EiIfpe0hsFVYge-4Y_INQ4tfKj0sCsO4uOaBsbOkud9FLNpzhlnI_nFCXL7ILHdVh8no3IRkLaRI1cgP1z4HK2qoCytXMo66o04NYpvlb-PtdtCzt32oETjRugNZEQwuMk2-kf3h3FsFj9vKvXsuGwGG5LH5ay9S5A'}
            conn.request("GET", "/api/cz/GetKPI?IsEgyptian="+is_egyption+"&RefId="+national_id+"&DateFrom="+date_from+"&DateTo="+date_to, payload, headers)
            ress = conn.getresponse()
            data = ress.read()
            dict_data = json.loads(data.decode('utf-8'))
            kpi_average = 0
            
            if dict_data:
                for i in dict_data:
                    try:
                        if str(i["kpi"]):
                            kpi_average += float(str(i["kpi"]))
                    except:
                        pass
                kpi_average = kpi_average/300
                print("KPI Average")
                print("KPI Average")
                print(kpi_average)
                print("KPI Average")
                print("KPI Average")
                
                kpi_float = str(kpi_average * 100).split('.')[0]
                print("Kpi Average")
                print(kpi_float)
                print(emp)
                emp.write({'kpi_average':int(kpi_float)})
                #return
                print(emp.kpi_average)
                print("Kpi Average")
                
                
                if float(kpi_average) < 0.51 :
                    raise ValidationError(_("Your KPI doesnt meet the Requirements. "))
                    emp.write({'Applicable':False})
                    return
            else:
                # KPI Online Restriction
                if emp.kpi_average:
                    if int(emp.kpi_average) < 51 :
                        raise ValidationError(_("Your KPI doesnt meet the Requirements"))
                        emp.write({'Applicable':False})
                        return
            #Grade Online Restriction
            
            if emp.employee_grade:
                job_obj = self.env['hr.job'].search([('id','=',values['job_id'])])
                grade_obj =  self.env['employee.grade'].search([('id','=',emp.employee_grade.id)])
                max_emp_grade = int(grade_obj.garde) + int(grade_obj.grade_level_exception)
                max_job_grade = int(job_obj.employee_grade.garde) # int(job_obj.employee_grade.grade_level_exception)

                if max_emp_grade < max_job_grade:
                    raise ValidationError(_("Your Grade doesn't meet the Requirements"))
                    return
                    
            
            
            # Head Count Online Restriction
            if emp:
                #KPI
                conn = http.client.HTTPSConnection("recruitment-api.rayacx.com")
                payload = ''
                headers = {'Authorization': 'Bearer W9OUSNrAOWDlZlYWoKOHSB9OTGdszSKobtdwoaqduEaOuct9ykv4EiIfpe0hsFVYge-4Y_INQ4tfKj0sCsO4uOaBsbOkud9FLNpzhlnI_nFCXL7ILHdVh8no3IRkLaRI1cgP1z4HK2qoCytXMo66o04NYpvlb-PtdtCzt32oETjRugNZEQwuMk2-kf3h3FsFj9vKvXsuGwGG5LH5ay9S5A'}
                conn.request("GET", "/api/cz/GetEmpHeadcount?IsEgyptian="+is_egyption+"&RefId="+national_id, payload, headers)
                ress = conn.getresponse()
                data = ress.read()
                dict_data = json.loads(data.decode('utf-8'))
                GetEmpHeadcount = 0
                print("HEAD Count ")
                print("HEAD Count ")
                print("HEAD Count ")
                print("HEAD Count ")
                
                print(dict_data)
                
                print("Head Count")
                print("HEAD Count ")
                print("HEAD Count ")
                print("HEAD Count ")
                print("HEAD Count ")
                if dict_data:
                    #for i in dict_data:
                    job_head_count = self.env['hr.job'].sudo().search([('id','=',values['job_id'])]).head_count_restriction                        
                    print("i")
                    
                    print("i")
                    last_emp_head_count = dict_data["headcount_Date"]
                    emp_head_count_date = dict_data["headcount_Date"].split('T')[0]
                    
                    if last_emp_head_count:
                        emp_head_count_date = datetime.strptime(emp_head_count_date,'%Y-%m-%d') 
                        print(emp_head_count_date)
                        print(emp_head_count_date)
                        print(emp_head_count_date)
                        emp_head_count_date =  emp_head_count_date+ timedelta(days=(int(job_head_count)*30))
                        print(emp_head_count_date)
                        if emp_head_count_date > datetime.now():
                            raise ValidationError(_("Your Last Head Count doesn't meet the Requirements"))
                            return False
                else:
                    job_head_count = self.env['hr.job'].search([('id','=',values['job_id'])]).head_count_restriction
                    last_emp_head_count = self.env['head.count.line'].search([('emp_id','=',emp.id)],order='id desc',limit=1)
                    if last_emp_head_count:
                        emp_head_count_date = last_emp_head_count.date + relativedelta(months=+int(job_head_count))
                        if emp_head_count_date > date.today():
                            raise ValidationError(_("Your Last Head Count doesn't meet the Requirements"))
                            return False
                            
            conn = http.client.HTTPSConnection("recruitment-api.rayacx.com")
            payload = ''
            headers = {'Authorization': 'Bearer W9OUSNrAOWDlZlYWoKOHSB9OTGdszSKobtdwoaqduEaOuct9ykv4EiIfpe0hsFVYge-4Y_INQ4tfKj0sCsO4uOaBsbOkud9FLNpzhlnI_nFCXL7ILHdVh8no3IRkLaRI1cgP1z4HK2qoCytXMo66o04NYpvlb-PtdtCzt32oETjRugNZEQwuMk2-kf3h3FsFj9vKvXsuGwGG5LH5ay9S5A'}
            
            conn.request("GET", "/api/cz/CheckBlackliste?IsEgyptian="+is_egyption+"&RefId="+national_id+"&DateFrom="+date_from+"&DateTo="+date_to, payload, headers)
            ress = conn.getresponse()
            data = ress.read()
            dict_data = json.loads(data.decode('utf-8'))
            
            
            #if dict_data:
            #    is_blacklisted_api = dict_data[0]
                
            #    print("is_blacklisted_api")
            #    print(is_blacklisted_api)
            #    print(dict_data)
            #    print("is_blacklisted_api")
                
            #    if is_blacklisted_api == "true":
            #        self.env['res.partner'].search([('national_id','ilike',values['national_id'])]).write({'blacklisted':True})
        
            # Misconduct Online Restriction
            if emp:            
                conn = http.client.HTTPSConnection("recruitment-api.rayacx.com")
                payload = ''
                headers = {'Authorization': 'Bearer W9OUSNrAOWDlZlYWoKOHSB9OTGdszSKobtdwoaqduEaOuct9ykv4EiIfpe0hsFVYge-4Y_INQ4tfKj0sCsO4uOaBsbOkud9FLNpzhlnI_nFCXL7ILHdVh8no3IRkLaRI1cgP1z4HK2qoCytXMo66o04NYpvlb-PtdtCzt32oETjRugNZEQwuMk2-kf3h3FsFj9vKvXsuGwGG5LH5ay9S5A'}
                conn.request("GET", "/api/cz/GetEmpMisconduct?IsEgyptian="+is_egyption+"&RefId="+national_id, payload, headers)
                ress = conn.getresponse()
                data = ress.read()
                dict_data = json.loads(data.decode('utf-8'))
                GetEmpMisconduct = 0
                print("Misconduct")
                print("Misconduct")
                print(dict_data)
                print("Misconduct")
                print("Misconduct")
                if dict_data:
                    for i in dict_data:
                        print(dict_data)
                        last_emp_miconduct_count = str(i["date"])
                        emp_misconduct_date = str(i["date"]).split('T')[0]
                        if i["type"] == "Warning":
                            if last_emp_miconduct_count:
                                #misconduct_period = last_emp_miconduct_count.misconduct_type_id.applying_restriction
                                miconduct_employee_date = datetime.strptime(emp_misconduct_date,'%Y-%m-%d')
                                emp_misconduct_date = miconduct_employee_date + timedelta(days=+90)
                                if emp_misconduct_date > datetime.now():
                                    emp.write({'Applicable':False})
                                    raise ValidationError(_("You have Misconducts that contradicts with the Requirements"))
                                    return False
                        if i["type"] == "Fine":
                            if last_emp_miconduct_count:
                                #misconduct_period = last_emp_miconduct_count.misconduct_type_id.applying_restriction
                                miconduct_employee_date = datetime.strptime(emp_misconduct_date,'%Y-%m-%d')
                                emp_misconduct_date = miconduct_employee_date + timedelta(days=+30)
                                if emp_misconduct_date > datetime.now():
                                    emp.write({'Applicable':False})
                                    raise ValidationError(_("You have Misconducts that contradicts with the Requirements"))
                                    return False
                        if i["type"] == "Pay attention":
                        
                            if last_emp_miconduct_count:
                                #misconduct_period = last_emp_miconduct_count.misconduct_type_id.applying_restriction
                                miconduct_employee_date = datetime.strptime(emp_misconduct_date,'%Y-%m-%d')
                                emp_misconduct_date = miconduct_employee_date + timedelta(days=+30)
                                if emp_misconduct_date > datetime.now():
                                    emp.write({'Applicable':False})
                                    raise ValidationError(_("You have Misconducts that contradicts with the Requirements"))
                                    return False
        #        #Get Last Misconduct for This emp
        #        else:
        #            last_emp_miconduct_count = self.env['employee.misconduct.line'].search([('emp_id','=',emp.id)],order='id desc',limit=1)
        #            if last_emp_miconduct_count:
        #            #Get Misconduct period
        #                misconduct_period = last_emp_miconduct_count.misconduct_type_id.applying_restriction
        #                #Get Date from misconduct on emploee
        #                miconduct_employee_date = last_emp_miconduct_count.date
        #                emp_misconduct_date = miconduct_employee_date + relativedelta(months=+int(misconduct_period))
        #                if emp_misconduct_date > date.today():
        #                    raise ValidationError(_("You have Misconducts that contradicts with the Requirements"))
        #                    return
        
                
        isblack = self.env['res.partner'].search([('national_id','ilike',values['national_id']),('active','=',True),('blacklisted','=',True)])
        if emp:
            emp.write({'Applicable':True})
        if len(isblack)>0:
            # res.is_hold=True
            applicant = self.env['hr.applicant'].search([('national_id','ilike',values['national_id'])])
            for app in applicant:
                app.write({'black_listed':True})
            res.black_listed = True
            res.partner_id.blacklisted = True
        else:
            # res.is_hold=False
            applicant = self.env['hr.applicant'].search([('national_id','ilike',values['national_id'])])
            for app in applicant:
                app.write({'black_listed':False})
            res.black_listed = False
            res.partner_id.blacklisted = False

        if res.job_category=='talent':
            stage_line=self.env['hr.recruitment.stage'].search([('job_category','=','talent'),('is_initial','=',True)],limit=1)
            res.stage_id=stage_line.id
        elif res.job_category=='operational':
            stage_line=self.env['hr.recruitment.stage'].search([('job_category','=','operational'),('is_o_initial','=',True)],limit=1)
            res.stage_id=stage_line.id
        if not res.job_id.user_id:
            res.user_id = 1
        return res
        
    @api.onchange('stage_id')
    def blacklisted_rest_fun(self):
        if self.stage_id and self.black_listed:
            raise UserError(_('This Applicant is Blacklisted and on Hold'))

class HrJobSurvey(models.Model):
    _inherit = 'hr.job'
    apply_survey_id = fields.Many2one('survey.survey',  string="Apply Survey")

class ISBlackListed(models.Model):
    _inherit = 'res.partner'
    blacklisted = fields.Boolean()
    dob = fields.Date("Date of birth")
    gender = fields.Selection([('male','Male'),('female','Female')],string="Gender")
    military_status = fields.Selection([('Completed','Completed')
        ,('Will serve','Will serve')
        ,('Exempted','Exempted')
        ,('Postponed','Postponed')
        ,('Female','Female')],string="Military Status")
    
    
    # compute="_compute_blacklisted_state"
    # def _compute_blacklisted_state(self):
    #     for this in self:
    #         if this.national_id:
    #             applicant = this.env['hr.applicant'].search([('national_id','=',this.national_id)])
    #             applicant_blacklisted = applicant.filtered(lambda x:x.black_listed == True)
    #             if len(applicant_blacklisted) > 0:
    #                 this.blacklisted = True
    #             else:
    #                 this.blacklisted = False
    #         else:
    #             this.blacklisted = False


    # def block_user(self):
    #     print(self)
    #     # self.blacklisted = True
    #     self.write({'blacklisted':True})
    #
    # def un_block_user(self):
    #     # self.is_blacklisted = False
    #     self.write({'blacklisted':False})
