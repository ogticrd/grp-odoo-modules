from marshmallow import fields
from odoo.addons.datamodel.core import Datamodel


class ProductSearch(Datamodel):
    _name = "product.search.param"
    _description = "Product Search Param"

    domain = fields.String(required=True, allow_none=False)


class ProductCreateParam(Datamodel):
    _name = "product.create.param"
    _description = "Product Create Param"

    values = fields.Dict(required=True, allow_none=False)


class ProductUpdateParam(Datamodel):
    _name = "product.update.param"
    _description = "Product Update Param"

    id = fields.Integer(required=True, allow_none=False)
    values = fields.Dict(required=True, allow_none=False)


class ProductUpdateParam(Datamodel):
    _name = "product.id.param"
    _description = "Product Id Param"

    id = fields.Integer(required=True, allow_none=False)
