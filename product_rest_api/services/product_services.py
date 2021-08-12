from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_datamodel.restapi import Datamodel
from odoo.addons.component.core import Component


class ProductService(Component):
    _inherit = "base.rest.service"
    _name = "product.service"
    _usage = "product"
    _collection = "product.rest.api.private.services"
    _description = """
        Product Services
        Access to the Product services is only allowed to authenticated users.
        If you are not authenticated please go to <a href='/web/login'>Login</a>
    """

    def get(self, _id):
        """
        Get product's information
        """
        res = self._get(_id)
        return self._to_json(res)

    def _get(self, _id):
        return self._get_model().browse(_id)

    @restapi.method(
        [(["/", "/search"], "GET")],
        input_param=Datamodel("product.search.param"),
    )
    def search(self, domain):
        """
        Search product by domain
        """
        domain = eval(domain.domain.replace("%20", " "))
        product_ids = self._get_model().search(domain)
        return {
            "count": len(product_ids),
            "rows": [self._to_json(product_id) for product_id in product_ids],
        }

    @restapi.method(
        [(["/", "/create"], "POST")],
        input_param=Datamodel("product.create.param"),
    )
    def create(self, values):
        """
        Create a new product
        """
        values = self._prepare_create_vals(values.values)
        product_id = self._get_model().create(values)
        return self._to_json(product_id)

    @restapi.method(
        [(["/update"], "POST")],
        input_param=Datamodel("product.update.param"),
    )
    def update(self, values):
        product_id = self._get(values.id)
        product_id.write(self._prepare_create_vals(values.values))
        return self._to_json(product_id)

    @restapi.method(
        [(["/delete"], "POST")],
        input_param=Datamodel("product.id.param"),
    )
    def delete(self, values):
        product_id = self._get(values.id)
        if product_id:
            product_id.unlink()
            if not product_id:
                return {"response": "Product deleted with id %s" % id}
        else:
            return {"response": "No product found with id %s" % id}

    def _to_json(self, product_id):
        return {
            k: v for k, v in product_id.read()[0].items() if not k.startswith("image_")
        }

    def _get_model(self):
        return self.env["product.product"]

    def _prepare_create_vals(self, params):
        fields2match = self._get_fields2match()
        for param_key, param_value in params.items():
            if param_key in fields2match:
                if type(params[param_key]) is str:
                    params[param_key] = self.env[fields2match[param_key]]._name_search(
                        params[param_value]
                    )[0][0]
                elif type(params[param_key]) is list:
                    for create_tuple in params[param_key]:
                        for tuple_k, tuple_v in create_tuple[2].items():
                            if tuple_k in fields2match:
                                create_tuple[2][tuple_k] = self.env[
                                    fields2match[tuple_k]
                                ]._name_search(params[tuple_v])[0][0]
        return params

    def _get_fields2match(self):
        return {
            "categ_id": "product.category",
            "tic_categ_id": "product.tic.category",
            "taxes_id": "account.tax",
            "company_id": "res.company",
            "supplier_taxes_ids": "account.tax",
        }
