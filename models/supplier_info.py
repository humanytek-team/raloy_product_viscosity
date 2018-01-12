from odoo import api, fields, models


class SuppliferInfo(models.Model):
    _inherit = "product.supplierinfo"


    #CAMPOS
    viscosity = fields.Float(digits=(6, 4))
    format_uom = fields.Many2one('product.uom', 'Format Unit of Measure',help="Printed in formats for products with viscosity")