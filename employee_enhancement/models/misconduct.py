# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Misconduct(models.Model):
    _name = 'employee.misconduct'
    _description = 'employee.misconduct'

    name = fields.Char('Type', required=True)
    applying_restriction = fields.Integer('Applying Restriction')
    description = fields.Text('Notes')

    @api.model
    def create(self, values):
        res = super(Misconduct, self).create(values)
        misconduct_ids = []
        first_create = False
        try:
            misconduct_ids.append(self.env.ref('employee_enhancement.employee_misconduct_pay_attention').id)
            misconduct_ids.append(self.env.ref('employee_enhancement.employee_misconduct_warning').id)
            misconduct_ids.append(self.env.ref('employee_enhancement.employee_misconduct_Fine').id)
        except Exception as e:
            first_create = True
        if first_create:
            pass
        else:
            if res.id not in misconduct_ids:
                raise ValidationError(_('You can not add new misconduct, Please contact your system administrator'))
        return res
    def write(self, values):
        res = super(Misconduct, self).write(values)
        raise ValidationError(_('You can not modify this misconduct, Please contact your system administrator'))
        return res
    def unlink(self):
        res = super(Misconduct, self).unlink()
        raise ValidationError(_('You can not delete this misconduct, Please contact your system administrator'))
        return res
    def toggle_active(self):
        res=super(Misconduct, self).toggle_active()
        raise ValidationError(_('You can not change active state this misconduct, Please contact your system administrator'))
        return res

    @api.constrains('applying_restriction')
    def _check_applying_restriction_value(self):
        if self.applying_restriction > 1000 or self.applying_restriction <= 0:
            raise ValidationError(_('Enter Applying Restriction greater than 0.'))


class MisconductLine(models.Model):
    _name = 'employee.misconduct.line'
    _description = 'employee.misconduct.line'

    _order = "date desc"

    emp_id = fields.Many2one('hr.employee')

    date = fields.Date(required=True)
    misconduct_type_id = fields.Many2one('employee.misconduct', string=" Misconduct Type", required=True)
    description = fields.Text('Notes')
