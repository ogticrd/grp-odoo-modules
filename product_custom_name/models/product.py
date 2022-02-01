from odoo.osv import expression
from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = "product.product"
    _order = "default_code, name, custom_name, id"

    custom_name = fields.Char(index=True)

    @api.model
    def _name_search(
        self, name="", args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        res = super(ProductProduct, self)._name_search(
            name=name,
            args=args,
            operator=operator,
            limit=limit,
            name_get_uid=name_get_uid,
        )
        if not len(res):
            return self._search(
                expression.AND([[("custom_name", operator, name)], args]),
                limit=limit,
                access_rights_uid=name_get_uid,
            )
        return res
