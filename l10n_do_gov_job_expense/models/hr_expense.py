from odoo import models, fields, api


class Expense(models.Model):
    _inherit = "hr.expense"

    job_id = fields.Many2one("hr.job", related="employee_id.job_id")
    product_id = fields.Many2one(
        domain=[]
        # domain=lambda self: [
        #     ("id", "in", self.job_id.l10n_do_gov_expense_product_ids.ids)]
    )

    @api.onchange("employee_id")
    def _onchange_employee_id(self):
        expense_product_ids = []
        if self.employee_id:
            expense_product_ids = self.job_id.l10n_do_gov_expense_product_ids.ids
        return {
            "domain": {
                "product_id": [
                    ("id", "in", expense_product_ids)
                ]
            }
        }
