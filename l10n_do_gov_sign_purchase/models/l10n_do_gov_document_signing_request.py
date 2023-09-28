from odoo import models, fields


class SignRequest(models.Model):
    _inherit = "l10n_do_gov.document.signing.request"

    purchase_id = fields.Many2one("purchase.order", "Purchase")
