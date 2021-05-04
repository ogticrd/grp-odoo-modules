from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    l10n_do_gov_header_center_data = fields.Text("Header center data")
    l10n_do_gov_header_center_image = fields.Binary("Header Center Image")
    l10n_do_gov_header_right_image = fields.Binary("Header Right Image")
