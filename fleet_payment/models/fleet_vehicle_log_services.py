# -*- coding: utf-8 -*-

from odoo import models, fields, api

class FleetVehicleLogServices(models.Model):
    _inherit = 'fleet.vehicle.log.services'

    license_plate = fields.Char(string='Plate', related='vehicle_id.license_plate', readonly=True)
    brand = fields.Char(string='Brand', related='vehicle_id.model_id.brand_id.name', readonly=True)
    model = fields.Char(string='Model', related='vehicle_id.model_id.name', readonly=True)
    method_payment_id = fields.Many2one(
        'fleet.method.payment',
        string='Method Payment',
        domain=[('state', '=', 'active')],
        help='Select the payment method'
        )
    ref = fields.Char(string='Reference')