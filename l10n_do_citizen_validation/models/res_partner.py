import os
import time
import json
import logging
import tempfile
import requests
from odoo import models, api

from json.decoder import JSONDecodeError

_logger = logging.getLogger(__name__)

# 60 minutes in seconds
MAX_AGE = 60 * 60
TOKEN_PATH = os.path.join(
    tempfile.gettempdir(),
    "oauth.token",
)


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _get_param(self, key):
        return self.env["ir.config_parameter"].sudo().get_param(key, False)

    @api.model
    def get_bearer_token(self):
        token = ""

        # Tries to get Oath2 token from temporary file
        if os.path.isfile(TOKEN_PATH):
            token_age = time.time() - os.path.getmtime(TOKEN_PATH)
            if token_age < MAX_AGE:
                with open(TOKEN_PATH, "r") as infile:
                    token = infile.read()

        if not token:

            # Gets service URL
            url = self._get_param("citizen.oauth.url")
            if not url:
                _logger.error("No Oath2 URL found for Citizen data fetching")
                return False

            # Builds request headers
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": "Basic MDRmMTE2NTAtYTllNS00ZmIwLWIxMTY"
                "tNTBhOWU1MmZiMGFiOkhxS1ZhRVE4SEMzcFZQ"
                "NTIxOFc1WENoNUhDR3ZrSnZ4cHZLeGI0SWJLVTg=",
            }
            resp = requests.post(
                url, headers=headers, data="grant_type=client_credentials"
            )
            try:
                token = json.loads(resp.text)["access_token"]
                with open(TOKEN_PATH, "w") as outfile:
                    outfile.write(token)
            except (JSONDecodeError, KeyError):
                return False

        return "Bearer %s" % token

    @api.model
    def get_citizen_vals(self, citizen_id):

        citizen_vals = {}

        # Gets access token
        access_token = self._get_param("citizen.api.token")
        if not access_token:
            _logger.error("No access token found for Citizens data fetching")
            return citizen_vals

        # Gets API URL
        url = self._get_param("citizen.api.url")
        if not url:
            _logger.error("No API URL found for Citizen data fetching")
            return citizen_vals
        url += "/%s/info/basic" % citizen_id

        # Gets Oauth2 token
        bearer_token = self.get_bearer_token()
        if not bearer_token:
            return citizen_vals

        # Builds request headers
        headers = {"Authorization": bearer_token, "x-access-token": access_token}

        _logger.info("Fetching Citizens data for %s" % citizen_id)
        response = requests.get(url, headers=headers)

        try:
            response_vals = json.loads(response.text)
        except JSONDecodeError:
            return citizen_vals

        if not response_vals.get("valid"):
            return citizen_vals

        return {
            "name": " ".join(
                response_vals["payload"][f]
                for f in ["names", "firstSurname", "secondSurname"]
            ),
            "vat": citizen_id,
            "company_type": "person",
        }

    @api.model
    def _get_sanitized_citizen_id(self, citizen_id):
        digits = filter(str.isdigit, citizen_id)
        return "".join(digits)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:

            # only fetch citizen data if partner vat is a Cédula
            vat = vals["name"] if vals["name"].isdigit() else vals.get("vat", False)
            if vat and len(vat) >= 11:
                citizen_vals = self.get_citizen_vals(
                    self._get_sanitized_citizen_id(vat)
                )
                vals.update(citizen_vals)

        return super(ResPartner, self).create(vals_list)
