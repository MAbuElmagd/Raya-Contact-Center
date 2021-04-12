# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError,UserError


class DateAdd(models.TransientModel):
    _name = "wizard.date.add"

    date = fields.Date()
    readonly_date = fields.Date()
    release_note = fields.Text()
    acceptance_add = fields.Boolean()
    release_add = fields.Boolean()
    release_confirm = fields.Boolean()

    def accept_and_put_date(self):
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        applicant = self.env['hr.applicant'].browse(active_ids)
        applicant.acceptance_date = self.date
        applicant.acceptance_is_done = True
        applicant.transfer_form_is_sent = False
    def set_release_date(self):
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        applicant = self.env['hr.applicant'].browse(active_ids)
        applicant.release_date = self.date
        applicant.release_note = self.release_note
        applicant.release_is_setted = True
        applicant.acceptance_is_done = False
    def confirm_release_date(self):
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        applicant = self.env['hr.applicant'].browse(active_ids)
        applicant.released_date = self.date
        applicant.released_confirmed = True





class HrEmployee(models.Model):
    _inherit = "hr.employee"

    raya_team = fields.Boolean()
    hr_id = fields.Char("HR ID", required=True)
    job_category_n_c = fields.Selection([('talent','Talent'),('operational','Operational')])

    @api.constrains('hr_id')
    def _constrains_hr_id(self):
        if self.hr_id:
            if len(self.search([('hr_id','=',self.hr_id),('id', '!=', self.id)])) > 0:
                raise ValidationError(_('HR ID Shoud Be Unique!'))

class HrRecruitmentStage(models.Model):
    _inherit = "hr.recruitment.stage"

    # refuse_email_template = fields.Many2one('mail.template')
    job_category = fields.Selection([('talent','Talent'),('operational','Operational')], required=True)
    ta_employee_transfer = fields.Boolean()
    @api.constrains('ta_employee_transfer')
    def _constrains_ta_employee_transfer(self):
        for rec in self:
            mail = self.search([('ta_employee_transfer', '=', True),
                                   ('id', '!=', rec.id)])
            if mail and rec.ta_employee_transfer:
                raise UserError(
                    _('TA Employee Transfer Already Marked in %s.' % mail.name)
                )


# class ApplicantGetRefuseReason(models.TransientModel):
#     _inherit = "applicant.get.refuse.reason"
#
#     def action_refuse_reason_apply(self):
#         # if self.applicant_ids.stage_id.refuse_email_template:
#         self.applicant_ids.write({'refuse_reason_id': self.refuse_reason_id.id, 'active': False})
#         ir_model_data = self.env['ir.model.data']
#         try:
#             template_id = self.env['mail.template'].search([('refuse_email_template','=',True)],limit=1).id
#         except ValueError:
#             template_id = False
#         try:
#             compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
#         except ValueError:
#             compose_form_id = False
#         ctx = {
#             'default_use_template': bool(template_id),
#             'default_template_id': template_id,
#             'default_composition_mode': 'comment',
#             'force_email': True
#         }
#         return {
#             'type': 'ir.actions.act_window',
#             'view_type': 'form',
#             'view_mode': 'form',
#             'res_model': 'mail.compose.message',
#             'views': [(compose_form_id, 'form')],
#             'view_id': compose_form_id,
#             'target': 'new',
#             'context': ctx,
#         }
#         # else:
#             # return self.applicant_ids.write({'refuse_reason_id': self.refuse_reason_id.id, 'active': False})

class hrApplicant(models.Model):
    _inherit = "hr.applicant"

    # @api.constrains('hiring_request')
    # def constrain_source_type(self):
    #     lines=self.env['hiring.request'].search([('id','=',self.hiring_request)])
    #     if  self.emp_id:
    #         raise UserError(_('You can only apply for External Hinring request !'))

    created_employee = fields.Boolean()

    @api.onchange('emp_id')
    def get_contact(self):
        self.partner_id = self.emp_id.address_home_id.id or False
    @api.onchange('hiring_request')
    def get_project(self):
        if self.hiring_request:
            self.project = self.hiring_request.project.id or False

    def trans_emp_enhance(self):
        applications = self.env['hr.applicant'].search([('released_date','!=',False)])
        for app in applications:
            if app.released_date == fields.Date.today():
                if app.emp_id.job_id != app.job_id:
                    employee= self.env['hr.resume.line'].search([('employee_id','=',app.emp_id.id),('name','=',app.emp_id.job_id.name)])
                    employee.update({'date_end':app.released_date,})
                    app.emp_id.job_id = app.job_id.id
                    employee.create({
                        'employee_id': app.emp_id.id,
                        'name':app.emp_id.job_id.name,
                        'date_start':app.released_date,
                        'description':app.emp_id.company_id.name or '',
                    })

    @api.constrains('hiring_request')
    def check_employ_type(self):
        employee=self.env['hr.employee'].search([('identification_id','=',self.national_id)])
        if len(employee)>0 and (self.hiring_request.sourceing_type=='external'):
             raise UserError(
                    _('This applicant is not allowed to apply for this Hirring request')
                )
        elif len(employee)==0 and (self.hiring_request.sourceing_type=='internal'):
             raise UserError(
                    _('This applicant is not allowed to apply for this Hirring request')
                )


    def send_transfer_form_ta(self):
        if not self.emp_id or not self.emp_id.address_home_id:
            raise UserError(_('The employee shoud have a address'))
        self.transfer_form_is_sent = True
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = self.env['mail.template'].search([('ta_employee_transfer','=',True)],limit=1).id
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'default_partner_ids':[(6,0,[self.emp_id.address_home_id.id])],
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

    def employee_acceptance_btn(self):
        return {
            'name': _('Employee Acceptance'),
            'view_mode': 'form',
            'res_model': 'wizard.date.add',
            'type': 'ir.actions.act_window',
            'view_id' : self.env.ref('wc_ta_extention.wc_ta_extention_wizard_for_transfer').id,
            'context':"{'default_acceptance_add':True,'default_release_add':False,'default_release_confirm':False}",
            'target': 'new'
        }
    def contact_manager_btn(self):
        if not self.manager or not self.manager.address_home_id:
            raise UserError(_('The employee shoud have a manager and also an address'))
        self.manager_contacted = True
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = self.env['mail.template'].search([('ta_transfer_manager_contact','=',True)],limit=1).id
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'default_partner_ids':[(6,0,[self.manager.address_home_id.id])],
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
    def set_release_btn(self):
        return {
            'name': _('Set Release'),
            'view_mode': 'form',
            'res_model': 'wizard.date.add',
            'type': 'ir.actions.act_window',
            'view_id' : self.env.ref('wc_ta_extention.wc_ta_extention_wizard_for_transfer').id,
            'context':"{'default_acceptance_add':False,'default_release_add':True,'default_release_confirm':False}",
            'target': 'new'
        }
    def confirm_release_btn(self):
        return {
            'name': _('Confirm Release'),
            'view_mode': 'form',
            'res_model': 'wizard.date.add',
            'type': 'ir.actions.act_window',
            'view_id' : self.env.ref('wc_ta_extention.wc_ta_extention_wizard_for_transfer').id,
            'context':{'default_acceptance_add':False,'default_release_add':False,'default_release_confirm':True,'default_readonly_date':self.release_date},
            'target': 'new'
        }


    transfer_form_is_sent = fields.Boolean()
    acceptance_is_done = fields.Boolean('Accepted')
    acceptance_date = fields.Date()
    release_date = fields.Date()
    release_note = fields.Text()
    released_date = fields.Date()
    released_confirmed = fields.Boolean()
    manager_contacted = fields.Boolean()
    release_is_setted = fields.Boolean()
    ta_employee_transfer = fields.Boolean(compute="_compute_ta_transfer_state")
    def _compute_ta_transfer_state(self):
        for this in self:
            this.ta_employee_transfer = this.stage_id.ta_employee_transfer or False


    manager = fields.Many2one('hr.employee', compute="_compute_manager_get")
    def _compute_manager_get(self):
        for this in self:
            this.manager = this.emp_id.parent_id.id or False



    @api.model
    def create(self, values):
        res = super(hrApplicant, self).create(values)
        if not res.hiring_request:
            if res.job_id:
                if res.job_id.job_category:
                    res.job_category = res.job_id.job_category
                # if res.job_id.job_category == 'operational':
                #     res.hiring_request = res.job_id.hiring_request.id
                if res.job_id.job_category == 'talent':
                    if len(res.job_id.hiring_request_many.filtered(lambda x:x.state == 'approved')) == 1:
                        res.hiring_request = res.job_id.hiring_request_many.filtered(lambda x:x.state == 'approved')[0].id
                    else:
                        res.hiring_request = False
        return res
    @api.onchange('stage_id')
    def check_hr_when_change(self):
        # after_one_stage = self.env['hr.recruitment.stage'].search(['|', ('job_category', '=', False), ('job_category', '=', self.job_category)], order='sequence asc')[1]
        initial_stage = self.env['hr.recruitment.stage'].search([('job_category','=',self.job_category),('is_initial','=',True)])
        if self.stage_id != initial_stage and not self.hiring_request and self.job_id.job_category == 'talent':
            raise ValidationError(_('You must enter the hiring request!'))


class hrJobEXT(models.Model):
    _inherit = "hr.employee"

    project = fields.Many2one('rcc.project', 'Project')

class hrJobEXT(models.Model):
    _inherit = "hr.job"

    # interview_checklist = fields.Many2one

    has_active_hiring_request = fields.Boolean(compute="get_has_active_hr")
    def get_has_active_hr(self):
        for this in self:
            this.has_active_hiring_request = False
            if this.job_category == 'operational':
                if this.hiring_request and this.hiring_request.state == 'approved':
                    this.has_active_hiring_request = True
                else:
                    this.has_active_hiring_request = False
            elif this.job_category == 'talent':
                if len(this.hiring_request_many.filtered(lambda x:x.state == 'approved')) > 0:
                    this.has_active_hiring_request = True
                else:
                    this.has_active_hiring_request = False


    hiring_request_many = fields.Many2many(
        'hiring.request', 'request_job_id_rel','id','job_id', 'Hiring Request',compute="_compute_many_hiring_request")
    def _compute_many_hiring_request(self):
        for this in self:
            hiring_requests = self.env['hiring.request'].search([('job','=',this.id)]).ids
            this.hiring_request_many = [(6,0,hiring_requests)]
            sum_heads = 0.0
            for hirs in this.hiring_request_many.filtered(lambda x:x.state == 'approved'):
                sum_heads += hirs.total_heads
            this.no_of_recruitment = sum_heads


class hiringRequest(models.Model):
    _inherit = 'hiring.request'

    @api.onchange('job')
    def check_department_first(self):
        if self.job and not self.center:
            if self.category == 'Talent Acq':
                raise UserError(_('Please Choose Department First'))
            else:
                raise UserError(_('Please Choose Center First'))
    # @api.onchange('center')
    # def check_project_first(self):
    #     if self.center and not self.project:
    #         raise UserError(_('Please Choose Project First'))

    sourceing_type = fields.Selection([('internal','Internal'),('external','External'),('both','Both')], string="Type")

    @api.onchange('sourceing_type')
    def chng_sourceing_type(self):
        if self.sourceing_type == 'external':
            self.share_option = False
            self.employee_id = False
            self.company_id = False
            self.dept_id = False
            self.employee_tag = False
            self.proj_id = False

    share_option = fields.Selection([('employee','Employee'),('company','Company'),('department','Department'),('employee_tag','Employee Tag'),('project','Project')])
    employee_id = fields.Many2many('hr.employee',string='Employees')
    company_id = fields.Many2one('res.company',string='Company')
    dept_id = fields.Many2many('hr.department',string='Departments')
    employee_tag = fields.Many2many('hr.employee.category',string='Tags')
    proj_id = fields.Many2many('rcc.project',string='Projects')

    targeted_partners = fields.Many2many('res.partner', compute="_compute_targeted_partners")

    @api.onchange('employee_id','company_id','employee_tag','dept_id','proj_id','share_option')
    def _compute_targeted_partners(self):
        for this in self:
            this.targeted_partners = False
            if this.sourceing_type == 'internal':
                if this.share_option == 'employee':
                    partners_ids = []
                    for emp in this.employee_id:
                        if emp.address_home_id.id:
                            partners_ids.append(emp.address_home_id.id)
                        else:
                            raise UserError(_('Employee address is not set, you need to add an address to this Employee'))
                    if len(partners_ids) <=0:
                        pass
                    else:
                        this.targeted_partners = [(6,0,[])]
                        this.targeted_partners = [(6,0,partners_ids)]
                elif this.share_option == 'company':
                    this.targeted_partners = [(6,0,this.company_id.partner_id.ids)]
                elif this.share_option == 'department':
                    emps = self.env['hr.employee'].search([('department_id','in',this.dept_id.ids)])
                    partners_ids = []
                    for emp in emps:
                        if emp.address_home_id.id:
                            partners_ids.append(emp.address_home_id.id)
                        else:
                            raise UserError(_('Employee address is not set, you need to add an address to this Employee'))
                    if len(partners_ids) <=0:
                        pass
                    else:
                        this.targeted_partners = [(6,0,[])]
                        this.targeted_partners = [(6,0,partners_ids)]
                elif this.share_option == 'employee_tag':
                    emps = self.env['hr.employee'].search([('category_ids','=',this.employee_tag.ids)])
                    partners_ids = []
                    for emp in emps:
                        if emp.address_home_id.id:
                            partners_ids.append(emp.address_home_id.id)
                        else:
                            raise UserError(_('Employee address is not set, you need to add an address to this Employee'))
                    if len(partners_ids) <=0:
                        pass
                    else:
                        this.targeted_partners = [(6,0,[])]
                        this.targeted_partners = [(6,0,partners_ids)]
                elif this.share_option == 'project':
                    emps = self.env['hr.employee'].search([('project','=',this.proj_id.ids)])
                    partners_ids = []
                    for emp in emps:
                        if emp.address_home_id.id:
                            partners_ids.append(emp.address_home_id.id)
                        else:
                            raise UserError(_('Employee address is not set, you need to add an address to this Employee'))
                    if len(partners_ids) <=0:
                        pass
                    else:
                        this.targeted_partners = [(6,0,[])]
                        this.targeted_partners = [(6,0,partners_ids)]
            else:
                this.targeted_partners = False
    def send_hiring_request_email(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('wc_ta_extention', 'email_template_hiring_request')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'force_email': True,
            'default_partner_ids':[(6,0,self.targeted_partners.ids)]
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


class MailTemplate(models.Model):
    """docstring for MailTemplate."""
    _inherit = 'mail.template'

    internal_sourcing_template = fields.Boolean()
    ta_employee_transfer = fields.Boolean()
    ta_transfer_manager_contact = fields.Boolean()
    refuse_email_template = fields.Boolean()


    @api.constrains('internal_sourcing_template')
    def _constrains_internal_sourcing_template(self):
        for rec in self:
            mail = self.search([('internal_sourcing_template', '=', True),
                                   ('id', '!=', rec.id)])
            if mail and rec.internal_sourcing_template:
                raise UserError(
                    _('Internal Sourcing Template Already Marked in %s.' % mail.name)
                )
    @api.constrains('ta_employee_transfer')
    def _constrains_ta_employee_transfer(self):
        for rec in self:
            mail = self.search([('ta_employee_transfer', '=', True),
                                   ('id', '!=', rec.id)])
            if mail and rec.ta_employee_transfer:
                raise UserError(
                    _('TA Employee Transfer Already Marked in %s.' % mail.name)
                )
    @api.constrains('ta_transfer_manager_contact')
    def _constrains_ta_transfer_manager_contact(self):
        for rec in self:
            mail = self.search([('ta_transfer_manager_contact', '=', True),
                                   ('id', '!=', rec.id)])
            if mail and rec.ta_transfer_manager_contact:
                raise UserError(
                    _('TA Transfer Manager Contact Already Marked in %s.' % mail.name)
                )

    @api.constrains('refuse_email_template')
    def _constrains_refuse_email_template(self):
        for rec in self:
            mail = self.search([('refuse_email_template', '=', True),
                                   ('id', '!=', rec.id)])
            if mail and rec.refuse_email_template:
                raise UserError(
                    _('Refuse Email Template Already Marked in %s.' % mail.name)
                )

    # @api.model
    # def create(self, values):
    #     old_sourcing_template = self.env['mail.template'].search([('internal_sourcing_template','=',True)])
    #     if len(old_sourcing_template) >= 1 and values['internal_sourcing_template'] == True:
    #         raise ValidationError(_('You can have only one internal sourcing template'))
    #     res = super(MailTemplate, self).create(values)
    #     return res
    #
    # def write(self, values):
    #     old_sourcing_template = self.env['mail.template'].search([('internal_sourcing_template','=',True)])
    #     if len(old_sourcing_template) >= 1 and values['internal_sourcing_template'] == True:
    #         raise ValidationError(_('You can have only one internal sourcing template'))
    #     res = super(MailTemplate, self).write(values)
    #     return res
