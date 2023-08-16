from odoo import models, fields


class Users(models.Model):
    _inherit = "res.users"

    l10n_do_gov_sign_username = fields.Char("Username")
    l10n_do_gov_sign_password = fields.Char("Password")
