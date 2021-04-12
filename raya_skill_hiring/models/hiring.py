# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError,UserError



class HrTalent(models.Model):
    _name = 'hr.skill.clone.hire'


    skill_type_id = fields.Many2one('hr.skill.type')
    skill_id = fields.Many2one('hr.skill')
    skill_level_id = fields.Many2one('hr.skill.level')

    ##################################################################
    ###### hiring.request
    ##################################################################
    hiring_tech_talent_id = fields.Many2one('hiring.request')
    hiring_non_tech_talent_id = fields.Many2one('hiring.request')
    hiring_lang_talent_id = fields.Many2one('hiring.request')
    ###############################################################

    @api.onchange('skill_type_id')
    def _update_skills_domain(self):
        if self.skill_type_id:
            ids = self.env['hr.skill'].search([('skill_type_id', '=', self.skill_type_id.id)]).ids
            return {
                'domain': {
                    'skill_id': [('id', 'in', ids)],
                }
            }

    @api.onchange('skill_id')
    def _update_levels_domain(self):

        if self.skill_level_id.id == False:
            if self.skill_type_id.id and self.skill_id.id:
                # cur_levels = self.env['hr.skill.level'].search()
                cur_levels = self.skill_type_id.mapped('skill_level_ids').ids
                ids = []

                rel = "("
                for level in cur_levels:
                    if level == cur_levels[-1]:
                        rel += str(level) +")"
                    else:
                        rel += str(level) +","

                sql = "SELECT level_id from hr_level_to_skills_rel where level_id in" +str(rel)+ " and skill_id = "+ str(self.skill_id.id)+" ;"
                self._cr.execute(sql)
                result = self._cr.fetchall()
                for value in result:
                    ids.append(value[0])


                return {
                    'domain': {
                        'skill_level_id': [('id', 'in', ids)],
                    }
                }

class raya_skill_hire(models.Model):
    _inherit = 'hiring.request'


    def _tech_val(self):
        val = self.env['hr.skill.type'].search([('skill_type','=','technical')])
        self.tech = val
    def _nontech_val(self):
        val = self.env['hr.skill.type'].search([('skill_type','=','non_technical')])
        self.nontech = val
    def _lang_val(self):
        val = self.env['hr.skill.type'].search([('skill_type','=','language')])
        self.lang = val

    # tech = fields.Many2one('hr.skill.type', compute= _tech_val)
    # nontech = fields.Many2one('hr.skill.type', compute= _nontech_val)
    # lang = fields.Many2one('hr.skill.type', compute= _lang_val)
    tech = fields.Many2one('hr.skill.type', default=lambda self: self.env['hr.skill.type'].search([('skill_type','=','technical')]), compute= _tech_val)
    nontech = fields.Many2one('hr.skill.type', default=lambda self: self.env['hr.skill.type'].search([('skill_type','=','non_technical')]), compute= _nontech_val)
    lang = fields.Many2one('hr.skill.type', default=lambda self: self.env['hr.skill.type'].search([('skill_type','=','language')]), compute= _lang_val)


    techskill_ids = fields.One2many(
        'emp.tech.skills', 'hire_id', 'Technical Skills')
    nontechskill_ids = fields.One2many(
        'emp.nontech.skills', 'hire_id', 'Non-Technical Skills')
    language_level_ids =  fields.One2many(
        'emp.lang.skills2', 'hire_id', 'Language Level')

    # Talent Skills
    techskill_talent_ids = fields.One2many(
        'hr.skill.clone.hire', 'hiring_tech_talent_id', 'Technical Skills')
    nontechskill_talent_ids = fields.One2many(
        'hr.skill.clone.hire', 'hiring_non_tech_talent_id', 'Non-Technical Skills')
    language_level_talent_ids =  fields.One2many(
        'hr.skill.clone.hire', 'hiring_lang_talent_id', 'Language Level')


    education_ids = fields.One2many(
        'employee.education', 'hire_id', 'Education')
    certification_ids = fields.One2many(
        'employee.certification', 'hire_id', 'Certification')
    profession_ids = fields.One2many(
        'employee.profession.job', 'hire_id', 'Professional Experience')

    @api.onchange('category')
    def update_job_domain(self):
        job_ids=[]
        if self.category == 'Talent Acq':
            job_ids = self.env['hr.job'].search([('job_category','=','talent')]).ids
        elif self.category:
            job_ids = self.env['hr.job'].search([('job_category','=',self.category)]).ids

        return {
                'domain': {
                    'job': [('id', 'in', job_ids)],
                }
        }
    @api.onchange('job')
    def update_lines(self):

        if self.job:
            # self.techskill_ids = self.job.techskill_ids
            # self.nontechskill_ids = self.job.nontechskill_ids
            # self.language_level_ids = self.job.language_level_ids

            # self.techskill_talent_ids = self.job.techskill_talent_ids
            # self.nontechskill_talent_ids = self.job.nontechskill_talent_ids
            # self.language_level_talent_ids = self.job.language_level_talent_ids

            self.techskill_talent_ids = [(5,0,0)]
            lines = []
            for line in self.job.techskill_talent_ids:
                vals = (0, 0, {
                                'skill_type_id': line.skill_type_id.id,
                                'skill_id': line.skill_id.id,
                                'skill_level_id': line.skill_level_id.id,
                                })
                lines.append(vals)

            self.techskill_talent_ids = lines

            self.nontechskill_talent_ids = [(5,0,0)]
            lines = []
            for line in self.job.nontechskill_talent_ids:
                vals = (0, 0, {
                                'skill_type_id': line.skill_type_id.id,
                                'skill_id': line.skill_id.id,
                                'skill_level_id': line.skill_level_id.id,
                                })
                lines.append(vals)

            self.nontechskill_talent_ids = lines

            self.language_level_talent_ids = [(5,0,0)]
            lines = []
            for line in self.job.language_level_talent_ids:
                vals = (0, 0, {
                                'skill_type_id': line.skill_type_id.id,
                                'skill_id': line.skill_id.id,
                                'skill_level_id': line.skill_level_id.id,
                                })
                lines.append(vals)

            self.language_level_talent_ids = lines

            self.education_ids = self.job.education_ids
            self.certification_ids = self.job.certification_ids
            self.profession_ids = self.job.profession_ids

            if self.category == 'Talent Acq':
                if self.job:
                    self.resume_line_ids=[(5,0,0)]
                    lines=[]
                    for line in self.job.resume_line_ids:
                        vals=(0,0,{
                            'name':line.name,
                            'date_start':line.date_start,
                            'date_end':line.date_end,
                            'description':line.description,
                            'line_type_id':line.line_type_id.id,
                            'display_type':line.display_type,
                        })
                        lines.append(vals)
                    self.resume_line_ids=lines

    def unlink(self):
        if self.state == 'draft':
            return super(raya_skill_hire, self).unlink()
        else:
            raise ValidationError(_("You can't delete not draft Hiring Request"))

class HireTechSkills(models.Model):
    _inherit = 'emp.tech.skills'
    _description = 'Employee Tech Skills'

    hire_id = fields.Many2one('hiring.request',string="Project")

class HireNonTechSkills(models.Model):
    _inherit = 'emp.nontech.skills'
    _description = 'Employee Non Tech Skills'

    hire_id = fields.Many2one('hiring.request',string="Project")

class HireTechSkills(models.Model):
    _inherit = 'emp.lang.skills2'
    _description = 'Employee language levels'

    hire_id = fields.Many2one('hiring.request',string="Project")

class HireEducation(models.Model):
    _inherit = 'employee.education'
    _description = 'Employee Education'

    hire_id = fields.Many2one('hiring.request',string="Project")

class HireCertification(models.Model):
    _inherit = 'employee.certification'
    _description = 'Employee Certification'

    hire_id = fields.Many2one('hiring.request',string="Project")

class HireProfessionJob(models.Model):
    _inherit = 'employee.profession.job'
    _description = 'Employee Profession'

    hire_id = fields.Many2one('hiring.request',string="Project")


class raya_skill_applicant(models.Model):
    _inherit = 'hr.applicant'



    def _update_domains(self,row):

        # if row.skill_level_id.id == False:
        if row.skill_type_id.id and row.skill_id.id:
            # cur_levels = self.env['hr.skill.level'].search()
            cur_levels = row.skill_type_id.mapped('skill_level_ids').ids
            ids = []

            rel = "("
            for level in cur_levels:
                if level == cur_levels[-1]:
                    rel += str(level) +")"
                else:
                    rel += str(level) +","

            sql = "SELECT level_id from hr_level_to_skills_rel where level_id in" +str(rel)+ " and skill_id = "+ str(row.skill_id.id)+" ;"
            self._cr.execute(sql)
            result = self._cr.fetchall()
            for value in result:
                ids.append(value[0])

            if row.skill_type_id.skill_type == 'non_technical':
                row.nontech_level_domain = [(5,)]
                row.nontech_level_domain = [(6,0,ids)]
                return {
                    'domain': {
                        'nontech_applicant_talent_level': [('id', 'in', ids)],
                    }
                }
            if row.skill_type_id.skill_type == 'technical':
                row.tech_level_domain = [(5,)]
                row.tech_level_domain = [(6,0,ids)]
                return {
                    'domain': {
                        'tech_applicant_talent_level': [('id', 'in', ids)],
                    }
                }
            if row.skill_type_id.skill_type == 'language':
                row.lang_level_domain = [(5,)]
                row.lang_level_domain = [(6,0,ids)]
                return {
                    'domain': {
                        'lang_applicant_talent_level': [('id', 'in', ids)],
                    }
                }

    @api.onchange('emp_id','hiring_request')
    def update_lines(self):
        if self.hiring_request:

            self.techskill_ids = self.hiring_request.techskill_ids
            self.nontechskill_ids = self.hiring_request.nontechskill_ids
            self.language_level_ids = self.hiring_request.language_level_ids

            # self.techskill_talent_ids = self.hiring_request.techskill_talent_ids
            self.techskill_talent_ids = [(5,0,0)]
            lines = []
            for line in self.hiring_request.techskill_talent_ids:

                vals = (0, 0, {
                                'skill_type_id': line.skill_type_id.id,
                                'skill_id': line.skill_id.id,
                                'skill_level_id': line.skill_level_id.id,
                                })
                lines.append(vals)

            self.techskill_talent_ids = lines

            if self.techskill_talent_ids:
                for row in self.techskill_talent_ids:
                    self._update_domains(row)

            # self.nontechskill_talent_ids = self.hiring_request.nontechskill_talent_ids
            self.nontechskill_talent_ids = [(5,0,0)]
            lines = []
            for line in self.hiring_request.nontechskill_talent_ids:
                vals = (0, 0, {
                                'skill_type_id': line.skill_type_id.id,
                                'skill_id': line.skill_id.id,
                                'skill_level_id': line.skill_level_id.id,
                                })
                lines.append(vals)

            self.nontechskill_talent_ids = lines

            if self.nontechskill_talent_ids:
                for row in self.nontechskill_talent_ids:
                    self._update_domains(row)

            # self.language_level_talent_ids = self.hiring_request.language_level_talent_ids
            self.language_level_talent_ids = [(5,0,0)]
            lines = []
            for line in self.hiring_request.language_level_talent_ids:
                vals = (0, 0, {
                                'skill_type_id': line.skill_type_id.id,
                                'skill_id': line.skill_id.id,
                                'skill_level_id': line.skill_level_id.id,
                                })
                lines.append(vals)

            self.language_level_talent_ids = lines

            if self.language_level_talent_ids:
                for row in self.language_level_talent_ids:
                    self._update_domains(row)

            self.education_ids = self.hiring_request.education_ids
            self.certification_ids = self.hiring_request.certification_ids
            self.profession_ids = self.hiring_request.profession_ids
            # if self.hiring_request.nontechskill_ids:
            #     self.language_level_ids = [(5,0,0)]
            #     for value in self.hiring_request.language_level_ids:
            #         val={
            #             'tech_id':value.tech_id.id,
            #             'levels':value.levels.id,
            #         }
            #         self.language_level_ids = [(0,0,val)]
            # else:
            #     self.language_level_ids = [(5,0,0)]
            if self.job_category == 'talent':
                if self.hiring_request:
                    self.resume_line_ids=[(5,0,0)]
                    lines=[]
                    for line in self.hiring_request.resume_line_ids:
                        vals=(0,0,{
                            'name':line.name,
                            'date_start':line.date_start,
                            'date_end':line.date_end,
                            'description':line.description,
                            'line_type_id':line.line_type_id.id,
                            'display_type':line.display_type,
                        })
                        lines.append(vals)
                    self.resume_line_ids=lines

        if self.emp_id:
            if self.emp_id.employee_skill_ids:
                tech_ids = self.emp_id.employee_skill_ids.filtered(lambda x:x.skill_type_id.skill_type == 'technical')
                non_tech_ids = self.emp_id.employee_skill_ids.filtered(lambda x:x.skill_type_id.skill_type == 'non_technical')
                lang_ids = self.emp_id.employee_skill_ids.filtered(lambda x:x.skill_type_id.skill_type == 'language')
                if self.job_category == 'operational':
                    if self.techskill_ids:
                        for tech in self.techskill_ids:
                            for emp in tech_ids:
                                if emp.skill_id.name.lower().strip() == tech.tech_id.name.lower().strip():
                                    tech.employee_level = emp.skill_level_id.id
                                    tech.validation_date = emp.validation_date
                    if self.nontechskill_ids:
                        for non_tech in self.nontechskill_ids:
                            for emp in non_tech_ids:
                                if emp.skill_id.name.lower().strip() == non_tech.nontech_id.name.lower().strip():
                                    non_tech.employee_level = emp.skill_level_id.id
                                    non_tech.validation_date = emp.validation_date
                    if self.language_level_ids:
                        for lang in self.language_level_ids:
                            for emp in lang_ids:
                                if emp.skill_id.name.lower().strip() == lang.tech_id.name.lower().strip():
                                    lang.employee_level = emp.skill_level_id.id
                                    lang.validation_date = emp.validation_date

                else:
                    if self.techskill_talent_ids:
                        for tech in self.techskill_talent_ids:
                            for emp in tech_ids:
                                if emp.skill_id.id == tech.skill_id.id:
                                    tech.tech_employee_talent_level = emp.skill_level_id.id
                                    tech.tech_validation_talent_date = emp.validation_date
                    if self.nontechskill_talent_ids:
                        for non_tech in self.nontechskill_talent_ids:
                            for emp in non_tech_ids:
                                if emp.skill_id.id == non_tech.skill_id.id:
                                    non_tech.nontech_employee_talent_level = emp.skill_level_id.id
                                    non_tech.nontech_validation_talent_date = emp.validation_date
                    if self.language_level_talent_ids:
                        for lang in self.language_level_talent_ids:
                            for emp in lang_ids:
                                if emp.skill_id.id == lang.skill_id.id:
                                    lang.lang_employee_talent_level = emp.skill_level_id.id
                                    lang.lang_validation_talent_date = emp.validation_date


        self.update_skills_from_partner()

    @api.onchange('partner_id')
    def update_skills_from_partner(self):
        if self.partner_id:
            if self.partner_id.nontechskill_ids:
                for value in self.nontechskill_talent_ids:
                    for part in self.partner_id.nontechskill_ids:
                        if value.skill_id.id == part.skill_id.id:
                            value.nontech_applicant_talent_level = part.nontech_applicant_talent_level

            if self.partner_id.techskill_ids:
                for value in self.techskill_talent_ids:
                    for part in self.partner_id.techskill_ids:
                        if value.skill_id.id == part.skill_id.id:
                            value.tech_applicant_talent_level = part.tech_applicant_talent_level

            if self.partner_id.language_level_talent_ids:
                for value in self.language_level_talent_ids:
                    for part in self.partner_id.language_level_talent_ids:
                        if value.skill_id.id == part.skill_id.id:
                            value.lang_applicant_talent_level = part.lang_applicant_talent_level













# applicant = str(self.id).split("_")[-1]
# sql = "SELECT name from emp_tech_skills inner join tech_tech on tech_id = tech_tech.id and applicant_id = "+ str(applicant)+";"
# self._cr.execute(sql)
# result = self._cr.fetchall()
# print(sql)
# print(result)
# for tech in result:
#     print(tech[0])
#     for emp in tech_ids:
#         if emp.skill_id.name.lower().strip() == tech[0].lower().strip():
#             tech.employee_level = emp.employee_level
#             tech.validation_date = emp.validation_date
