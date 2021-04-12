

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


class hrApplicant(models.Model):
    _inherit = "hr.applicant"


    finished_hiring_request_state = fields.Boolean(compute="_compute_finished_hiring_request_state")
    def _compute_finished_hiring_request_state(self):
        for this in self:
            this.finished_hiring_request_state = this.hiring_request.finished_hiring_request_state

    @api.onchange('stage_id')
    def check_can_move(self):
        if self.finished_hiring_request_state:
            initial_stage = self.env['hr.recruitment.stage'].search([('job_category','=',self.job_category),('is_initial','=',True)])
            if self.stage_id != initial_stage:
                raise ValidationError(_('You cannot move more applications through stages, You can only return to the inial stage or archive the application The Hiring Request required employees are Hired'))
        if self.job_category == 'talent':
            hiring_stage = initial_stage = self.env['hr.recruitment.stage'].search([('job_category','=','talent'),('is_final','=',True)])
            if self.stage_id == hiring_stage:
                for value in self.nontechskill_talent_ids:
                    if not value.nontech_applicant_talent_level:
                        raise ValidationError(_("You have to Fill all The Applicant's Skill Levels"))
                for value in self.techskill_talent_ids:
                    if not value.tech_applicant_talent_level:
                        raise ValidationError(_("You have to Fill all The Applicant's Skill Levels"))
                for value in self.language_level_talent_ids:
                    if not value.lang_applicant_talent_level:
                        raise ValidationError(_("You have to Fill all The Applicant's Skill Levels"))

    applicant_file_id =fields.Many2many(comodel_name="ir.attachment",
                                relation="m2m_ir_applicant_id_rel",
                                column1="m2m_id",
                                column2="applicant_file_id", string="Applicant ID")

    @api.constrains('applicant_file_id')
    def constrain_assessment_test(self):
        if len(self.applicant_file_id) > 1 :
                raise UserError(_('You can only upload one Applicant ID !'))

    @api.onchange('hr_id')
    def create_employee_from_applicant(self):
        """ Create an hr.employee from the hr.applicants """
        if self.hr_id and self.final and self.created_employee == False:
            employee = False
            for applicant in self:
                contact_name = False
                if applicant.partner_id:
                    address_id = applicant.partner_id.address_get(['contact'])['contact']
                    contact_name = applicant.partner_id.display_name
                else:
                    if not applicant.partner_name:
                        raise UserError(_('You must define a Contact Name for this applicant.'))
                    new_partner_id = self.env['res.partner'].create({
                        'is_company': False,
                        'type': 'private',
                        'name': applicant.partner_name,
                        'email': applicant.email_from,
                        'phone': applicant.partner_phone,
                        'mobile': applicant.partner_mobile
                    })
                    applicant.partner_id = new_partner_id
                    address_id = new_partner_id.address_get(['contact'])['contact']
                if applicant.partner_name or contact_name:

                    skills = []
                    flag = True

                    for value in applicant.nontechskill_talent_ids:
                        if not value.nontech_applicant_talent_level:
                            raise ValidationError(_('Fill all Applicant Level'))

                        skills.append((0,0,{
                                        'skill_type_id':value.skill_id.skill_type_id.id,
                                        'skill_id': value.skill_id.id,
                                        'level_progress': value.nontech_applicant_talent_level.level_progress,
                                        'skill_level_id':value.nontech_applicant_talent_level.id
                                    }))
                        if value.skill_id.id == applicant.skill_id.id:
                            flag = False
                    for value in applicant.techskill_talent_ids:
                        if not value.tech_applicant_talent_level:
                            raise ValidationError(_('Fill all Applicant Level'))

                        skills.append((0,0,{
                                        'skill_type_id':value.skill_id.skill_type_id.id,
                                        'skill_id': value.skill_id.id,
                                        'level_progress': value.tech_applicant_talent_level.level_progress,
                                        'skill_level_id':value.tech_applicant_talent_level.id
                                    }))
                        if value.skill_id.id == applicant.skill_id.id:
                            flag = False
                    for value in applicant.language_level_talent_ids:
                        if not value.lang_applicant_talent_level:
                            raise ValidationError(_('Fill all Applicant Level'))

                        skills.append((0,0,{
                                        'skill_type_id':value.skill_id.skill_type_id.id,
                                        'skill_id': value.skill_id.id,
                                        'level_progress': value.lang_applicant_talent_level.level_progress,
                                        'skill_level_id':value.lang_applicant_talent_level.id
                                    }))
                        if value.skill_id.id == applicant.skill_id.id:
                            flag = False


                    if applicant.excel_check:
                        if applicant.excel_line_ids:

                            if flag:
                                total=0
                                for value in applicant.excel_line_ids:
                                    total+=value.new_mark
                                skills.append((0,0,{
                                                    'skill_type_id':applicant.skill_id.skill_type_id.id,
                                                    'skill_id': applicant.skill_id.id,
                                                    'current_degree': total,
                                                    'skill_level_id':applicant.skill_level_id.id
                                                }))

                    employee_data = {
                        'default_name': applicant.partner_name or contact_name,
                        'default_job_id': applicant.job_id.id,
                        'default_job_title': applicant.job_id.name,
                        'address_home_id': address_id,
                        'default_department_id': applicant.department_id.id or False,
                        'default_address_id': applicant.company_id and applicant.company_id.partner_id
                                and applicant.company_id.partner_id.id or False,
                        'default_hr_id':applicant.hr_id,
                        'default_work_email': '',
                        'default_work_phone': '',
                        'form_view_initial_mode': 'edit',
                        'default_applicant_id': applicant.ids,
                        'default_identification_id':applicant.national_id,
                        'default_project':applicant.project.id,
                        'default_country_id':applicant.nationality.id,
                        'default_gender':applicant.gender,
                        'default_birthday':applicant.date_of_birth,
                        'default_military_status':applicant.military_status,
                        'default_employee_skill_ids': skills,

                        'default_education_ids':applicant.education_ids.ids,
                        'default_certification_ids':applicant.certification_ids.ids,
                        'default_profession_ids':applicant.profession_ids.ids,

                        }

            dict_act_window = self.env['ir.actions.act_window']._for_xml_id('hr.open_view_employee_list')
            dict_act_window['context'] = employee_data
            applicant.created_employee = True
            return dict_act_window

    national_id = fields.Char(string="National id", required=True ,size=14)
    @api.constrains('national_id')
    def _constrains_national_id(self):
        if self.national_id:
            id_length = len(self.national_id.replace(" ", ""))
            if id_length != 14 or not self.national_id.isnumeric():
                raise ValidationError(_('National ID Shoud Be 14, Numeric Only & Unique!'))
    hiring_request = fields.Many2one('hiring.request',string="Hiring Request")
    interest_reason_id = fields.Many2one('hr.applicant.lost.interest.reason',string="Lost Interest Reason" )
    not_matching_criteria_reason_id = fields.Many2one('hr.applicant.not.match.reason',string="Not Matching Reason" )
    no_show_reason_id = fields.Many2one('hr.applicant.no.show.reason',string="No Show Reason" )
    accept_pipeline = fields.Char(string='Accept Pipeline')
    area = fields.Many2one('city.area',string="Area")
    def no_show(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('No Show Reason'),
            'res_model': 'applicant.not.matching.reason',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_applicant_ids': self.ids, 'active_test': False},
            'views': [[False, 'form']]
        }

    def not_matching_application(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Not Matching Criteria '),
            'res_model': 'applicant.not.matching.reason',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_applicant_ids': self.ids, 'active_test': False},
            'views': [[False, 'form']]
        }

    def lost_interest_applicant(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Lost Interest Reason'),
            'res_model': 'applicant.lost.interest.reason',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_applicant_ids': self.ids, 'active_test': False},
            'views': [[False, 'form']]
        }

    def transfer_applicant(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Transfer Application'),
            'res_model': 'applicant.get.transfer.reason',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_applicant_ids': self.ids, 'active_test': False},
            'views': [[False, 'form']]
        }

    @api.model
    def create(self, vals):
        res = super(hrApplicant, self).create(vals)
        vals['hiring_request'] = self.env['hr.job'].search([('id','=',vals['job_id'])]).hiring_request.id
        return res


class City(models.Model):
    _name = "city.area"
    name = fields.Char()
    city=fields.Many2one('res.country.state',required=True,string='City')

class HRJOB(models.Model):
    _inherit = 'hr.job'



class HREMPLOYEE(models.Model):
    _inherit = "hr.employee"
    military_status = fields.Selection([('Completed','Completed'),
                                        ('Will serve','Will serve'),
                                        ('Exempted','Exempted'),
                                        ('Postponed','Postponed'),
                                        ('Female','Female')
                                        ],string="Military Status")
    @api.model
    def create(self, values):
        res = super(HREMPLOYEE, self).create(values)
        if res.applicant_id:
            if not res.applicant_id.partner_id:
                partner_id = self.env['res.partner'].create({
                'name':res.applicant_id.name.replace("'s Application",""),
                'email':res.applicant_id.email_from,
                'mobile':res.applicant_id.partner_mobile,
                'phone':res.applicant_id.partner_phone,
                'national_id':res.applicant_id.national_id,
                })
                res.write({'address_home_id':partner_id.id})
            else:
                res.applicant_id.partner_id.email = res.applicant_id.email_from
                res.applicant_id.partner_id.mobile = res.applicant_id.partner_mobile
                res.applicant_id.partner_id.phone = res.applicant_id.partner_phone
                res.applicant_id.partner_id.national_id = res.applicant_id.national_id
                res.write({'address_home_id':res.applicant_id.partner_id.id})
        return res



class HiringRequest(models.Model):
    _name = "hiring.request"
    _description = "Hiring Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]


    finished_hiring_request_state = fields.Boolean(compute="_compute_finished_hiring_request_state")
    def _compute_finished_hiring_request_state(self):
        for this in self:
            if this.category == 'Talent Acq':
                final_stage = self.env['hr.recruitment.stage'].search([('is_final','=',True),('job_category','=','talent')])
                applications = self.env['hr.applicant'].search([('hiring_request','=',this.id),('stage_id','=',final_stage.id)])
                if len(applications) >= this.total_heads:
                    this.finished_hiring_request_state = True
                else:
                    this.finished_hiring_request_state = False
            else:
                final_stage = self.env['hr.recruitment.stage'].search([('is_final','=',True),('job_category','=','operational')])
                applications = self.env['hr.applicant'].search([('hiring_request','=',this.id),('stage_id','=',final_stage.id)])
                if len(applications) >= this.total_heads:
                    this.finished_hiring_request_state = True
                else:
                    this.finished_hiring_request_state = False
    name = fields.Char(
        string="Request ID",
        )
    ref = fields.Char(
        string="Request Reference",
        )
    accrual_start_date =fields.Date("Actual start date")

    center = fields.Many2one('hr.department',string="Center",required=True)
    working_location = fields.Many2one('work.locations',string="Working Location",required=True)
    job = fields.Many2one('hr.job',string="Job Title",required=True)
    project = fields.Many2one('rcc.project')
    total_heads = fields.Integer(string="Total Request Heads",required=True)
    actual_hired = fields.Integer(string="Actual Hired", compute="_compute_actual_hired")
    actual_hired_n_c = fields.Integer(string="Actual Hired")
    def _compute_actual_hired(self):
        for this in self:
            if this.category == 'Talent Acq':
                hired_stage = self.env['hr.recruitment.stage'].search([('job_category','=','talent'),('is_final','=',True)])
                applicants = self.env['hr.applicant'].search([('stage_id','=',hired_stage.id),('hiring_request','=',this.id)])
                this.actual_hired = len(applicants)
                this.actual_hired_n_c = len(applicants)
            elif this.category == 'operational':
                hired_stage = self.env['hr.recruitment.stage'].search([('job_category','=','operational'),('is_o_final','=',True)])
                applicants = self.env['hr.applicant'].search([('stage_id','=',hired_stage.id),('hiring_request','=',this.id)])
                this.actual_hired = len(applicants)
                this.actual_hired_n_c = len(applicants)
            else:
                this.actual_hired = 0
                this.actual_hired_n_c = 0
    total_males = fields.Integer(string="Total Males",required=True)
    total_females = fields.Integer(string="Total Females",required=True)
    requested_due_dates = fields.Date(string="Requested Due Dates")
    batch_numbers = fields.Integer(string="Batch Numbers",required=True)
    comments = fields.Char(string="Comments")
    category = fields.Selection([('operational','Operational Recruitment'),('Talent Acq','Talent Acquisition')],string="Category")
    scope = fields.Many2one('rcc.scope',string="Scope")
    english_level =fields.Selection([('good','Good')])
    lang_levels = fields.Many2one('lang.levels', string="Language Level ")
    sector = fields.Many2one('sector.sector',string="Sector" )


    state = fields.Selection([
    ("draft", "Draft"),("approved", "Confirmed / Approved "),
    ("rejected", "Rejected"),("done", "Finished and Closed")],
        string="Status",
        index=True,
        track_visibility="onchange",
        required=True,
        default="draft"
    )

    def button_approved(self):
        self.write({'state':'approved'})
    def button_done(self):
        self.write({'state':'done'})
    def button_rejected(self):
        self.write({'state':'rejected'})

class SCOPE(models.Model):
    _name = 'rcc.scope'
    name = fields.Char(string="Scope Name ")
    category = fields.Selection([('operational','Operational Recruitment'),('Talent Acq','Talent Acq')],string="Category")

class Sector(models.Model):
    _name ="sector.sector"
    name = fields.Char(string="Sector")


class WorkLocations(models.Model):
    _name = "work.locations"
    _description = "Working Locations"
    name = fields.Char("Locations")

class RCCPROJECT(models.Model):
    _name = 'rcc.project'
    _description = "RCC Projects"

    name = fields.Char(string="Project Name")

class LanguagesLeve(models.Model):
    _name='lang.levels'
    name = fields.Char(string="Level Name")


class HRJOB(models.Model):
    _inherit = 'hr.job'

    hiring_request = fields.Many2one('hiring.request',string="Hiring Request")

    hrr_center = fields.Many2one('hr.department',string="Center")
    hrr_working_location = fields.Many2one('work.locations',string="Working Location")
    hrr_job = fields.Many2one('hr.job',string="Job Title")
    hrr_project = fields.Many2one('rcc.project')
    hrr_total_heads = fields.Integer(string="Total Heads")
    hrr_total_males = fields.Integer(string="Total Males")
    hrr_total_females = fields.Integer(string="Total Females")
    hrr_requested_due_dates = fields.Date(string="Requested Due Dates")
    hrr_batch_numbers = fields.Integer(string="Batch Numbers")
    hrr_comments = fields.Char(string="Comments")
    hrr_scope = fields.Many2one('rcc.scope',string="Scope")
    hrr_english_level = fields.Selection([('good','Good'),('excellent','Excellent')] , string="English Level ")


    @api.onchange('hiring_request')
    def change_hiring_request(self):
        if self.hiring_request:
            self.hrr_center = self.hiring_request.center
            self.hrr_working_location = self.hiring_request.working_location
            self.hrr_job = self.hiring_request.job
            self.hrr_project = self.hiring_request.project
            self.hrr_total_heads = self.hiring_request.total_heads
            self.hrr_total_males = self.hiring_request.total_males
            self.hrr_total_females = self.hiring_request.total_females
            self.hrr_requested_due_dates = self.hiring_request.requested_due_dates
            self.hrr_batch_numbers = self.hiring_request.batch_numbers
            self.hrr_comments = self.hiring_request.comments
            self.hrr_scope = self.hiring_request.scope
            self.hrr_english_level = self.hiring_request.english_level
            self.department_id = self.hiring_request.center
            self.no_of_recruitment = self.hiring_request.total_heads
