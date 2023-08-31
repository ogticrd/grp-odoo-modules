import json
import requests
from requests.auth import HTTPBasicAuth

from odoo import models, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError


class GovSign(models.AbstractModel):
    """
    This model is meant to be inherited in each model
    is required to sign documents
    """

    _name = "l10n_do.gov.sign"
    _description = "Dominican Gov Sign"

    def _make_request(self, service, data, method="get"):
        params = (
            self.env["ir.config_parameter"].sudo().get_param("l10n_do.firmas.gob.url")
        )
        try:
            params = safe_eval(params)
            url = params["url"]
            user = params["user"]
            password = params["password"]
        except (ValueError, SyntaxError, KeyError):
            raise ValidationError(_("Could not parse a valid dict params for request."))

        basic = HTTPBasicAuth(user, password)
        if not url:
            raise ValidationError(_("Firmas Gob base URL param not found."))

        if not url.endswith("/"):
            url += "/"
        url += service
        result = getattr(requests, method)(
            url,
            headers={"Content-Type": "application/json"},
            auth=basic,
            data=json.dumps(data),
        )

        if result.status_code == 500:
            error_vals = safe_eval(result.text)
            raise ValidationError(
                "El servicio de firmado a retornado el siguiente error:\n\n%s"
                % error_vals["errorMessage"]
            )

        return result

    def create_signing_request(self, documents, addressee, values=None):
        if values is None:
            values = {}

        values.update(
            {
                "sender": {
                    "userCode": self.env.user.l10n_do_gov_sign_username,
                    "entityCode": "default",
                },
                "addresseeLines": [
                    {
                        "addresseeGroups": [
                            {
                                "isOrGroup": False,
                                "userEntities": [
                                    {
                                        "userCode": addr.user_id.l10n_do_gov_sign_username,
                                        "entityCode": "default",
                                        "action": addr.action,
                                    }
                                ],
                            }
                            for addr in addressee
                        ]
                    }
                ],
                "verificationAccess": {
                    "type": "USERPASSWORD",
                    "username": self.env.user.l10n_do_gov_sign_username,
                    "password": self.env.user.l10n_do_gov_sign_password,
                },
                "senderNotificationLevel": "ALL",
                "signatureLevel": "CERTIFICATE_ONLY",
                "useDefaultStamp": True,
                "documentsToSign": [
                    {"filename": doc.display_name, "data": doc.datas.decode("ascii")}
                    for doc in documents
                ],
            }
        )

        response = self._make_request("requests", values, "post")
        return response.json()

    def get_request_data(self, public_access_id):
        url = "requests/%s" % public_access_id
        response = self._make_request(url, {}, "get")
        return response.json()

    def finalize_signing_request(self, public_access_id):
        url = "requests/end/%s" % public_access_id
        self._make_request(url, {}, "get")

    def get_signed_document(self, public_access_id):
        url = "documents/%s/signed" % public_access_id
        response = self._make_request(url, {}, "get")
        return response.json()
