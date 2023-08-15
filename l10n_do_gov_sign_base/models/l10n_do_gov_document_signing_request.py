from odoo import models, fields


class SignRequest(models.Model):
    _name = "l10n_do_gov.document.signing.request"
    _description = "Document Signing Request"

    user_id = fields.Many2one("res.users", "User", required=True)
    action = fields.Selection(
        [("sign", "Sign"), ("approval", "Approval")], required=True
    )
    action_date = fields.Datetime(required=True)
    status = fields.Selection(
        [
            ("new", "New"),
            ("read", "Read"),
            ("signed", "Signed"),
            ("approval", "Approval"),
            ("reject", "Rejected"),
            ("no_action", "No action"),
        ],
        default="new",
        required=True,
    )
    comment = fields.Char()
