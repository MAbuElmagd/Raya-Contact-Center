# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError

class MailTemplate(models.Model):
    _inherit = "mail.template"

    criteria_hold_notification = fields.Boolean()
    @api.constrains('criteria_hold_notification')
    def _constrains_criteria_hold_notification(self):
        for rec in self:
            mail = self.search([('criteria_hold_notification', '=', True),
                                   ('id', '!=', rec.id)])
            if mail and rec.criteria_hold_notification:
                raise UserError(
                    _('Quality Hold Notification Template Already Marked in %s.' % mail.name)
                )


class Partner(models.Model):
    _inherit = "res.partner"

    criteria_hold_applications = fields.Many2many('hr.applicant','partner_user_crit_rel','partner_id','applicant_id', compute="_compute_crit_applicants")
    def _compute_crit_applicants(self):
        for this in self:
            this.criteria_hold_applications = False
            partner_user = self.env['res.users'].search([('partner_id','=',this.id)])
            if partner_user and len(partner_user) > 0:
                if partner_user.has_group('operational_apply_criteria_restrict.group_recruitment_analyst'):
                    hold_applicants = self.env['hr.applicant'].search([('crit_hold','=',True)])
                    if hold_applicants and len(hold_applicants) > 0:
                        this.criteria_hold_applications = [(6,0,hold_applicants.ids)]
class MilitaryStatus(models.Model):
    _name = 'military.status'
    name = fields.Char(string="Name")
    related_military_status = fields.Selection([('Completed','Completed'),
                                        ('Will serve','Will serve'),
                                        ('Exempted','Exempted'),
                                        ('Postponed','Postponed'),
                                        ('Female','Female')
                                        ],string="Military Status")
class HrEmployee(models.Model):
    _inherit = 'hr.job'

    restricted_criteria=fields.Boolean(string="Restricted Criteria")

    # Tab restiction fields
    age_from_restrict=fields.Integer('Age From')
    age_to_restrict=fields.Integer('Age To')
    nationality_restrict=fields.Many2many('res.country',string="Nationality")
    gender_restrict=fields.Selection([('male','Male'),('female','Female')],string="Gender")
    governorate_restrict=fields.Many2many('res.country.state',string="Governorate")
    area_restrict= fields.Many2many('city.area',string="Where do you live / Area")
    # military_status_restict=fields.Selection([('Completed','Completed'),
    #                                     ('Will serve','Will serve'),
    #                                     ('Exempted','Exempted'),
    #                                     ('Postponed','Postponed'),
    #                                     ('Female','Female')
    #                                     ],string="Military Status")
    military_status_restict=fields.Many2many('military.status',string="Military Status")

    graduation_status_restrict=fields.Selection([('graduated','Graduated'),
                                        ('notgraduated','Under Grade')],string="Graduation status" )
    university_restrict= fields.Many2many('hr.institute',string="University")
    faculty_restrict=fields.Many2many('university.fac',string="Faculty")
    english_level_restict=fields.Selection([('Fluent','Fluent'),
                                        ('Excellent','Excellent'),
                                        ('V.Good','V.Good'),
                                        ('Good','Good'),
                                        ('Fair','Fair')],string="Your English Level")
    social_insurance_restict= fields.Selection([('Yes','Yes'),
                                        ('No','No')],string="Do You have Social insurance")
    worked_4_raya_restrict=fields.Selection([('Yes','Yes'),
                                        ('No','No')],string="Did You work before at Raya")
    pc_laptop_restrict=fields.Selection([('Yes','Yes'),
                                        ('No','No')],string="Do You Have PC or Laptop")
    internet_con_restrict=fields.Selection([('Yes','Yes'),
                                        ('No','No')],string="Do You have Internet Connection")
    connection_speed_restict=fields.Selection([('less_10','Less than 10 Mbps'),
                                        ('10 Mbps','10 Mbps'),
                                        ('More10Mbps','More than 10 Mbps')],string="What is your Connection Speed")
    internet_provider_restrict=fields.Selection([('WE','WE'),('vodafone','Vodafone'),('Orange','Orange'),('Other','Other')],string="Connection Provider Name")
    type_of_connection_restrict= fields.Selection([('adsl','ADSL'),
        ('adsl','ADSL'),
        ('mobile_data','Mobile Data'),
        ('other','Other')],string="Type Of Connection")
    ready_work_from_home_restrict= fields.Selection([('Yes','Yes'),
                                        ('No','No')],string="Are You ready to work from home")
    operating_sys_restrict= fields.Selection([('Windows XP','Windows XP'),
                                        ('Windows 7','Windows 7'),
                                        ('Windows 8','Windows 8'),
                                        ('Windows 10','Windows 10'),
                                        ('Linux','Linux'),
                                        ('macOS','macOS'),
                                        ('Unix','Unix')],string="Your Operating System")
    indebendancy_restict=fields.Selection([('Independently','Independently'),
                            ('Within a Team','Within a Team'),
                            ('Both','Both')],string="Do You Prefer Working Independently or within a Team")
    prev_work_experience_restrict= fields.Selection([('Yes','Yes'),
                                        ('No','No')],string="Do you have Previous Work Experience")
    rotational_shifts_restict=fields.Selection([('Yes','Yes'),
                                        ('No','No')],string="Are you fine with rotational shifts")

class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    def notify_criteria_hold(self):
        op_criteria_team = self.env.ref('operational_apply_criteria_restrict.group_recruitment_analyst').users
        ir_model_data = self.env['ir.model.data']
        template_id = ir_model_data.get_object_reference('operational_apply_criteria_restrict', 'email_template_criteria_hold_notify')[1]
        for user in op_criteria_team:
            if user.partner_id.criteria_hold_applications and len(user.partner_id.criteria_hold_applications) > 0:
                self.env['mail.template'].browse(template_id).send_mail(user.id)


    crit_hold=fields.Boolean("Critria Hold")
    crit_hold_exception = fields.Boolean()
    # @api.model
    # def create(self, vals):
    #     in_nationality=False
    #     in_govern=False
    #     in_area=False
    #     in_uni=False
    #     in_faculty=False
    #     res = super(HrApplicant, self).create(vals)
    #     if res.job_category=='operational':
    #         if res.job_id.restricted_criteria:
    #             # AGE RESTTICT
    #             if res.job_id.age_from_restrict!=0 or res.job_id.age_to_restrict != 0:
    #                 if res.age == 0:
    #                     res.crit_hold=False
    #                 else:
    #                     if res.job_id.age_from_restrict != 0 and res.job_id.age_to_restrict != 0:
    #                         if not(res.age >= res.job_id.age_from_restrict and res.age <= res.job_id.age_to_restrict ):
    #                             res.crit_hold=True
    #                             return res
    #                     elif res.job_id.age_from_restrict != 0:
    #                         if res.age < res.job_id.age_from_restrict:
    #                             res.crit_hold=True
    #                             return res
    #                     elif res.job_id.age_to_restrict != 0:
    #                         if res.age > res.job_id.age_to_restrict:
    #                             res.crit_hold=True
    #                             return res
    #             # Nationality RESTTICT M2M
    #             if res.job_id.nationality_restrict:
    #                 if res.nationality == False:
    #                     res.crit_hold=False
    #                 else:
    #                     for nat in res.job_id.nationality_restrict:
    #                         if res.nationality == nat:
    #                             in_nationality=True
    #                             break
    #                         else:
    #                             in_nationality=False
    #                     if in_nationality==False and res.nationality:
    #                         res.crit_hold=True
    #                         return res
    #                     else:
    #                         res.crit_hold=False
    #
    #             # Gender RESTTICT
    #             if res.job_id.gender_restrict:
    #                 if res.gender == False:
    #                     res.crit_hold=False
    #                 else:
    #                     if res.gender!=res.job_id.gender_restrict:
    #                         res.crit_hold=True
    #                         return res
    #                     else:
    #                         res.crit_hold=False
    #             # Governorate RESTTICT M2M
    #             if res.job_id.governorate_restrict:
    #                 if res.state == False:
    #                     res.crit_hold=False
    #                 else:
    #                     for govern in res.job_id.governorate_restrict:
    #                         if res.state == govern:
    #                             in_govern=True
    #                             break
    #                         else:
    #                             in_govern=False
    #                     if in_govern==False and res.state:
    #                         res.crit_hold=True
    #                         return res
    #                     else:
    #                         res.crit_hold=False
    #
    #             # Area RESTTICT M2M
    #             if res.job_id.area_restrict:
    #                 if res.area == False:
    #                     res.crit_hold=False
    #                 else:
    #                     for area in res.job_id.area_restrict:
    #                         if res.area == area:
    #                             in_area=True
    #                             break
    #                         else:
    #                             in_area=False
    #                     if in_area==False and res.area:
    #                         res.crit_hold=True
    #                         return res
    #                     else:
    #                         res.crit_hold=False
    #             # # Military Status RESTTICT
    #             # if res.job_id.military_status_restict:
    #             #     if res.military_status!=res.job_id.military_status_restict:
    #             #         res.crit_hold=True
    #             # Military Status RESTTICT
    #             if len(res.job_id.military_status_restict) > 0:
    #                 list_resticted = []
    #                 for line in res.job_id.military_status_restict:
    #                     list_resticted.append(line.related_military_status)
    #                 if res.military_status == False:
    #                     res.crit_hold=False
    #                 elif res.military_status not in list_resticted:
    #                     res.crit_hold=True
    #                     return res
    #                 else:
    #                     res.crit_hold=False
    #             # University RESTTICT M2M
    #             if res.job_id.university_restrict:
    #                 if res.university == False:
    #                     res.crit_hold=True
    #                     return res
    #                 else:
    #                     for uni in res.job_id.university_restrict:
    #                         if res.university == uni:
    #                             in_uni=True
    #                             break
    #                         else:
    #                             in_uni=False
    #                     if in_uni==False and res.university:
    #                         res.crit_hold=True
    #                         return res
    #                     else:
    #                         res.crit_hold=False
    #             # Faculty RESTTICT M2M
    #             if res.job_id.faculty_restrict:
    #                 if res.faculty:
    #                     res.crit_hold=False
    #                 else:
    #                     for fac in res.job_id.faculty_restrict:
    #                         if res.faculty == fac:
    #                             in_faculty=True
    #                             break
    #                         else:
    #                             in_faculty=False
    #                     if in_faculty==False and res.faculty:
    #                         res.crit_hold=True
    #                         return res
    #                     else:
    #                         res.crit_hold=False
    #             # English Level RESTTICT
    #             if res.job_id.english_level_restict:
    #                 if res.english_status == False:
    #                     res.crit_hold=False
    #                 else:
    #                     if res.english_status=="Fluent":
    #                         res.crit_hold=False
    #                     elif res.english_status=="Excellent"  and not res.job_id.english_level_restict=="Fluent":
    #                         res.crit_hold=False
    #                     elif res.english_status=="V.Good"  and not (res.job_id.english_level_restict=="Fluent" or res.job_id.english_level_restict=="Excellent"):
    #                         res.crit_hold=False
    #                     elif res.english_status=="Good"  and not (res.job_id.english_level_restict=="Fluent" or res.job_id.english_level_restict=="Excellent" or res.job_id.english_level_restict=="V.Good"):
    #                         res.crit_hold=False
    #                     elif res.english_status!=res.job_id.english_level_restict:
    #                         res.crit_hold=True
    #                         return res
    #             # Social insurance RESTTICT
    #             if res.job_id.social_insurance_restict:
    #                 if res.social_insurance == False:
    #                     res.crit_hold=False
    #                 else:
    #                     if res.social_insurance!=res.job_id.social_insurance_restict:
    #                         res.crit_hold=True
    #                         return res
    #                     else:
    #                         res.crit_hold=False
    #             # work before at Raya RESTTICT
    #             if res.job_id.worked_4_raya_restrict:
    #                 if res.worked_4_raya == False:
    #                     res.crit_hold=False
    #                 else:
    #                     if res.worked_4_raya!=res.job_id.worked_4_raya_restrict:
    #                         res.crit_hold=True
    #                         return res
    #                     else:
    #                         res.crit_hold=False
    #             # PC or Laptop RESTTICT
    #             if res.job_id.pc_laptop_restrict:
    #                 if res.pc_laptop == False:
    #                     res.crit_hold=False
    #                 else:
    #                     if res.pc_laptop != res.job_id.pc_laptop_restrict:
    #                         res.crit_hold=True
    #                         return res
    #                     else:
    #                         res.crit_hold=False
    #             # Internet Connection RESTTICT
    #             if res.job_id.internet_con_restrict:
    #                 if res.internet_con == False:
    #                     res.crit_hold=False
    #                 else:
    #                     if res.internet_con!=res.job_id.internet_con_restrict:
    #                         res.crit_hold=True
    #                         return res
    #                     else:
    #                         res.crit_hold=False
    #             # Connection Speed RESTTICT
    #             if res.job_id.connection_speed_restict:
    #                 if res.con_speed == False:
    #                     res.crit_hold=False
    #                 else:
    #                     if res.con_speed=="More10Mbps":
    #                         res.crit_hold=False
    #                     elif res.con_speed=="10 Mbps"  and not res.job_id.connection_speed_restict=="More10Mbps":
    #                         res.crit_hold=False
    #                     elif res.con_speed!=res.job_id.connection_speed_restict:
    #                         res.crit_hold=True
    #                         return res
    #             # Connection Provider RESTTICT
    #             if res.job_id.internet_provider_restrict:
    #                 if res.res.internet_provider == False:
    #                     res.crit_hold=False
    #                 else:
    #                     if res.internet_provider!=res.job_id.internet_provider_restrict:
    #                         res.crit_hold=True
    #                         return res
    #                     else:
    #                         res.crit_hold=False
    #             # Type Of Connection RESTTICT
    #             if res.job_id.type_of_connection_restrict:
    #                 if res.type_of_connection == False:
    #                     res.crit_hold=False
    #                 else:
    #                     if res.type_of_connection!=res.job_id.type_of_connection_restrict:
    #                         res.crit_hold=True
    #                         return res
    #                     else:
    #                         res.crit_hold=False
    #             #  work from home RESTTICT
    #             if res.job_id.ready_work_from_home_restrict:
    #                 if res.ready_work_from_home == False:
    #                     res.crit_hold=False
    #                 else:
    #                     if res.ready_work_from_home!=res.job_id.ready_work_from_home_restrict:
    #                         res.crit_hold=True
    #                         return res
    #                     else:
    #                         res.crit_hold=False
    #             # Operating System RESTTICT
    #             if res.job_id.operating_sys_restrict:
    #                 if res.operating_sys == False:
    #                     res.crit_hold=False
    #                 else:
    #                     if res.operating_sys!=res.job_id.operating_sys_restrict:
    #                         res.crit_hold=True
    #                         return res
    #                     else:
    #                         res.crit_hold=False
    #             # Working Independently or within a Team RESTTIC
    #             if res.job_id.indebendancy_restict:
    #                 if res.indebendancy == False:
    #                     res.crit_hold=False
    #                 else:
    #                     if res.indebendancy=="Both":
    #                         res.crit_hold=False
    #                     elif res.indebendancy!=res.job_id.indebendancy_restict:
    #                         res.crit_hold=True
    #                         return res
    #             # Previous Work Experience RESTTICT
    #             if res.job_id.prev_work_experience_restrict:
    #                 if res.prev_work_experience:
    #                     res.crit_hold=False
    #                 else:
    #                     if res.job_id.prev_work_experience_restrict=='yes':
    #                         if res.prev_work_experience!=res.job_id.prev_work_experience_restrict:
    #                             res.crit_hold=True
    #                             return res
    #                         else:
    #                             res.crit_hold=False
    #                     else:
    #                         res.crit_hold=False
    #             # rotational shifts RESTTICT
    #             if res.job_id.rotational_shifts_restict:
    #                 if res.rotational_shifts:
    #                     res.crit_hold=False
    #                 else:
    #                     if res.job_id.rotational_shifts_restict=='yes':
    #                         if res.rotational_shifts!=res.job_id.rotational_shifts_restict:
    #                             res.crit_hold=True
    #                             return res
    #                         else:
    #                             res.crit_hold=False
    #                     else:
    #                         res.crit_hold=False
    #
    #
    #     return res

    def write(self, vals):
        in_nationality=False
        in_govern=False
        in_area=False
        in_uni=False
        in_faculty=False
        if self.job_category=='operational':
            if self.job_id.restricted_criteria:
                if self.crit_hold==True:
                    vals['crit_hold']=False
                # AGE RESTTICT
                if self.job_id.age_from_restrict!=0 or self.job_id.age_to_restrict != 0:
                    if self.age == 0:
                        vals['crit_hold']=False
                    else:
                        if self.job_id.age_from_restrict != 0 and self.job_id.age_to_restrict != 0:
                            if not(self.age >= self.job_id.age_from_restrict and self.age <= self.job_id.age_to_restrict ):
                                vals['crit_hold']=True
                                if self.crit_hold_exception:
                                    vals['crit_hold']=False
                                res = super(HrApplicant, self).write(vals)
                                return res
                        elif self.job_id.age_from_restrict != 0:
                            if self.age < self.job_id.age_from_restrict:
                                vals['crit_hold']=True
                                if self.crit_hold_exception:
                                    vals['crit_hold']=False
                                res = super(HrApplicant, self).write(vals)
                                return res
                        elif self.job_id.age_to_restrict != 0:
                            if self.age > self.job_id.age_to_restrict:
                                vals['crit_hold']=True
                                if self.crit_hold_exception:
                                    vals['crit_hold']=False
                                res = super(HrApplicant, self).write(vals)
                                return res
                        else:
                            vals['crit_hold']=False
                # Nationality RESTTICT M2M
                if self.job_id.nationality_restrict:
                    if self.nationality == False:
                        vals['crit_hold']=False
                    else:
                        for nat in self.job_id.nationality_restrict:
                            if self.nationality == nat:
                                in_nationality=True
                                break
                            else:
                                in_nationality=False
                        if in_nationality==False:
                            vals['crit_hold']=True
                            if self.crit_hold_exception:
                                vals['crit_hold']=False
                            res = super(HrApplicant, self).write(vals)
                            return res
                        else:
                            vals['crit_hold']=False
                # Gender RESTTICT
                if self.job_id.gender_restrict:
                    if self.gender == False:
                        vals['crit_hold']=False
                    else:
                        if self.gender!=self.job_id.gender_restrict:
                            vals['crit_hold']=True
                            if self.crit_hold_exception:
                                vals['crit_hold']=False
                            res = super(HrApplicant, self).write(vals)
                            return res
                        else:
                            vals['crit_hold']=False
                # Governorate RESTTICT M2M
                if self.job_id.governorate_restrict:
                    if self.state == False:
                        vals['crit_hold']=False
                    else:
                        for govern in self.job_id.governorate_restrict:
                            if self.state == govern:
                                in_govern=True
                                break
                            else:
                                in_govern=False
                        if in_govern==False and self.state:
                            vals['crit_hold']=True
                            if self.crit_hold_exception:
                                vals['crit_hold']=False
                            res = super(HrApplicant, self).write(vals)
                            return res
                        else:
                            vals['crit_hold']=False
                # Area RESTTICT M2M
                if self.job_id.area_restrict:
                    if self.area == False:
                        vals['crit_hold']=False
                    else:
                        for area in self.job_id.area_restrict:
                            if self.area == area:
                                in_area=True
                                break
                            else:
                                in_area=False
                        if in_area==False:
                            vals['crit_hold']=True
                            if self.crit_hold_exception:
                                vals['crit_hold']=False
                            res = super(HrApplicant, self).write(vals)
                            return res
                        else:
                            vals['crit_hold']=False
                # # Military Status RESTTICT
                # if self.job_id.military_status_restict:
                #     if self.military_status!=self.job_id.military_status_restict:
                #         vals['crit_hold']=True
                #     else:
                #         vals['crit_hold']=False
                # Military Status RESTTICT
                if len(self.job_id.military_status_restict) > 0:
                    list_resticted = []
                    for line in self.job_id.military_status_restict:
                        list_resticted.append(line.related_military_status)
                    if self.military_status not in list_resticted:
                        vals['crit_hold']=True
                        if self.crit_hold_exception:
                            vals['crit_hold']=False
                        res = super(HrApplicant, self).write(vals)
                        return res
                    else:
                        vals['crit_hold']=False
                # University RESTTICT M2M
                if self.job_id.university_restrict:
                    if self.university == False:
                        vals['crit_hold']=True
                        if self.crit_hold_exception:
                            vals['crit_hold']=False
                    else:
                        for uni in self.job_id.university_restrict:
                            if self.university == uni:
                                in_uni=True
                                break
                            else:
                                in_uni=False
                        if in_uni==False and self.university:
                            vals['crit_hold']=True
                            if self.crit_hold_exception:
                                vals['crit_hold']=False
                            res = super(HrApplicant, self).write(vals)
                            return res
                        else:
                            vals['crit_hold']=False
                # Faculty RESTTICT M2M
                if self.job_id.faculty_restrict:
                    if self.faculty:
                        vals['crit_hold']=False
                    else:
                        for fac in self.job_id.faculty_restrict:
                            if self.faculty == fac:
                                in_faculty=True
                                break
                            else:
                                in_faculty=False
                        if in_faculty==False and self.faculty:
                            vals['crit_hold']=True
                            if self.crit_hold_exception:
                                vals['crit_hold']=False
                            res = super(HrApplicant, self).write(vals)
                            return res
                        else:
                            vals['crit_hold']=False
                # English Level RESTTICT
                if self.job_id.english_level_restict:
                    if self.english_status == False:
                        vals['crit_hold']=False
                    else:
                        if self.english_status=="Fluent":
                            vals['crit_hold']=False
                        elif self.english_status=="Excellent"  and not self.job_id.english_level_restict=="Fluent":
                            vals['crit_hold']=False
                        elif self.english_status=="V.Good"  and not (self.job_id.english_level_restict=="Fluent" or self.job_id.english_level_restict=="Excellent"):
                            vals['crit_hold']=False
                        elif self.english_status=="Good"  and not (self.job_id.english_level_restict=="Fluent" or self.job_id.english_level_restict=="Excellent" or self.job_id.english_level_restict=="V.Good"):
                            vals['crit_hold']=False
                        elif self.english_status!=self.job_id.english_level_restict:
                            vals['crit_hold']=True
                            if self.crit_hold_exception:
                                vals['crit_hold']=False
                            res = super(HrApplicant, self).write(vals)
                            return res
                        else:
                            vals['crit_hold']=False
                # Social insurance RESTTICT
                if self.job_id.social_insurance_restict:
                    if self.social_insurance == False:
                        vals['crit_hold']=False
                    else:
                        if self.social_insurance!=self.job_id.social_insurance_restict:
                            vals['crit_hold']=True
                            if self.crit_hold_exception:
                                vals['crit_hold']=False
                            res = super(HrApplicant, self).write(vals)
                            return res
                        else:
                            vals['crit_hold']=False
                # work before at Raya RESTTICT
                if self.job_id.worked_4_raya_restrict:
                    if self.worked_4_raya == False:
                        vals['crit_hold']=False
                    else:
                        if self.worked_4_raya!=self.job_id.worked_4_raya_restrict:
                            vals['crit_hold']=True
                            if self.crit_hold_exception:
                                vals['crit_hold']=False
                            res = super(HrApplicant, self).write(vals)
                            return res
                        else:
                            vals['crit_hold']=False
                # PC or Laptop RESTTICT
                if self.job_id.pc_laptop_restrict:
                    if self.pc_laptop == False:
                        vals['crit_hold']=False
                    else:
                        if self.prev_work_experience!=self.job_id.pc_laptop_restrict:
                            vals['crit_hold']=True
                            if self.crit_hold_exception:
                                vals['crit_hold']=False
                            res = super(HrApplicant, self).write(vals)
                            return res
                        else:
                            vals['crit_hold']=False
                # Internet Connection RESTTICT
                if self.job_id.internet_con_restrict:
                    if self.internet_con == False:
                        vals['crit_hold']=False
                    else:
                        if self.internet_con!=self.job_id.internet_con_restrict:
                            vals['crit_hold']=True
                            if self.crit_hold_exception:
                                vals['crit_hold']=False
                            res = super(HrApplicant, self).write(vals)
                            return res
                        else:
                            vals['crit_hold']=False
                # Connection Speed RESTTICT
                if self.job_id.connection_speed_restict:
                    if self.con_speed == False:
                        vals['crit_hold']=False
                    else:
                        if self.con_speed=="More10Mbps":
                            vals['crit_hold']=False
                        elif self.con_speed=="10 Mbps"  and not self.job_id.connection_speed_restict=="More10Mbps":
                            vals['crit_hold']=False
                        elif self.con_speed!=self.job_id.connection_speed_restict:
                            vals['crit_hold']=True
                            if self.crit_hold_exception:
                                vals['crit_hold']=False
                            res = super(HrApplicant, self).write(vals)
                            return res
                        else:
                            vals['crit_hold']=False
                # Connection Provider RESTTICT
                if self.job_id.internet_provider_restrict:
                    if self.self.internet_provider == False:
                        vals['crit_hold']=False
                    else:
                        if self.type_of_connection!=self.job_id.internet_provider_restrict:
                            vals['crit_hold']=True
                            if self.crit_hold_exception:
                                vals['crit_hold']=False
                            res = super(HrApplicant, self).write(vals)
                            return res
                        else:
                            vals['crit_hold']=False
                # Type Of Connection RESTTICT
                if self.job_id.type_of_connection_restrict:
                    if self.type_of_connection == False:
                        vals['crit_hold']=False
                    else:
                        if self.type_of_connection!=self.job_id.type_of_connection_restrict:
                            vals['crit_hold']=True
                            if self.crit_hold_exception:
                                vals['crit_hold']=False
                            res = super(HrApplicant, self).write(vals)
                            return res
                        else:
                            vals['crit_hold']=False
                #  work from home RESTTICT
                if self.job_id.ready_work_from_home_restrict:
                    if self.ready_work_from_home == False:
                        vals['crit_hold']=False
                    else:
                        if self.ready_work_from_home!=self.job_id.ready_work_from_home_restrict:
                            vals['crit_hold']=True
                            if self.crit_hold_exception:
                                vals['crit_hold']=False
                            res = super(HrApplicant, self).write(vals)
                            return res
                        else:
                            vals['crit_hold']=False
                # Operating System RESTTICT
                if self.job_id.operating_sys_restrict:
                    if self.operating_sys == False:
                        vals['crit_hold']=False
                    else:
                        if self.operating_sys!=self.job_id.operating_sys_restrict:
                            vals['crit_hold']=True
                            if self.crit_hold_exception:
                                vals['crit_hold']=False
                            res = super(HrApplicant, self).write(vals)
                            return res
                        else:
                            vals['crit_hold']=False
                # Working Independently or within a Team RESTTIC
                if self.job_id.indebendancy_restict:
                    if self.indebendancy == False:
                        vals['crit_hold']=False
                    else:
                        if self.indebendancy=="Both":
                            vals['crit_hold']=False
                        elif self.indebendancy!=self.job_id.indebendancy_restict:
                            vals['crit_hold']=True
                            if self.crit_hold_exception:
                                vals['crit_hold']=False
                            res = super(HrApplicant, self).write(vals)
                            return res
                        else:
                            vals['crit_hold']=False
                # Previous Work Experience RESTTICT
                if self.job_id.prev_work_experience_restrict:
                    if self.prev_work_experience:
                        vals['crit_hold']=False
                    else:
                        if self.job_id.rotational_shifts_restict=='yes':
                            if self.rotational_shifts!=self.job_id.prev_work_experience_restrict:
                                vals['crit_hold']=True
                                if self.crit_hold_exception:
                                    vals['crit_hold']=False
                                res = super(HrApplicant, self).write(vals)
                                return res
                            else:
                                vals['crit_hold']=False
                        else:
                            vals['crit_hold']=False
                # rotational shifts RESTTICT
                if self.job_id.rotational_shifts_restict:
                    if self.rotational_shifts:
                        vals['crit_hold']=False
                    else:
                        if self.job_id.rotational_shifts_restict=='yes':
                            if self.rotational_shifts!=self.job_id.rotational_shifts_restict:
                                vals['crit_hold']=True
                                if self.crit_hold_exception:
                                    vals['crit_hold']=False
                                res = super(HrApplicant, self).write(vals)
                                return res
                            else:
                                vals['crit_hold']=False
                        else:
                            vals['crit_hold']=False
            else:
                vals['crit_hold']=False
        else:
            vals['crit_hold']=False
        res = super(HrApplicant, self).write(vals)
        return res
    @api.constrains('stage_id')#onchange('stage_id')
    def restict_crit_hold(self):
        for this in self:
            if this.job_category=='operational':
                stage_line=self.env['hr.recruitment.stage'].search([('job_category','=','operational'),('is_o_initial','=',True)],limit=1)
                if this.crit_hold==True and this.stage_id != stage_line and this.stage_id != False :
                    raise UserError(_('This application is on Restricted Criteria Hold.'))

    def crit_hold_release(self):
        for this in self:
            this.crit_hold_exception=True
