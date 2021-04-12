# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Jupical Technologies(<http://www.jupical.com>).
#    Author: Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from datetime import timedelta
import base64
from odoo.http import request, route
import http.client as clientapi
from odoo.addons.portal.controllers.portal import CustomerPortal
import base64
import json
import pytz
from dateutil.relativedelta import relativedelta
from datetime import datetime
from psycopg2 import IntegrityError
from werkzeug.exceptions import BadRequest
import werkzeug.urls
import werkzeug.wrappers
from odoo import http, SUPERUSER_ID, _
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.translate import _
from odoo.exceptions import ValidationError, UserError
from odoo.addons.base.models.ir_qweb_fields import nl2br
from datetime import date

class WebsiteForm(http.Controller):

    @http.route([
        '/tinterview/sub/<string:second_feedback>/<int:second_feedback_reason>/<string:second_interview_description>/<int:applicant>/',
    ], type='http', auth="public", website=True)
    def technical_interview_submit(self, second_feedback=None, second_feedback_reason=None, second_interview_description=None, applicant=None, **kwargs):
        applicant = request.env['hr.applicant'].sudo().browse(int(applicant))
        feedback_reasons = request.env['interview.feedback'].sudo().browse(int(second_feedback_reason))
        applicant.sudo().write({'second_interview_feedback':str(second_feedback),'second_interview_feedback_reason':feedback_reasons.id,'second_interview_description':str(second_interview_description),'technical_done':True})
        return request.render("technical_interviewer_ext.thankyou", {
            'applicant': applicant,
        })
    @http.route([
        '/my/tinterview/detail/<int:applicant>',
    ], type='http', auth="public", website=True)
    def technical_interview_detail(self, applicant=None, **kwargs):
        env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))
        user = request.env.user
        feedback_reasons = env['interview.feedback'].sudo().search([])
        applicant = env['hr.applicant'].sudo().browse(int(applicant))
        return request.render("technical_interviewer_ext.detail", {
            'applicant': applicant,
            'user': user,
            'feedback_reasons': feedback_reasons
        })

    @http.route([
        '/my/tinterviews/',
    ], type='http', auth="public", website=True)
    def technical_interviewer(self, **kwargs):
        env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))
        user = request.env.user
        technical_stage = env['hr.recruitment.stage'].sudo().search([('job_category','=','operational'),('technical','=','true')])
        applicants = env['hr.applicant'].sudo().search([('technical_interviewer','=',user.id),('stage_id','=',technical_stage.id),('technical_done','=',False)])
        # Render page
        return request.render("technical_interviewer_ext.applicants", {
            'applicants': applicants,
        })

    @http.route('''/jobs/detail/<model("hr.job"):job>''', type='http', auth="public", website=True, sitemap=True)
    def jobs_detail(self, job, **kwargs):
        if not job.can_access_from_current_website():
            raise NotFound()
        request.session['utm_kwargs'] = kwargs
        return request.render("website_hr_recruitment.detail", {
            'job': job,
            'main_object': job,
        })


    @http.route(['''/jobs/apply/<model("hr.job"):job>'''], type='http', auth="public", website=True, sitemap=True)
    def jobs_apply(self, job, **kwargs):
        if not job.can_access_from_current_website():
            raise NotFound()
        if job.job_category == 'talent' and request.env.user.id == 4:
            return http.redirect_with_hash('/web/signup')
        error = {}
        default = {}
        if 'website_hr_recruitment_error' in request.session:
            error = request.session.pop('website_hr_recruitment_error')
            default = request.session.pop('website_hr_recruitment_default')

        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])
        areas = request.env['res.country.state'].sudo().search([])
        partner_id	= request.env.user.partner_id
        partner_name = ""
        partner_phone = ""
        national_id = ""
        email_from =""
        region =""
        country =""
        dob = ""
        gender = ""
        military_status = ""
        job_category = request.env['hr.job'].sudo().search([('id','=',int(job))]).job_category

        if partner_id:
            #job_category = job_category
            partner_name = partner_id.name
            partner_phone = partner_id.phone
            national_id = partner_id.national_id
            email_from = partner_id.email
            region = partner_id.state_id.id
            country = partner_id.country_id.id
            date_of_birth = partner_id.dob
            gender = partner_id.gender
            military_status = partner_id.military_status
        if job_category == 'operational':
            try:
                project = int(request.session.get('utm_kwargs').get('utm_project'))
            except Exception as e:
                project = False
            try:
                hiring_request = int(request.session.get('utm_kwargs').get('utm_hiring_request'))
            except Exception as e:
                hiring_request = False
            try:
                recruiter = int(request.session.get('utm_kwargs').get('recruiter'))
            except Exception as e:
                recruiter = request.env['res.users'].sudo().browse(1).id
            return request.render("website_hr_recruitment.apply", {
                'job': job,
                'partner_id':partner_id,
                'partner_name':partner_name,
                'partner_phone':partner_phone,
                'national_id':national_id,
                'email_from':email_from,
                'job_category':job_category,
                'state':region,
                'countries':countries,
                'states':states,
                'nationality': country,
                'date_of_birth':str(date_of_birth),
                'gender':gender,
                'military_status':military_status,
                'project':project,
                'hiring_request':hiring_request,
                'recruiter':recruiter,
                'error': error,
                'default': default,
            })
        else:
            return request.render("website_hr_recruitment.apply", {
                'job': job,
                'partner_id':partner_id,
                'partner_name':partner_name,
                'partner_phone':partner_phone,
                'national_id':national_id,
                'email_from':email_from,
                'job_category':job_category,
                'state':region,
                'countries':countries,
                'states':states,
                'nationality': country,
                'date_of_birth':str(date_of_birth),
                'gender':gender,
                'military_status':military_status,
                'error': error,
                'default': default,
            })

    @http.route(['/survey/open/site/<int:applicant_id>'], type='http', auth="public", methods=['GET'], website=True, sitemap=True)
    def test_redirect(self, applicant_id,**kwargs):
        app_obj = request.env['hr.applicant'].sudo().search([('id','=',int(applicant_id))])
        app_obj.update_lines()
        app_obj.excel_lines()
        app_obj.get_national_id_emp()
        app_obj.pick_applicant_quartile_type()
        app_obj.check_quality_hold()
        app_obj.get_project()
        job_obj =  app_obj.job_id
        survey_id = app_obj.job_id.apply_survey_id
        partner_id = app_obj.partner_id
        #insert Skills
        #self.insert_skills(applicant_id,partner_id.id)

        if job_obj.job_category == 'talent':

            if not app_obj.response_apply_id:
                response = survey_id._create_answer(partner=partner_id)
                app_obj.response_apply_id = response.id
            else:
                response = app_obj.response_apply_id

            # grab the token of the response and start surveying
            url = '%s?%s' % (survey_id.get_start_url(), werkzeug.urls.url_encode({'answer_token': response and response.access_token or None}))
            app_obj.sudo().write({'response_apply_id':response.id})
            return http.redirect_with_hash(url)
        else:
            return http.redirect_with_hash('/job-thank-you')
        #return app_obj.survey_id.action_start_survey(answer=response)

   # def insert_skills(self,applicationID,partner_id):


        #PartnerOBJ = request.env['res.partner'].sudo().search([('id','=',int(partner_id))])
        #techSkills = PartnerOBJ.techskill_ids
        #for tech in techSkills:
       #    request.env['hr.skill.clone'].sudo().create({'skill_id':tech.skill_id.id,'tech_applicant_talent_level':tech.nontech_applicant_talent_level.id,'applicant_tech_talent_id	':applicationID})
       # nontechSkills = PartnerOBJ.nontechskill_ids
       # for tech in nontechSkills:
       #     request.env['hr.skill.clone'].sudo().create({'skill_id':tech.skill_id.id,'nontech_applicant_talent_level':tech.nontech_applicant_talent_level.id,'applicant_non_tech_talent_id':applicationID})


    @http.route('/website_form/', type='http', auth="public", methods=['POST'], multilang=False)
    def website_form_empty(self, **kwargs):
        # This is a workaround to don't add language prefix to <form action="/website_form/" ...>
        return ""
        #return werkzeug.utils.redirect( request.httprequest.referrer + "#servy" )

    # Check and insert values from the form on the model <model>
    @http.route('/website_form/<string:model_name>', type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def website_form(self, model_name, **kwargs):
        if model_name =='hr.applicant':
            job_id  = request.params.get('job_id')
            #partner = request.params.get('partner_id')
            survey_id = request.env['hr.job'].sudo().search([('id','=',int(job_id))]).survey_id
            #partner_id = request.env['res.partner'].search([('id','=',int(partner))])
           # print(partner_id)
            url = "/survey/start/"+ str(survey_id.access_token)
            #return http.redirect_with_hash(url)

        # Partial CSRF check, only performed when session is authenticated, as there
        # is no real risk for unauthenticated sessions here. It's a common case for
        # embedded forms now: SameSite policy rejects the cookies, so the session
        # is lost, and the CSRF check fails, breaking the post for no good reason.
        csrf_token = request.params.pop('csrf_token', None)
        if request.session.uid and not request.validate_csrf(csrf_token):
            raise BadRequest('Session expired (invalid CSRF token)')

        try:
            if request.env['ir.http']._verify_request_recaptcha_token('website_form'):
                return self._handle_website_form(model_name, **kwargs)
            error = _("Suspicious activity detected by Google reCaptcha.")
        except (ValidationError, UserError) as e:
            error = e.args[0]
        return json.dumps({
            'error': error,
        })

    def _handle_website_form(self, model_name, **kwargs):
        model_record = request.env['ir.model'].sudo().search([('model', '=', model_name), ('website_form_access', '=', True)])
        if not model_record:
            return json.dumps({
                'error': _("The form's specified model does not exist")
            })

        try:
            data = self.extract_data(model_record, request.params)
        # If we encounter an issue while extracting data
        except ValidationError as e:
            # I couldn't find a cleaner way to pass data to an exception
            return json.dumps({'error_fields' : e.args[0]})

        try:
            id_record = self.insert_record(request, model_record, data['record'], data['custom'], data.get('meta'))
            if id_record:
                self.insert_attachment(model_record, id_record, data['attachments'])
                # in case of an email, we want to send it immediately instead of waiting
                # for the email queue to process
                if model_name == 'mail.mail':
                    request.env[model_name].sudo().browse(id_record).send()

        # Some fields have additional SQL constraints that we can't check generically
        # Ex: crm.lead.probability which is a float between 0 and 1
        # TODO: How to get the name of the erroneous field ?
        except IntegrityError:
            return json.dumps(False)
        if model_name =='hr.applicant':
            job_id  = request.params.get('job_id')
            #partner = request.params.get('partner_id')
            survey_id = request.env['hr.job'].sudo().search([('id','=',int(job_id))]).survey_id
            #partner_id = request.env['res.partner'].search([('id','=',int(partner))])
           # print(partner_id)
            url = "/survey/start/"+ str(survey_id.access_token)

        request.session['form_builder_model_model'] = model_record.model
        request.session['form_builder_model'] = model_record.name
        request.session['form_builder_id'] = id_record
        # print("ID Record")
        # print(id_record)
        # print("ID Record")
        #return werkzeug.utils.redirect( request.httprequest.referrer + "#comments" )
        return json.dumps({'id': id_record,'data-success-page':url})


    # Constants string to make metadata readable on a text field

    _meta_label = "%s\n________\n\n" % _("Metadata")  # Title for meta data

    # Dict of dynamically called filters following type of field to be fault tolerent

    def identity(self, field_label, field_input):
        return field_input

    def integer(self, field_label, field_input):
        return int(field_input)

    def floating(self, field_label, field_input):
        return float(field_input)

    def boolean(self, field_label, field_input):
        return bool(field_input)

    def binary(self, field_label, field_input):
        return base64.b64encode(field_input.read())

    def one2many(self, field_label, field_input):
        return [int(i) for i in field_input.split(',')]

    def many2many(self, field_label, field_input, *args):
        return [(args[0] if args else (6,0)) + (self.one2many(field_label, field_input),)]

    _input_filters = {
        'char': identity,
        'text': identity,
        'html': identity,
        'date': identity,
        'datetime': identity,
        'many2one': integer,
        'one2many': one2many,
        'many2many':many2many,
        'selection': identity,
        'boolean': boolean,
        'integer': integer,
        'float': floating,
        'binary': binary,
        'monetary': floating,
    }


    # Extract all data sent by the form and sort its on several properties
    def extract_data(self, model, values):
        dest_model = request.env[model.sudo().model]

        data = {
            'record': {},        # Values to create record
            'attachments': [],  # Attached files
            'custom': '',        # Custom fields values
            'meta': '',         # Add metadata if enabled
        }

        authorized_fields = model.sudo()._get_form_writable_fields()
        # print("authorized_fields")
        # print(authorized_fields)
        # print("authorized_fields")
        authorized_fields['referred_by_hr_id'] = {
        "type": "char",
        "change_default": False,
        "company_dependent": False,
        "depends": (),
        "manual": False,
        "readonly": False,
        "required": False,
        "searchable": True,
        "sortable": True,
        "store": True,
        "string": "Referred By Hr Id",
        "translate": False,
        "trim": True,}

        authorized_fields['application_for'] = {
        "type": "selection",
        "change_default": False,
        "company_dependent": False,
        "depends": (),
        "manual": False,
        "readonly": False,
        "required": False,
        "searchable": True,
        "sortable": True,
        "store": True,
        "string": "Referred By Hr Id",
        "translate": False,
        "trim": True,}

        authorized_fields['project'] = {
        "type": "many2one",
        "change_default": False,
        "company_dependent": False,
        "depends": (),
        "manual": False,
        "readonly": False,
        "relation": "rcc.project",
        "required": False,
        "searchable": True,
        "sortable": True,
        "store": True,
        "string": "Project",
        "translate": False,
        "trim": True,}

        authorized_fields['hiring_request'] = {
        "type": "many2one",
        "change_default": False,
        "company_dependent": False,
        "depends": (),
        "manual": False,
        "readonly": False,
        "relation": "hiring.request",
        "required": False,
        "searchable": True,
        "sortable": True,
        "store": True,
        "string": "Hiring Request",
        "translate": False,
        "trim": True,}

        authorized_fields['recruiter'] = {
        "type": "many2one",
        "change_default": False,
        "company_dependent": False,
        "depends": (),
        "manual": False,
        "readonly": False,
        "relation": "res.users",
        "required": False,
        "searchable": True,
        "sortable": True,
        "store": True,
        "string": "Recruiter",
        "translate": False,
        "trim": True,}

        error_fields = []
        custom_fields = []

        for field_name, field_value in values.items():
            # If the value of the field if a file
            if hasattr(field_value, 'filename'):
                # Undo file upload field name indexing
                field_name = field_name.split('[', 1)[0]

                # If it's an actual binary field, convert the input file
                # If it's not, we'll use attachments instead
                if field_name in authorized_fields and authorized_fields[field_name]['type'] == 'binary':
                    data['record'][field_name] = base64.b64encode(field_value.read())
                    field_value.stream.seek(0) # do not consume value forever
                    if authorized_fields[field_name]['manual'] and field_name + "_filename" in dest_model:
                        data['record'][field_name + "_filename"] = field_value.filename
                else:
                    field_value.field_name = field_name
                    data['attachments'].append(field_value)

            # If it's a known field
            elif field_name in authorized_fields:
                try:
                    input_filter = self._input_filters[authorized_fields[field_name]['type']]
                    data['record'][field_name] = input_filter(self, field_name, field_value)
                except ValueError:
                    error_fields.append(field_name)

            # If it's a custom field
            elif field_name != 'context':
                custom_fields.append((field_name, field_value))

        data['custom'] = "\n".join([u"%s : %s" % v for v in custom_fields])

        # Add metadata if enabled  # ICP for retrocompatibility
        if request.env['ir.config_parameter'].sudo().get_param('website_form_enable_metadata'):
            environ = request.httprequest.headers.environ
            data['meta'] += "%s : %s\n%s : %s\n%s : %s\n%s : %s\n" % (
                "IP"                , environ.get("REMOTE_ADDR"),
                "USER_AGENT"        , environ.get("HTTP_USER_AGENT"),
                "ACCEPT_LANGUAGE"   , environ.get("HTTP_ACCEPT_LANGUAGE"),
                "REFERER"           , environ.get("HTTP_REFERER")
            )

        # This function can be defined on any model to provide
        # a model-specific filtering of the record values
        # Example:
        # def website_form_input_filter(self, values):
        #     values['name'] = '%s\'s Application' % values['partner_name']
        #     return values
        if hasattr(dest_model, "website_form_input_filter"):
            data['record'] = dest_model.website_form_input_filter(request, data['record'])

        missing_required_fields = [label for label, field in authorized_fields.items() if field['required'] and not label in data['record']]
        if any(error_fields):
            raise ValidationError(error_fields + missing_required_fields)

        return data

    def insert_record(self, request, model, values, custom, meta=None):
        # print("model")
        # print(model)
        # print("Request")
        # print(request)
        # print("values")
        # print(values)
        national_id = values['national_id']
        is_egyption = "true"
        date_from = "2020-12-01"
        date_to = "2021-03-18"
        model_name = model.sudo().model
        if model_name == 'mail.mail':
            values.update({'reply_to': values.get('email_from')})
        if model_name == 'hr.applicant':
            if values['partner_phone'].isnumeric() == False:
                raise ValidationError(_("Mobile Number Must Contain numbers only."))
                return

            job_obj = request.env['hr.job'].sudo().search([('id','=',values['job_id'])])
            if job_obj.job_category == 'operational':
                there_is_application_for = False
                try:
                    app_for = values['application_for']
                    there_is_application_for = True
                except Exception as e:
                    there_is_application_for = False
                if not there_is_application_for:
                    raise ValidationError(_("Please select the application (Apply for myself) Or (Refer a Friend)."))
                    return
                if there_is_application_for:
                    if values['application_for'] == 'refer':
                        if values['referred_by_hr_id']:
                            emp = request.env['hr.employee'].sudo().search([('hr_id','=',values['referred_by_hr_id'])])
                            if emp:
                                values['referred_by_employee'] = emp.id
                                values['referred_by_employee_grade'] = emp.employee_grade.id
                            if not emp:
                                raise ValidationError(_("HR ID should be linked to an employee."))
                                return
            
            emp = request.env['hr.employee'].sudo().search([('identification_id','=',values['national_id'])])
            if emp:
                national_id = values['national_id']
                is_egyption = "true"
                date_from = "2020-12-01"
                date_to = "2021-03-18"
                
                conn = clientapi.HTTPSConnection("recruitment-api.rayacx.com")
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
                            
            if emp.employee_grade:
                job_obj = request.env['hr.job'].sudo().search([('id','=',values['job_id'])])
                grade_obj =  request.env['employee.grade'].sudo().search([('id','=',emp.employee_grade.id)])
                max_emp_grade = int(grade_obj.garde) + int(grade_obj.grade_level_exception)
                max_job_grade = int(job_obj.employee_grade.garde) # int(job_obj.employee_grade.grade_level_exception)

                if max_emp_grade < max_job_grade:
                    raise ValidationError(_("Your Grade doesn't meet the Requirements"))
                    return

            if emp:
                conn = clientapi.HTTPSConnection("recruitment-api.rayacx.com")
                payload = ''
                headers = {'Authorization': 'Bearer W9OUSNrAOWDlZlYWoKOHSB9OTGdszSKobtdwoaqduEaOuct9ykv4EiIfpe0hsFVYge-4Y_INQ4tfKj0sCsO4uOaBsbOkud9FLNpzhlnI_nFCXL7ILHdVh8no3IRkLaRI1cgP1z4HK2qoCytXMo66o04NYpvlb-PtdtCzt32oETjRugNZEQwuMk2-kf3h3FsFj9vKvXsuGwGG5LH5ay9S5A'}
                conn.request("GET", "/api/cz/GetEmpMisconduct?IsEgyptian="+is_egyption+"&RefId="+national_id, payload, headers)
                ress = conn.getresponse()
                dataa = ress.read()
                dict_data = json.loads(dataa.decode('utf-8'))
                GetEmpMisconduct = 0
                if dict_data:
                    for i in dict_data:
                        # print(dict_data)
                        if i !="message":
                            last_emp_miconduct_count = str(i["date"])
                            emp_misconduct_date = str(i["date"]).split('T')[0]
                            if i["type"] == "Warning":
                                if last_emp_miconduct_count:
                                    #misconduct_period = last_emp_miconduct_count.misconduct_type_id.applying_restriction
                                    miconduct_employee_date = datetime.strptime(emp_misconduct_date,'%Y-%m-%d')
                                    emp_misconduct_date = miconduct_employee_date + timedelta(days=+90)
                                    if emp_misconduct_date > datetime.now():
                                        raise ValidationError(_("You have Misconducts that contradicts with the Requirements"))
                                        return False
                            if i["type"] == "Fine":
                                if last_emp_miconduct_count:
                                    #misconduct_period = last_emp_miconduct_count.misconduct_type_id.applying_restriction
                                    miconduct_employee_date = datetime.strptime(emp_misconduct_date,'%Y-%m-%d')
                                    emp_misconduct_date = miconduct_employee_date + timedelta(days=+30)
                                    if emp_misconduct_date > datetime.now():
                                        raise ValidationError(_("You have Misconducts that contradicts with the Requirements"))
                                        return False
                            if i["type"] == "Pay attention":

                                if last_emp_miconduct_count:
                                    #misconduct_period = last_emp_miconduct_count.misconduct_type_id.applying_restriction
                                    miconduct_employee_date = datetime.strptime(emp_misconduct_date,'%Y-%m-%d')
                                    emp_misconduct_date = miconduct_employee_date + timedelta(days=+30)
                                    if emp_misconduct_date > datetime.now():
                                        raise ValidationError(_("You have Misconducts that contradicts with the Requirements"))
                                        return False
        # Misconduct Online Restriction
            if emp:
                #KPI
                conn = clientapi.HTTPSConnection("recruitment-api.rayacx.com")
                payload = ''
                headers = {'Authorization': 'Bearer W9OUSNrAOWDlZlYWoKOHSB9OTGdszSKobtdwoaqduEaOuct9ykv4EiIfpe0hsFVYge-4Y_INQ4tfKj0sCsO4uOaBsbOkud9FLNpzhlnI_nFCXL7ILHdVh8no3IRkLaRI1cgP1z4HK2qoCytXMo66o04NYpvlb-PtdtCzt32oETjRugNZEQwuMk2-kf3h3FsFj9vKvXsuGwGG5LH5ay9S5A'}
                conn.request("GET", "/api/cz/GetEmpHeadcount?IsEgyptian="+is_egyption+"&RefId="+national_id, payload, headers)
                ress = conn.getresponse()
                data = ress.read()
                dict_data = json.loads(data.decode('utf-8'))
                GetEmpHeadcount = 0
                # print("HEAD Count ")
                # print("HEAD Count ")
                # print("HEAD Count ")
                # print("HEAD Count ")

                # print(dict_data)

                # print("Head Count")
                # print("HEAD Count ")
                # print("HEAD Count ")
                # print("HEAD Count ")
                # print("HEAD Count ")
                if dict_data:
                    #for i in dict_data:
                    job_head_count = request.env['hr.job'].sudo().search([('id','=',values['job_id'])]).head_count_restriction
                    # print("i")

                    # print("i")
                    last_emp_head_count = dict_data["headcount_Date"]
                    emp_head_count_date = dict_data["headcount_Date"].split('T')[0]

                    if last_emp_head_count:
                        emp_head_count_date = datetime.strptime(emp_head_count_date,'%Y-%m-%d')
                        # print(emp_head_count_date)
                        # print(emp_head_count_date)
                        # print(emp_head_count_date)
                        emp_head_count_date =  emp_head_count_date+ timedelta(days=(int(job_head_count)*30))
                        # print(emp_head_count_date)
                        if emp_head_count_date > datetime.now():
                            raise ValidationError(_("Your Last Head Count doesn't meet the Requirements"))
                            return False
                else:
                    job_head_count = request.env['hr.job'].search([('id','=',values['job_id'])]).head_count_restriction
                    last_emp_head_count = request.env['head.count.line'].search([('emp_id','=',emp.id)],order='id desc',limit=1)
                    if last_emp_head_count:
                        emp_head_count_date = last_emp_head_count.date + relativedelta(months=+int(job_head_count))
                        if emp_head_count_date > date.today():
                            raise ValidationError(_("Your Last Head Count doesn't meet the Requirements"))
                            return False
        record = request.env[model_name].sudo().create(values)
        if record.recruiter:
            record.user_id = record.recruiter.id

        # print("RECORD")
        # print(record)
        # print("RECORD")
        if custom or meta:
            _custom_label = "%s\n___________\n\n" % _("Other Information:")  # Title for custom fields
            if model_name == 'mail.mail':
                _custom_label = "%s\n___________\n\n" % _("This message has been posted on your website!")
            default_field = model.website_form_default_field_id
            default_field_data = values.get(default_field.name, '')
            custom_content = (default_field_data + "\n\n" if default_field_data else '') \
                           + (_custom_label + custom + "\n\n" if custom else '') \
                           + (self._meta_label + meta if meta else '')

            # If there is a default field configured for this model, use it.
            # If there isn't, put the custom data in a message instead

            if default_field.name:
                if default_field.ttype == 'html' or model_name == 'mail.mail':
                    custom_content = nl2br(custom_content)
                # print(record)
                record.update({default_field.name: custom_content})
            else:
                values = {
                    'body': nl2br(custom_content),
                    'model': model_name,
                    'message_type': 'comment',
                    'no_auto_thread': False,
                    'res_id': record.id,
                }
                mail_id = request.env['mail.message'].with_user(SUPERUSER_ID).create(values)

        return record.id


    def insert_attachment(self, model, id_record, files):
        orphan_attachment_ids = []
        model_name = model.sudo().model
        record = model.env[model_name].browse(id_record)
        authorized_fields = model.sudo()._get_form_writable_fields()
        for file in files:
            custom_field = file.field_name not in authorized_fields
            attachment_value = {
                'name': file.filename,
                'datas': base64.encodebytes(file.read()),
                'res_model': model_name,
                'res_id': record.id,
            }
            attachment_id = request.env['ir.attachment'].sudo().create(attachment_value)
            if attachment_id and not custom_field:
                record.sudo()[file.field_name] = [(4, attachment_id.id)]
            else:
                orphan_attachment_ids.append(attachment_id.id)

        if model_name != 'mail.mail':
            # If some attachments didn't match a field on the model,
            # we create a mail.message to link them to the record
            if orphan_attachment_ids:
                values = {
                    'body': _('<p>Attached files : </p>'),
                    'model': model_name,
                    'message_type': 'comment',
                    'no_auto_thread': False,
                    'res_id': id_record,
                    'attachment_ids': [(6, 0, orphan_attachment_ids)],
                }
                mail_id = request.env['mail.message'].with_user(SUPERUSER_ID).create(values)
        else:
            # If the model is mail.mail then we have no other choice but to
            # attach the custom binary field files on the attachment_ids field.
            for attachment_id_id in orphan_attachment_ids:
                record.attachment_ids = [(4, attachment_id_id)]

class CustomerProfile(CustomerPortal):

    CustomerPortal.MANDATORY_BILLING_FIELDS.append("image_1920")
    CustomerPortal.MANDATORY_BILLING_FIELDS.append("mobile")
    CustomerPortal.MANDATORY_BILLING_FIELDS.append("dob")
    CustomerPortal.MANDATORY_BILLING_FIELDS.append("gender")
    CustomerPortal.MANDATORY_BILLING_FIELDS.append("military_status")

    def _prepare_portal_layout_values(self):
        """Values for /my/* templates rendering.

        Does not include the record counts.
        """
        # get customer sales rep
        sales_user = False
        partner = request.env.user.partner_id
        if partner.user_id and not partner.user_id._is_public():
            sales_user = partner.user_id
        is_emp = request.env['hr.employee'].sudo().search([('identification_id','=',request.env.user.partner_id.national_id)]).id
        print("IS EMP")
        print(is_emp)
        print("IS EMP")
        return {
            'sales_user': sales_user,
            'page_name': 'home',
            'is_emp': is_emp,
        }

    @route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):

        values = self._prepare_portal_layout_values()
        # print("############ I Am Here ##############")
        # print(values)

        # print("############ I Am Here ##############")

        partner = request.env.user.partner_id

        values.update({
            'error': {},
            'error_message': [],
        })

        if post and request.httprequest.method == 'POST':
            error, error_message = self.details_form_validate(post)
            values.update({'error': error, 'error_message': error_message})
            values.update(post)

            if not error:
                values = {key: post[key] for key in self.MANDATORY_BILLING_FIELDS}
                values.update({key: post[key]
                               for key in self.OPTIONAL_BILLING_FIELDS if key in post})
                values.update({'country_id': int(values.pop('country_id', 0))})
                values.update({'zip': values.pop('zipcode', '')})
                if values.get('state_id') == '':
                    values.update({'state_id': False})
                values['image_1920'] = False
                files_to_send = request.httprequest.files.getlist('image_1920')
                for file in files_to_send:
                    values['image_1920'] = base64.b64encode(file.read())
                # print("DOOOOOOOOOOOBBBBBBBBBBBBBBB")
                # print(values.get('dob'))
                date_of_birth = datetime.strptime(values.get('dob'), '%m/%d/%y %H:%M:%S')
                # print(date_of_birth)
                # print(date_of_birth.date())
                # print("DOOOOOOOOOOOBBBBBBBBBBBBBBB")
                values['dob'] = date_of_birth.date()

                partner.sudo().write(values)
                if values.get('image_1920'):
                    request.env.user.sudo().write({'image_1920': values.get('image_1920')})
                if redirect:
                    return request.redirect(redirect)
                return request.redirect('/my/home')

        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])

        values.update({
            'partner': partner,
            'countries': countries,
            'states': states,
            'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
            'redirect': redirect,
            'page_name': 'my_details',
        })

        response = request.render("portal.portal_my_details", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response
