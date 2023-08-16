from odoo import models, fields


class Purchase(models.Model):
    _inherit = ["purchase.order", "l10n_do.gov.sign"]

    public_access_id = fields.Char()
    l10n_do_gov_signing_request_ids = fields.One2many(
        "l10n_do_gov.document.signing.request",
        "purchase_id",
        "Signing/Approval Requests",
    )
