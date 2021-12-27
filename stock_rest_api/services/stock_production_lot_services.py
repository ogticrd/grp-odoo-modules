from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_datamodel.restapi import Datamodel
from odoo.addons.component.core import Component
from odoo.exceptions import UserError
from odoo import _


class StockProductionLotService(Component):
    _inherit = "base.rest.service"
    _name = "stock.production.lot.service"
    _usage = "stock_production_lot"
    _collection = "stock.rest.api.private.services"
    _description = """
        Stock Production Lot Services
        Access to the stock production lot services is only allowed to authenticated
        users. If you are not authenticated please go to <a href='/web/login'>Login</a>
    """

    @restapi.method(
        [(["/<int:id>/get", "/<int:id>"], "GET")],
    )
    def get(self, _id):
        """
        Get lot information
        """
        res = self._get(_id)
        return self._to_json(res)

    @restapi.method(
        [(["/<int:id>/product_lots"], "GET")],
    )
    def get_product_lots(self, _id):
        """
        Get lots by product
        """
        lot_ids = self._get_model().search([("product_id", "=", _id)])
        return self._to_json(lot_ids)

    @restapi.method(
        [(["/search"], "GET")],
        input_param=Datamodel("stock.search.param"),
    )
    def search(self, domain):
        """
        Search lots by domain

        ex:

        "domain": "[("name", "=", "0000000010001")]"

        """
        domain = eval(domain.domain.replace("%20", " "))
        lot_ids = self._get_model().search(domain)
        return {
            "count": len(lot_ids),
            "rows": self._to_json(lot_ids),
        }

    def _get(self, _id):
        return self._get_model().browse(_id)

    def _get_model(self):
        return self.env["stock.production.lot"]

    def _to_json(self, lot_id):
        return lot_id.read()

    def _prepare_create_vals(self, create_vals):
        fields2match = self._get_fields2match()

        def _get_recordfstring(field, string):
            result = self.env[fields2match[field]]._name_search(string)
            if not result:
                raise UserError(
                    _(
                        f"Couldn't find record for field {field}: {string} \n"
                        f"Try using literal id or changing the string for the name search."
                    )
                )
            return result and result[0][0] or False

        for create_key, create_value in create_vals.items():
            if create_key not in fields2match or isinstance(create_value, int):
                continue
            elif isinstance(create_value, str):
                create_vals[create_key] = _get_recordfstring(create_key, create_value)
            elif isinstance(create_value, list):
                create_list = []
                if all(isinstance(value, str) for value in create_value):
                    create_list = [
                        (4, _get_recordfstring(create_key, value))
                        for value in create_value
                    ]
                elif all(isinstance(value, int) for value in create_value):
                    create_list = [(4, value) for value in create_value]
                elif all(isinstance(value, dict) for value in create_value):
                    for value in create_value:
                        for k, v in value.items():
                            if k not in fields2match or isinstance(v, int):
                                continue
                            elif isinstance(v, str):
                                value[k] = _get_recordfstring(k, v)
                            elif isinstance(v, list):
                                dict_create_list = []
                                if all(isinstance(value, str) for value in v):
                                    dict_create_list = [
                                        (4, _get_recordfstring(k, value)) for value in v
                                    ]
                                elif all(isinstance(value, int) for value in v):
                                    dict_create_list = [(4, value) for value in v]
                                value[k] = dict_create_list
                    create_list = [(0, 0, value) for value in create_value]
                create_vals[create_key] = create_list
        return create_vals

    def _get_fields2match(self):
        return {
            "product_id": "product.product",
            "product_uom_id": "uom.uom",
            "location_id": "stock.location",
            "quant_ids": "stock.quant",
        }
