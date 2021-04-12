# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError
from datetime import date

class wc_raya_qoh_qh_status(models.Model):
    _name = 'wc_raya_qoh.hc_status'
    _description = 'wc_raya_qoh.HC status'

    name = fields.Char()
    is_certified=fields.Boolean()
    is_join=fields.Boolean()
    is_rejoin=fields.Boolean()
    is_transfer=fields.Boolean()
    is_trainee=fields.Boolean()

    @api.onchange('is_certified')
    def constrain_is_certified_onnly(self):
        if self.is_certified:
            self.is_join=False
            self.is_rejoin=False
            self.is_transfer=False
            self.is_trainee=False

    @api.onchange('is_join')
    def constrain_is_join_onnly(self):
        if self.is_join:
            self.is_certified=False
            self.is_rejoin=False
            self.is_transfer=False
            self.is_trainee=False

    @api.onchange('is_rejoin')
    def constrain_is_rejoin_onnly(self):
        if self.is_rejoin:
            self.is_certified=False
            self.is_join=False
            self.is_transfer=False
            self.is_trainee=False

    @api.onchange('is_transfer')
    def constrain_is_transfer_onnly(self):
        if self.is_transfer:
            self.is_certified=False
            self.is_join=False
            self.is_rejoin=False
            self.is_trainee=False

    @api.onchange('is_trainee')
    def constrain_is_trainee_onnly(self):
        if self.is_trainee:
            self.is_certified=False
            self.is_join=False
            self.is_transfer=False
            self.is_rejoin=False

    @api.constrains('is_certified')
    def constrain_is_certified(self):
        lines=self.env['wc_raya_qoh.hc_status'].search([('is_certified','=',True)])
        if len(lines)>1 :
            raise UserError(_('You can only pick one Certified status !'))

    @api.constrains('is_join')
    def constrain_is_join(self):
        lines=self.env['wc_raya_qoh.hc_status'].search([('is_join','=',True)])
        if len(lines)>1 :
            raise UserError(_('You can only pick one Join status !'))

    @api.constrains('is_rejoin')
    def constrain_is_rejoin(self):
        lines=self.env['wc_raya_qoh.hc_status'].search([('is_rejoin','=',True)])
        if len(lines)>1 :
            raise UserError(_('You can only pick one Re-Join status !'))

    @api.constrains('is_transfer')
    def constrain_is_transfer(self):
        lines=self.env['wc_raya_qoh.hc_status'].search([('is_transfer','=',True)])
        if len(lines)>1 :
            raise UserError(_('You can only pick one Transfer status !'))

    @api.constrains('is_trainee')
    def constrain_is_trainee(self):
        lines=self.env['wc_raya_qoh.hc_status'].search([('is_trainee','=',True)])
        if len(lines)>1 :
            raise UserError(_('You can only pick one Trainee status !'))

class hrApplicant(models.Model):
    _inherit = "hr.applicant"

    hc_status=fields.Many2one('wc_raya_qoh.hc_status',string="HC status")
    hc_date=fields.Date("HC Date")
    app_qoh=fields.Selection([('1','Yes'),('0','No')],string="QOH",compute="compute_qoh")
    qoh=fields.Selection([('1','Yes'),('0','No')],string="QOH")
    # @api.onchange('app_qoh')
    # def compute_qohdata(self):
    #     for this in self:
    #         this.qoh=this.app_qoh
    def compute_qoh(self):
        for this in self:
            if this.tarinee_status=='active' and (this.hc_status.is_certified or this.hc_status.is_join or this.hc_status.is_rejoin or this.hc_status.is_transfer):
                this.app_qoh='1'
                this.qoh='1'
            elif this.tarinee_status=='dropped':
                this.app_qoh='0'
                this.qoh='0'
            elif this.quality_of_hiring_date !=False:
                if this.tarinee_status=='active' and this.hc_status.is_trainee and this.quality_of_hiring_date <= date.today():
                    this.app_qoh='0'
                    this.qoh='0'
                elif this.tarinee_status=='active' and this.hc_status.is_trainee and this.quality_of_hiring_date > date.today():
                    this.app_qoh='1'
                    this.qoh='1'
                else:
                    this.app_qoh=False
                    this.qoh=False
            else:
                this.app_qoh=False
                this.qoh=False


