# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

class hr_recruitment_o_double_hiring(models.Model):
    _inherit='hr.applicant'

    is_hold=fields.Boolean(String="Hold")
    is_o_initial=fields.Boolean(compute='get_is_o_initial_o',sorted=True)
    is_o_final=fields.Boolean(compute='get_is_o_final_o',sorted=True)

    @api.onchange('hiring_request')
    def check_double_operational(self):
        if isinstance(self.id, int):
            if self.hiring_request and self.job_category == 'operational':
                old_application = self.env['hr.applicant'].search([('job_category','=','operational'),('national_id','=',self.national_id),('job_id','=',self.job_id.id),('hiring_request','=',self.hiring_request.id),('id','!=',int(str(self.id).replace('NewId_','')))])
                if len(old_application) > 0:
                    raise ValidationError(_("The Application Already Exist, You can't Apply Twice"))
    @api.onchange('stage_id')
    def get_is_o_final_o(self):
        for this in self:
            this.is_o_final=this.stage_id.is_o_final
    @api.onchange('stage_id')
    def get_is_o_initial_o(self):
        for this in self:
            self.is_o_initial=this.stage_id.is_o_initial
    @api.onchange('stage_id')
    def check_holding_o(self):
        if self.is_hold==True:
            raise ValidationError('This applicant currently has another Hirring Process')
    @api.model
    def create(self, vals):
        res = super(hr_recruitment_o_double_hiring, self).create(vals)
        if res.job_category=='operational':
            for this in res:
                old_line = this.env['hr.applicant'].search([('job_category','=','operational'),('national_id','ilike',res.national_id),('id','!=',res.id),('active','=',True)])
                print(old_line)
                if len(old_line)>=1:
                    for line in old_line:
                        if line.stage_id.is_o_final != True and line.stage_id.is_o_initial != True:
                            print("1111111111111111111111111111111111111111111111111")
                            res.is_hold=True
                            break
                        else:
                            res.is_hold=False
        if res.job_category=='operational':
            stage_line=self.env['hr.recruitment.stage'].search([('job_category','=','operational'),('is_o_initial','=',True)],limit=1)
            res.stage_id=stage_line.id
        if res.job_category == 'operational':
            emp = self.env['hr.employee'].search([('identification_id','=',res.national_id)])
            if len(emp) > 0:
                raise ValidationError(_('You Should Apply Through Internal Transfer'))
        return res
    @api.onchange('emp_id')
    def get_national_id_o(self):
        lines=self.env['hr.employee'].search([('id','=',self.emp_id.id)])
        if len(lines)>=1:
            self.national_id=lines.identification_id

    @api.onchange('national_id')
    def get_national_id_emp_o(self):
        lines=self.env['hr.employee'].search([('identification_id','=',self.national_id)],limit=1)
        if len(lines)>=1:
            self.emp_id=lines

    @api.onchange('job_id')
    def check_applied_job_o(self):
        if self.job_category=='operational':
            self.stage_id=False

    @api.onchange('stage_id')
    def check_is_holding_o(self):
        # for this in self:
        #     if this.job_category=='operational':
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
        #                 if line.stage_id.is_o_final != True and line.stage_id.is_o_initial != True :
        #                     line.is_hold=True
        #                 else:
        #                     line.is_hold=False
        if self.job_category=='operational':
            for this in self:
                t=str(self.id).split('_')[-1]
                if self.stage_id :
                    if not isinstance(t, int):
                        if this.is_o_initial == False and this.is_o_final ==False:
                            old_line = this.env['hr.applicant'].search([('job_category','=','operational'),('national_id','ilike',this.national_id),('is_o_initial','!=',True),('is_o_final','!=',True),('active','=',True),('id','!=',t)])
                            if len(old_line)>=1:
                                for line in old_line:
                                    print("2222222222222222222222222222222222222222222222")
                                    line.is_hold=True
                            else:
                                for line in old_line:
                                    line.is_hold=False
                        elif this.is_o_initial ==True and this.is_o_final==False:
                            old_line = this.env['hr.applicant'].search([('job_category','=','operational'),('national_id','ilike',this.national_id),('is_o_initial','!=',True),('is_o_final','!=',True),('active','=',True),('id','!=',t)])
                            if len(old_line)>=1:
                                for line in old_line:
                                    line.is_hold=False
                            else:
                                for line in old_line:
                                    print("333333333333333333333333333333333333333333")
                                    line.is_hold=True
                        elif this.is_o_initial !=True and this.is_o_final ==True:
                            old_line = this.env['hr.applicant'].search([('job_category','=','operational'),('national_id','ilike',this.national_id),('is_o_initial','!=',True),('is_o_final','!=',True),('active','=',True)])
                            if len(old_line)>=1:
                                for line in old_line:
                                    line.is_hold=False
                            else:
                                for line in old_line:
                                    print("44444444444444444444444444444444444")
                                    line.is_hold=True
                        else:
                            this.is_hold=False


    def toggle_active(self):
        res=super(hr_recruitment_o_double_hiring, self).toggle_active()
        for this in self:
            if this.job_category=='operational':
                old_line = this.env['hr.applicant'].search([('job_category','=','operational'),('national_id','ilike',this.national_id),('active','=',True)])
                if len(old_line)>=1:
                    for line in old_line:
                        if line.stage_id.is_o_final != True and line.stage_id.is_o_initial != True :
                            print("555555555555555555555555555555555")
                            line.is_hold=True
                        else:
                            line.is_hold=False
        return res
    def archive_applicant_o(self):
        for this in self:
            if this.job_category=='operational':
                old_line = this.env['hr.applicant'].search([('job_category','=','operational'),('national_id','ilike',this.national_id),('active','=',True)])
                if len(old_line)>=1:
                    for line in old_line:
                        if line.stage_id.is_o_final != True and line.stage_id.is_o_initial != True :
                            print("66666666666666666666666666666666")
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
            if this.job_category=='operational':
                old_line = this.env['hr.applicant'].search([('job_category','=','operational'),('national_id','ilike',this.national_id),('active','=',True)])
                if len(old_line)>=1:
                    for line in old_line:
                        if line.stage_id.is_o_final != True and line.stage_id.is_o_initial != True :
                            print("777777777777777777777777777777777777777")
                            line.is_hold=True
                        else:
                            line.is_hold=False
        return super(hr_recruitment_o_double_hiring, self).unlink()
