from marshmallow import fields

from odoo.addons.datamodel.core import Datamodel


class StockSearch(Datamodel):
    _name = "stock.search.param"
    _description = "Stock Search Param"

    domain = fields.String(required=True, allow_none=False)


class StockCreateParam(Datamodel):
    _name = "stock.create.param"
    _description = "Stock Create Param"

    values = fields.Dict(required=True, allow_none=False)


class StockUpdateParam(Datamodel):
    _name = "stock.update.param"
    _description = "Stock Update Param"

    id = fields.Integer(required=True, allow_none=False)
    values = fields.Dict(required=True, allow_none=False)


class StockIdParam(Datamodel):
    _name = "stock.id.param"
    _description = "Stock Id Param"

    id = fields.Integer(required=True, allow_none=False)


class StockRegisterParam(Datamodel):
    _name = "stock.register.param"
    _description = "Stock Register Param"

    id = fields.Integer(required=True, allow_none=False)
    values = fields.Dict(required=True, allow_none=False)
