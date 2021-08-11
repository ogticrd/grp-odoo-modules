from odoo.addons.base_rest.controllers import main


class StockRestPublicApiController(main.RestController):
    _root_path = "/stock_rest_api/public/"
    _collection_name = "stock.rest.api.public.services"
    _default_auth = "public"


class StockRestPrivateApiController(main.RestController):
    _root_path = "/stock_rest_api/private/"
    _collection_name = "stock.rest.api.private.services"
    _default_auth = "user"
