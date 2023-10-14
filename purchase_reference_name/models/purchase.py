from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _prepare_picking(self):
        result = super(PurchaseOrder, self)._prepare_picking()
        result["origin"] = self.partner_ref or self.name
        return result
