from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date 
class kpi_category(models.Model):
    _name = 'kpi_category'
    _description = 'kpi_category'

    name = fields.Char(string="Name")
    kpi_from = fields.Integer(string="KPI From",required=True)
    kpi_to = fields.Integer(string="KPI To",required=True)
    quartile_type=fields.Selection([('top','TOP Quartile'),('median','Median Quartile'),('bottom','Bottom Quartile')],string="Quartile Type",required=True)
    note = fields.Text(string="Note")
    @api.constrains('kpi_from')
    def _check_kpi_from_value(self):
        if self.kpi_from > 100 or self.kpi_from < 1:
           raise ValidationError('Enter Value for KPI From Between 1-100.')
    @api.constrains('kpi_to')
    def _check_kpi_to_value(self):
        if self.kpi_to > 100 or self.kpi_to < 1:
           raise ValidationError('Enter Value For KPI ToBetween 1-100.')
    
class HrEmployeePrivate(models.Model):
    _inherit = "hr.employee"
    evaluation_type=fields.Selection([('monthly','Monthly'),('quarterly','Quarterly')],string="Evaluation Type",default="monthly",required=True)
    employee_kpi=fields.One2many('employee_kpi_data','eva_type')
    @api.onchange('evaluation_type')
    def check_empty_lines(self):
        if self.evaluation_type and len(self.employee_kpi) > 0:
            raise ValidationError('You must Delete all KPIs to change the Evaluation types.')
    kpi_average=fields.Integer()
    @api.onchange('kpi_average')
    def pick_quartile(self):
        for this in self:
            quartiles=self.env['kpi_category'].search([('kpi_from','<=',this.employee_kpi.kpi),('kpi_to','>=',this.employee_kpi.kpi)])
            this.employee_kpi.quartile = quartiles.id
    #def _compute_kpi_average(self):
    #    res=0
    #    val=[]
       # for this in self:
       #     this.kpi_average=0
       #     if this.evaluation_type :
       #         if this.evaluation_type=='quarterly' and len(this.employee_kpi) > 0:
       #             res=this.env['employee_kpi_data'].search([('eva_type','=',this.id)], order='id desc', limit=1)
       #             this.kpi_average=res.kpi
       #         elif this.evaluation_type=='monthly' and len(this.employee_kpi) > 0:
       #             if len(this.employee_kpi) ==1:
       #                 val=this.env['employee_kpi_data'].search([('eva_type','=',this.id)], order='id desc', limit=1)
       #                 for line in val:
       #                     res=res+line.kpi
       #                 this.kpi_average=res
       #             elif len(this.employee_kpi) ==2:
       #                 val=this.env['employee_kpi_data'].search([('eva_type','=',this.id)], order='id desc', limit=2)
       #                 for line in val:
       #                     res=res+line.kpi
       #                 this.kpi_average=res/2
       #             elif len(this.employee_kpi) >=3:
       #                 val=this.env['employee_kpi_data'].search([('eva_type','=',this.id)], order='id desc', limit=3)
       #                 for line in val:
       #                     res=res+line.kpi
       #                 this.kpi_average=res/3
       #             else:
      #                  this.kpi_average=0
     #       else:
    #            this.kpi_average=0
    quartile_average=fields.Many2one('kpi_category',compute="pick_quartile_average")
    @api.onchange('kpi_average')
    def pick_quartile_average(self):
        for this in self:
            quartiles=self.env['kpi_category'].search([('kpi_from','<=',this.kpi_average),('kpi_to','>=',this.kpi_average)])
            this.quartile_average = quartiles.id

class employee_kpi_data(models.Model):
    _name="employee_kpi_data"
    eva_type=fields.Many2one('hr.employee','evaluation_type')
    @api.depends('eva_type.evaluation_type')
    def _compute_periods(self):
        for this in self :
            if self.eva_type.evaluation_type=='quarterly':
                this.eva_type_state=True
            
            elif self.eva_type.evaluation_type=='monthly':
                this.eva_type_state=False
    period_month=fields.Selection([('1','January'),('2','February'),('3','March'),('4','April'),('5','May '),('6','June'),('7','July'),('8','August'),('9','September'),('10','October'),('11','November'),('12','December')],string="Period")
    period_quarter=fields.Selection([('q1','Q1'),('q2','Q2'),('q3','Q3'),('q4','Q4')],string="Period")
    @api.model
    def year_selection(self):
            year = 2000 
            year_list = []
            while year != 2100: 
                  year_list.append((str(year), str(year)))
                  year += 1
            return year_list
    year=fields.Selection(
    year_selection,required=True,
    string="Year",
    default="2021", 
 )
    kpi=fields.Integer(string="KPI")
    quartile=fields.Many2one('kpi_category',compute="pick_quartile")
    note=fields.Text(string="Note")
    @api.constrains('kpi')
    def _check_kpi_value(self):
        if self.kpi > 100 or self.kpi < 1:
           raise ValidationError('Enter Value For KPI Between 1-100.')
    @api.onchange('kpi')
    def pick_quartile(self):
        for this in self:
            quartiles=self.env['kpi_category'].search([('kpi_from','<=',this.kpi),('kpi_to','>=',this.kpi)])
            this.quartile = quartiles.id
    @api.model
    def create(self, values):
        if values['period_month'] != False:
            old_line = self.env['employee_kpi_data'].search([('period_month','=',values['period_month']),('year','=',values['year']),('eva_type','=',values['eva_type'])])
            if len(old_line) >= 1:
                raise ValidationError('Duplicate in KPI periods are not allowed !.')
        elif values['period_quarter'] != False:
            old_line = self.env['employee_kpi_data'].search([('period_quarter','=',values['period_quarter']),('year','=',values['year']),('eva_type','=',values['eva_type'])])
            if len(old_line)>=1:
                raise ValidationError('Duplicate in KPI periods are not allowed !.')
        res = super(employee_kpi_data, self).create(values)
        return res
    # def write(self, vals):
    #     res = super(employee_kpi_data, self).write(vals)
    #     if self.period_month != False:
    #         old_line = self.env['employee_kpi_data'].search([('period_month','=',self.period_month),('year','=',self.year),('eva_type','=',self.eva_type.id)])
    #         if len(old_line) > 1:
    #             raise ValidationError('Duplicate in KPI periods are not allowed !.')
    #     elif self.period_quarter != False:
    #         old_line = self.env['employee_kpi_data'].search([('period_quarter','=',self.period_quarter),('year','=',self.year),('eva_type','=',self.eva_type)])
    #         if len(old_line)>1:
    #             raise ValidationError('Duplicate in KPI periods are not allowed !.') 
    #     return res

class RecruitmentStage(models.Model):
    _inherit = "hr.recruitment.stage"
    is_initial=fields.Boolean(string="TA Initial",default=False)
    is_final=fields.Boolean(string="Final Stage",default=False)

    is_o_initial=fields.Boolean(string="Operational Initial",default=False)
    is_o_final=fields.Boolean(string="Operational Final",default=False)

class hr_recruitment_botoom_refuse(models.Model):
    _inherit='hr.applicant'
    is_o_initial=fields.Boolean(string="Operational Initial",default=False,compute="check_o_initial_stage_state")
    is_o_final=fields.Boolean(string="Operational Final",default=False,compute="check_o_fianl_stage_state")

    def check_o_initial_stage_state(self):
        if self.stage_id.is_o_initial:
            self.is_o_initial=True
        else:
            self.is_o_initial=False
    def check_o_fianl_stage_state(self):
        if self.stage_id.is_o_final:
            self.is_o_final=True
        else:
            self.is_o_final=False

    @api.onchange('stage_id')
    def check_o_stage_state(self):
        if self.stage_id.is_o_initial:
            self.is_o_initial=True
        elif self.stage_id.is_o_final:
            self.is_o_final=True
        else:
            self.is_o_initial=False
            self.is_o_final=False

    applicant_quartile_type=fields.Selection([('top','TOP Quartile'),('median','Median Quartile'),('bottom','Bottom Quartile')],compute='pick_applicant_quartile_type',store=True)
    @api.onchange('emp_id')
    def pick_applicant_quartile_type(self):
        for this in self:
            this.applicant_quartile_type = this.emp_id.quartile_average.quartile_type

    @api.onchange('stage_id')
    def _check_top_quartile(self):
        for this in self:
            if this.emp_id.id != False and this.applicant_quartile_type!=False:
                if this.stage_id.is_final:
                    top_line = this.env['hr.applicant'].search([('is_final','!=',True),('job_id.id','=',this.job_id.id),('active','=',True),('job_category','=','talent')])
                    num_of_top = 0
                    for line in top_line:
                        if line.applicant_quartile_type =='top':
                            if line.is_final==False:
                                num_of_top += 1
                        if num_of_top>0 and this.applicant_quartile_type =='median':
                            raise ValidationError('You still have application/s from Top Quartile employees, you must process them first before Median Quartile')

    @api.model
    def create(self, vals):
        res = super(hr_recruitment_botoom_refuse, self).create(vals)
        if self.emp_id != False:
            old_line = self.env['hr.applicant'].search([('applicant_quartile_type','=','bottom'),('id','=',res.id)])
            if len(old_line)>=1:
                raise ValidationError('You are not allowed to apply to this job (Low KPI).')
            else:
                return res
        else:
            return res
