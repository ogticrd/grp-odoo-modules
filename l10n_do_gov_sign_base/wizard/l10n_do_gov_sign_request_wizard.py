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
        [("SIGN", "Sign"), ("APPROVAL", "Approve")], required=True
    )


class SignRequestWizard(models.TransientModel):
    _name = "l10n_do.gov.sign.request.wizard"
    _inherits = {"mail.compose.message": "composer_id"}
    _description = "Dominican Gov Sign Request Wizard"

    composer_id = fields.Many2one(
        "mail.compose.message", string="Composer", required=True, ondelete="cascade"
    )
    expiration_date = fields.Datetime("Expiration Date")
    subject = fields.Char()
    message = fields.Text()
    reference = fields.Char()
    addressee_ids = fields.One2many(
        "l10n_do.gov.sign.request.addressee", "request_id", "Addressees"
    )

    @api.onchange("template_id")
    def onchange_template_id(self):
        self.composer_id.template_id = self.template_id.id
        self.composer_id._onchange_template_id_wrapper()

    @api.model
    def default_get(self, fields_list):
        result = super(SignRequestWizard, self).default_get(fields_list)
        context = self._context
        result["model"] = context.get("active_model")
        result["res_id"] = context.get("active_id")
        record_id = self.env[result["model"]].browse(result["res_id"])
        result["subject"] = _("Approval Request for %s") % record_id.name
        result["reference"] = record_id.name

        return result

    def _get_addressee_user(self, user_code):
        return self.env["res.users"].search(
            [("l10n_do_gov_sign_username", "=", user_code)], limit=1
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
            addressee=self.addressee_ids,
            values=values,
        )

        if isinstance(result, dict):
            raise ValidationError(result.get("errorMessage", "Error en envío de request"))

        document_public_access_id = False
        if "documentsToSign" in result:
            for document in result["documentsToSign"]:
                document_public_access_id = document["publicAccessId"]
                break

        record_id.write(
            {
                "l10n_do_gov_signing_request_ids": [
                    (
                        0,
                        0,
                        {
                            "user_id": self._get_addressee_user(usr["userEntities"][0]["userCode"]).id,
                            "action": usr["userEntities"][0]["action"],
                            "status": usr["userEntities"][0]["status"],
                        },
                    )
                    for usr in result["addresseeLines"][0]["addresseeGroups"]
                ],
                "request_public_access_id": result["publicAccessId"],
                "document_public_access_id": document_public_access_id,
            }
        )
