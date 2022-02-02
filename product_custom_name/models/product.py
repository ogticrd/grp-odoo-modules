from odoo.osv import expression
from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = "product.product"
    _order = "default_code, name, custom_name, id"

    custom_name = fields.Char(index=True)
    display_custom_name = fields.Char(
        compute="_compute_display_custom_name", store=True, index=True
    )

    @api.depends("name", "custom_name")
    def _compute_display_custom_name(self):
        for product in self:
            product.display_custom_name = (
                product.name if not product.custom_name else product.custom_name
            )

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

    def name_get(self):

        def _name_get(d):
            name = d.get("name", "")
            code = (
                self._context.get("display_default_code", True)
                and d.get("default_code", False)
                or False
            )
            if code:
                name = "[%s] %s" % (code, name)
            return (d["id"], name)

        self.check_access_rights("read")
        self.check_access_rule("read")

        result = []
        products_wo_custom_name = self.filtered(lambda p: not p.custom_name)
        result.extend(super(ProductProduct, products_wo_custom_name).name_get())

        self.sudo().read(["display_custom_name", "default_code"], load=False)

        for product in (self - products_wo_custom_name).sudo():
            variant = (
                product.product_template_attribute_value_ids._get_combination_name()
            )

            name = (
                variant
                and "%s (%s)" % (product.display_custom_name, variant)
                or product.display_custom_name
            )
            sellers = (
                self.env["product.supplierinfo"]
                .sudo()
                .browse(self.env.context.get("seller_id"))
                or []
            )
            if sellers:
                for s in sellers:
                    seller_variant = (
                        s.product_name
                        and (
                            variant
                            and "%s (%s)" % (s.product_name, variant)
                            or s.product_name
                        )
                        or False
                    )
                    mydict = {
                        "id": product.id,
                        "name": seller_variant or name,
                        "default_code": s.product_code or product.default_code,
                    }
                    temp = _name_get(mydict)
                    if temp not in result:
                        result.append(temp)
            else:
                mydict = {
                    "id": product.id,
                    "name": name,
                    "default_code": product.default_code,
                }
                result.append(_name_get(mydict))
        return result

    @api.model_create_multi
    def create(self, vals_list):

        # set default custom name
        for vals in vals_list:
            vals["custom_name"] = vals["name"]

        return super(ProductProduct, self).create(vals_list)
