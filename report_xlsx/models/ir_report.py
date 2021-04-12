# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ReportAction(models.Model):
    _inherit = "ir.actions.report"
    report_type = fields.Selection([
        ('qweb-html', 'HTML'),
        ('qweb-pdf', 'PDF'),
        ('qweb-text', 'Text'),
        ("xlsx", "XLSX"),
    ], required=True, default='qweb-pdf',
    help='The type of the report that will be rendered, each one having its own'
        ' rendering method. HTML means the report will be opened directly in your'
        ' browser PDF means the report will be rendered using Wkhtmltopdf and'
        ' downloaded by the user.')

    # report_type = fields.Selection(selection_add=[],ondelete="cascade")

    @api.model
    def render_xlsx(self, docids, data):
        report_model_name = "report.%s" % self.report_name
        report_model = self.env.get(report_model_name)
        if report_model is None:
            raise UserError(_("%s model was not found") % report_model_name)
        return report_model.with_context(
            active_model=self.model
        ).create_xlsx_report(  # noqa
            docids, data
        )

    @api.model
    def _get_report_from_name(self, report_name):
        res = super(ReportAction, self)._get_report_from_name(report_name)
        if res:
            return res
        report_obj = self.env["ir.actions.report"]
        qwebtypes = ["xlsx"]
        conditions = [
            ("report_type", "in", qwebtypes),
            ("report_name", "=", report_name),
        ]
        context = self.env["res.users"].context_get()
        return report_obj.with_context(context).search(conditions, limit=1)
