# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

class hr_recruitment_double_hiring(models.Model):
    _inherit='hr.applicant'

    is_hold=fields.Boolean(String="Hold")
    is_initial=fields.Boolean(compute='get_is_initial',sorted=True)
    is_final=fields.Boolean(compute='get_is_final',sorted=True)


    @api.onchange('stage_id')
    def get_is_final(self):
        for this in self:
            this.is_final=this.stage_id.is_final
    @api.onchange('stage_id')
    def get_is_initial(self):
        for this in self:
            self.is_initial=this.stage_id.is_initial
    @api.onchange('stage_id')
    def check_holding(self):
        if self.is_hold==True:
            raise ValidationError('This applicant currently has another Hirring Process')
    @api.model
    def create(self, vals):
        res = super(hr_recruitment_double_hiring, self).create(vals)
        if res.job_category=='talent':
            for this in res:
                old_line = this.env['hr.applicant'].search([('job_category','=','talent'),('national_id','ilike',res.national_id),('id','!=',res.id),('active','=',True)])
                print(old_line)
                if len(old_line)>=1:
                    for line in old_line:
                        if line.stage_id.is_final != True and line.stage_id.is_initial != True:
                            print("8888888888888888888888888888")
                            res.is_hold=True
                            break
                        else:
                            res.is_hold=False
        if res.job_category=='talent':
            stage_line=self.env['hr.recruitment.stage'].search([('job_category','=','talent'),('is_initial','=',True)],limit=1)
            res.stage_id=stage_line.id
        elif res.job_category=='operational':
            stage_line=self.env['hr.recruitment.stage'].search([('job_category','=','operational'),('is_o_initial','=',True)],limit=1)
            res.stage_id=stage_line.id
        return res

    @api.onchange('emp_id')
    def get_national_id(self):
        lines=self.env['hr.employee'].search([('id','=',self.emp_id.id)])
        if len(lines)>=1:
            self.national_id=lines.identification_id

    @api.onchange('national_id')
    def get_national_id_emp(self):
        lines=self.env['hr.employee'].search([('identification_id','=',self.national_id)],limit=1)
        if len(lines)>=1:
            self.emp_id=lines

    @api.onchange('job_id')
    def check_applied_job(self):
        if self.job_category=='talent':
            self.stage_id=False

    @api.onchange('stage_id')
    def check_is_holding(self):
        # for this in self:
        #     if this.job_category=='talent':
        #         old_line = this.env['hr.applicant'].search([('national_id','ilike',this.national_id),('active','=',True)])
        #         print("*******************************")
        #         print(old_line)
        #         print(old_line)
        #         print(old_line)
        #         print(old_line)
        #         print(old_line)
        #         print("*******************************")
        #         if len(old_line)>=1:
        #             for line in old_line:
        #                 if line.stage_id.is_final != True and line.stage_id.is_initial != True :
        #                     line.is_hold=True
        #                 else:
        #                     line.is_hold=False
        if self.job_category=='talent':
            for this in self:
                t=str(self.id).split('_')[-1]
                if self.stage_id :
                    if not isinstance(t, int):
                        if this.is_initial == False and this.is_final ==False:
                            old_line = this.env['hr.applicant'].search([('job_category','=','talent'),('national_id','ilike',this.national_id),('is_initial','!=',True),('is_final','!=',True),('active','=',True),('id','!=',t)])
                            if len(old_line)>=1:
                                for line in old_line:
                                    print("999999999999999999999999")
                                    line.is_hold=True
                            else:
                                for line in old_line:
                                    line.is_hold=False
                        elif this.is_initial ==True and this.is_final==False:
                            old_line = this.env['hr.applicant'].search([('job_category','=','talent'),('national_id','ilike',this.national_id),('is_initial','!=',True),('is_final','!=',True),('active','=',True),('id','!=',t)])
                            if len(old_line)>=1:
                                for line in old_line:
                                    line.is_hold=False
                            else:
                                for line in old_line:
                                    print("1000000000000000000000000000")
                                    line.is_hold=True
                        elif this.is_initial !=True and this.is_final ==True:
                            old_line = this.env['hr.applicant'].search([('job_category','=','talent'),('national_id','ilike',this.national_id),('is_initial','!=',True),('is_final','!=',True),('active','=',True)])
                            if len(old_line)>=1:
                                for line in old_line:
                                    line.is_hold=False
                            else:
                                for line in old_line:
                                    print("200000000000000000000000000000")
                                    line.is_hold=True
                        else:
                            this.is_hold=False


    def toggle_active(self):
        res=super(hr_recruitment_double_hiring, self).toggle_active()
        for this in self:
            if this.job_category=='talent':
                old_line = this.env['hr.applicant'].search([('job_category','=','talent'),('national_id','ilike',this.national_id),('active','=',True)])
                if len(old_line)>=1:
                    for line in old_line:
                        if line.stage_id.is_final != True and line.stage_id.is_initial != True :
                            print("3000000000000000000000000")
                            line.is_hold=True
                        else:
                            line.is_hold=False
        return res
    def archive_applicant(self):
        for this in self:
            if this.job_category=='talent':
                old_line = this.env['hr.applicant'].search([('job_category','=','talent'),('national_id','ilike',this.national_id),('active','=',True)])
                if len(old_line)>=1:
                    for line in old_line:
                        if line.stage_id.is_final != True and line.stage_id.is_initial != True :
                            print("40000000000000000000000")
                            line.is_hold=True
                        else:
                            line.is_hold=False
        return {
        'type': 'ir.actions.act_window',
        'name': _('Refuse Reason'),
        'res_model': 'applicant.get.refuse.reason',
        'view_mode': 'form',
        'target': 'new',
        'context': {'default_applicant_ids': self.ids, 'active_test': False},
        'views': [[False, 'form']]
    }
    def unlink(self):
        for this in self:
            if this.job_category=='talent':
                old_line = this.env['hr.applicant'].search([('job_category','=','talent'),('national_id','ilike',this.national_id),('active','=',True)])
                if len(old_line)>=1:
                    for line in old_line:
                        if line.stage_id.is_final != True and line.stage_id.is_initial != True :
                            print("50000000000000000000000000")
                            line.is_hold=True
                        else:
                            line.is_hold=False
        return super(hr_recruitment_double_hiring, self).unlink()
