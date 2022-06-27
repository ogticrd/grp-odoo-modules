from odoo import models, fields


class Job(models.Model):
    _inherit = "hr.job"

    l10n_do_gov_expense_product_ids = fields.Many2many(
        "product.product",
        string="Expense products",
        domain=[("can_be_expensed", "=", True)],
        help="Allowed expense products for this job position",
    )
