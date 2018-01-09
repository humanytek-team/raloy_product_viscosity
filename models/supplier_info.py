from odoo import api, fields, models


class SuppliferInfo(models.Model):
    _inherit = "product.supplierinfo"


    #CAMPOS
    viscosity = fields.Float(
            digits=(6, 4)
        )