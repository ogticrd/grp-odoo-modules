from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_datamodel.restapi import Datamodel
from odoo.addons.component.core import Component
from odoo.exceptions import UserError
from odoo import osv, _


class StockPickingService(Component):
    _inherit = "base.rest.service"
    _name = "stock.picking.service"
    _usage = "stock_picking"
    _collection = "stock.rest.api.private.services"
    _description = """
        Stock Picking Services
        Access to the stock picking services is only allowed to authenticated users.
        If you are not authenticated please go to <a href='/web/login'>Login</a>
    """

    @restapi.method(
        [(["/<int:id>/get", "/<int:id>"], "GET")],
    )
    def get(self, _id):
        """
        Get stock picking information
        """
        res = self._get(_id)
        return self._to_json(res)

    @restapi.method(
        [(["/<int:id>/operations"], "GET")],
    )
    def operations(self, _id):
        """
        Get stock picking operations information
        """
        res = self._get(_id)
        return self._to_json(res.move_ids_without_package)

    def _get(self, _id):
        return self._get_model().browse(_id)

    @restapi.method(
        [(["/search"], "GET")],
        input_param=Datamodel("stock.search.param"),
    )
    def search(self, domain):
        """
        Search stock picking by domain

        ex:

        "domain": "[("picking_type_code", "=", "incoming")]"

        """
        domain = eval(domain.domain.replace("%20", " "))
        stock_picking_ids = self._get_model().search(domain)
        return {
            "count": len(stock_picking_ids),
            "rows": self._to_json(stock_picking_ids),
        }

    @restapi.method(
        [(["/create"], "POST")],
        input_param=Datamodel("stock.create.param"),
    )
    def create(self, values):
        """
        Create a new stock picking

        ex:

        "values": {
            "origin": "SO00010",
            "note": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "partner_id": "Jose Lopez",
            "move_type": "direct",
            "date": "2021-06-08",
            "location_id": "Shelf 1",
            "location_dest_id": "Shelf 2",
            "move_ids_without_package": [
                {
                    "name": "Three-Seat Sofa",
                    "product_id": "Three-Seat Sofa",
                    "product_uom_qty": 10,
                    "product_uom": "Unit(s)"
                },
                {
                    "name": "Customizable Desk",
                    "product_id": "Customizable Desk",
                    "product_uom_qty": 5,
                    "product_uom": "Unit(s)"
                }
            ],
            "picking_type_id": "Internal Transfers",
            "priority": "1"
        }
        """
        values = self._prepare_create_vals(values.values)
        stock_picking_id = self._get_model().create(values)
        return self._to_json(stock_picking_id)

    @restapi.method(
        [(["/update"], "POST")],
        input_param=Datamodel("stock.update.param"),
    )
    def update(self, values):
        """
        Update an existing stock picking

        ex:
        "id": 9,
        "values": {
            'origin': 'Inmediate Payment',
        },

        """
        stock_picking_id = self._get(values.id)
        stock_picking_id.write(self._prepare_create_vals(values.values))
        return self._to_json(stock_picking_id)

    @restapi.method(
        [(["/delete"], "DELETE")],
        input_param=Datamodel("stock.id.param"),
    )
    def delete(self, values):
        """
        Delete an existing stock picking

        ex:
        "id": 9

        """
        stock_picking_id = self._get(values.id)
        if stock_picking_id:
            stock_picking_id.unlink()
            return {"response": "Stock picking deleted with id %s" % values.id}

        return {"response": "No picking found with id %s" % values.id}

    @restapi.method(
        [(["/confirm"], "POST")],
        input_param=Datamodel("stock.id.param"),
    )
    def action_confirm(self, values):
        """
        Set Stock Picking as To Do

        ex:
        "id": 9
        """
        stock_picking_id = self._get(values.id)
        if stock_picking_id:
            stock_picking_id.action_confirm()
            return self._to_json(stock_picking_id)
        return {"response": "No picking found with id %s" % values.id}

    @restapi.method(
        [(["/cancel"], "POST")],
        input_param=Datamodel("stock.id.param"),
    )
    def action_cancel(self, values):
        """
        Set Stock Picking as Cancelled

        ex:
        "id": 9
        """
        stock_picking_id = self._get(values.id)
        if stock_picking_id:
            stock_picking_id.action_cancel()
            return self._to_json(stock_picking_id)
        return {"response": "No picking found with id %s" % values.id}

    @restapi.method(
        [(["/validate"], "POST")],
        input_param=Datamodel("stock.id.param"),
    )
    def action_validate(self, values):
        """
        Set Stock Picking as Done

        ex:
        "id": 9
        """
        stock_picking_id = self._get(values.id)
        if stock_picking_id:
            stock_picking_id.button_validate()
            return self._to_json(stock_picking_id)
        return {"response": "No picking found with id %s" % values.id}

    @restapi.method(
        [(["/assign"], "POST")],
        input_param=Datamodel("stock.id.param"),
    )
    def action_assign(self, values):
        """
        Set Stock Picking as Ready

        ex:
        "id": 9
        """
        stock_picking_id = self._get(values.id)
        if stock_picking_id:
            stock_picking_id.action_assign()
            return self._to_json(stock_picking_id)
        return {"response": "No picking found with id %s" % values.id}

    @restapi.method(
        [(["/unreserve"], "POST")],
        input_param=Datamodel("stock.id.param"),
    )
    def action_unreserve(self, values):
        """
        Unreserve picking quantities

        ex:
        "id": 9
        """
        stock_picking_id = self._get(values.id)
        if stock_picking_id:
            stock_picking_id.do_unreserve()
            return self._to_json(stock_picking_id)
        return {"response": "No picking found with id %s" % values.id}

    @restapi.method(
        [(["/do_quantity"], "POST")],
        input_param=Datamodel("stock.update.param"),
    )
    def operation_do_qty(self, values):
        """
        Update picking operation done quantity

        ex:
        "id": 51,
        "values": {"qty_done": 10}
        """
        stock_move_id = self.env["stock.move"].browse(values.id)
        if stock_move_id and stock_move_id.move_line_ids:
            stock_move_id.move_line_ids[0].qty_done = values.values["qty_done"]
            return self._to_json(stock_move_id)
        return {"response": "No stock move found with id %s" % values.id}

    def _to_json(self, stock_picking_id):
        return stock_picking_id.read()

    def _get_model(self):
        return self.env["stock.picking"]

    def _prepare_create_vals(self, create_vals):
        fields2match = self._get_fields2match()

        def _get_recordfstring(field, string):
            result = self.env[fields2match[field]]._name_search(string)
            if not isinstance(result, list):
                query_str, params = result.select()
                self._get_model()._cr.execute(query_str, params)
                result = self._get_model()._cr.fetchall()
            if not result:
                raise UserError(
                    _(
                        f"Couldn't find record for field {field}: {string} \n"
                        f"Try using literal id or changing the string for the name search."
                    )
                )
            return result and result[0] or False

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
            "partner_id": "res.partner",
            "location_id": "stock.location",
            "location_dest_id": "stock.location",
            "picking_type_id": "stock.picking.type",
            "product_id": "product.product",
            "move_ids_without_package": "stock.move",
            "product_uom": "uom.uom",
        }
