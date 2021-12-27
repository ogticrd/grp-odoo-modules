from odoo.addons.base_rest.controllers import main


class ProductRestPublicApiController(main.RestController):
    _root_path = "/product_rest_api/public/"
    _collection_name = "product.rest.api.public.services"
    _default_auth = "public"


class ProductRestPrivateApiController(main.RestController):
    _root_path = "/product_rest_api/private/"
    _collection_name = "product.rest.api.private.services"
    _default_auth = "api_key"
