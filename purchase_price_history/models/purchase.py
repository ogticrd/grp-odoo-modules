from odoo import models, fields


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def button_approve(self, force=False):
        # first call super() so price historic is not created if any exception is raised
        result = super(PurchaseOrder, self).button_approve(force=force)

        is_company_currency = self.currency_id == self.company_id.currency_id

        for purchase in self:
            price_history_values = []
            for line in purchase.order_line:
                company_po_price_unit = (
                    line.price_unit
                    if is_company_currency
                    else purchase.currency_id._convert(
                        line.price_unit,
                        purchase.company_id.currency_id,
                        purchase.company_id,
                        purchase.date_approve,
                    )
                )

                if line.product_uom != line.product_id.uom_id:
                    company_prd_price_unit = line.product_id.uom_id._compute_quantity(
                        company_po_price_unit, line.product_uom
                    )
                    currency_prd_price_unit = line.product_id.uom_id._compute_quantity(
                        line.price_unit, line.product_uom
                    )
                else:
                    company_prd_price_unit = company_po_price_unit
                    currency_prd_price_unit = line.price_unit

                price_history_values.append(
                    {
                        "date": fields.Date.today(),
                        "product_id": line.product_id.id,
                        "po_uom_id": line.product_uom.id,
                        "company_po_price_unit": company_po_price_unit,
                        "company_prd_price_unit": company_prd_price_unit,
                        "currency_po_price_unit": line.price_unit,
                        "currency_prd_price_unit": currency_prd_price_unit,
                        "purchase_id": purchase.id,
                        "partner_id": purchase.partner_id.id,
                        "state": "purchase",
                        "company_currency_id": purchase.company_id.currency_id.id,
                        "purchase_currency_id": purchase.currency_id.id,
                        "company_id": purchase.company_id.id,
                    }
                )

            self.env["product.price.history"].sudo().create(price_history_values)

        return result

    def button_cancel(self):

        super(PurchaseOrder, self).button_cancel()
        for purchase in self:
            historical = self.env["product.price.history"].search(
                [("purchase_id", "=", purchase.id)]
            )
            historical.write({"state": "cancel"})
