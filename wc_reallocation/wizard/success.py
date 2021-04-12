from odoo import fields, models, api, _
from odoo.tools import float_compare
from odoo.exceptions import UserError

class MessageWizard(models.TransientModel):
    _name = 'message.wizard'

    message = fields.Text('Message', default="You must Terminate the Employee on Connect Zone and Confirm")

    terminated = fields.Boolean('Terminated on Connect Zone')
    def action_ok(self):
        """ close wizard"""

        # if not self.terminated:
        #     mess= {
        #             'title': _('WARNING!'),
        #             'message' : "You must terminate the Employee on Connect Zone and Confirm."
        #         }
        #     return None
        #     # return {'warning': mess}
        reallocation = self.env['hr.applicant'].browse(self.env.context.get('active_id'))
        reallocation.terminated = self.terminated
        if self.terminated == True:
            # reallocation.state = "terminate"
            pass
        else:
            return {
                'name': _('Terminate'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'message.wizard',
                # # pass the id
                # 'res_id': message_id.id,
                'target': 'new'
            }
        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'reload',
        # }
        return {'type': 'ir.actions.act_window_close'}
