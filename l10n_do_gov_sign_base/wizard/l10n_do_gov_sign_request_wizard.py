from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SignRequestWizardAddressee(models.TransientModel):
    _name = "l10n_do.gov.sign.request.addressee"
    _description = "Dominican Gov Sign Request Addressee"

    user_id = fields.Many2one("res.users", "Addressee", required=True)
    request_id = fields.Many2one(
        "l10n_do.gov.sign.request.wizard", "Request", required=True
    )
    action = fields.Selection(
        [("SIGN", "Sign"), ("APPROVAL", "Approval")], required=True
    )


class SignRequestWizard(models.TransientModel):
    _name = "l10n_do.gov.sign.request.wizard"
    _inherit = "mail.compose.message"  # reuse mail template features to generate attachments
    _description = "Dominican Gov Sign Request Wizard"

    expiration_date = fields.Datetime("Request Expiration Date")
    subject = fields.Char()
    message = fields.Text()
    reference = fields.Char()
    addressee_ids = fields.One2many(
        "l10n_do.gov.sign.request.addressee", "request_id", "Addressees"
    )

    def send_signing_request(self):
        record_id = self.env[self.model].browse(self.res_id)
        values = {
            "subject": self.subject,
            "message": self.message,
            "reference": self.reference,
        }
        if self.expiration_date:
            values["expirationDate"] = round(self.expiration_date.timestamp() * 1000)

        result = self.env["l10n_do.gov.sign"].create_signing_request(
            documents=self.attachment_ids,
            users=self.addressee_ids,
            values=values,
        )
