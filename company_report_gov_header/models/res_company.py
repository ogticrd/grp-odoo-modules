from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    l10n_do_gov_header_center_data = fields.Html("Header center data")
    l10n_do_gov_header_center_image = fields.Binary("Header Center Image")
    l10n_do_gov_header_right_image = fields.Binary("Header Right Image")


class BaseDocumentLayout(models.TransientModel):
    _inherit = 'base.document.layout'

    l10n_do_gov_header_center_data = fields.Html(related='company_id.l10n_do_gov_header_center_data', readonly=False)
    l10n_do_gov_header_center_image = fields.Binary(related='company_id.l10n_do_gov_header_center_image', readonly=False)
    l10n_do_gov_header_right_image = fields.Binary(related='company_id.l10n_do_gov_header_right_image', readonly=False)
