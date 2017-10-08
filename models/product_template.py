from odoo import api, exceptions, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    check_viscosity = fields.Boolean()
    viscosity = fields.Float(
        digits=(6, 4)
    )

    @api.one
    @api.constrains('check_viscosity', 'viscosity')
    def _check_viscosity(self):
        if self.check_viscosity and self.viscosity <= 0:
            raise exceptions.ValidationError("Viscosity must be positive")
