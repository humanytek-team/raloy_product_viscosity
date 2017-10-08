from odoo import api, exceptions, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'


    check_viscosity = fields.Boolean(
        related="product_id.product_tmpl_id.check_viscosity",readonly=True,
    )
    viscosity = fields.Float(
        compute='_get_viscosity',
        digits=(6, 4),
        store=True,
    )
    product_uom_qty_default = fields.Float('Default Qty',
        compute='_get_product_uom_qty_default',
        store=True,
    )

    @api.one
    @api.onchange('viscosity')
    def _get_product_oum_qty_viscosity(self):
        if self.viscosity > 0:
            self.product_uom_qty = self.product_uom_qty_default*self.viscosity
            

    @api.one
    @api.depends('product_uom_qty')
    def _get_viscosity(self):
        if not self.viscosity:
            self.viscosity = self.product_id.product_tmpl_id.viscosity

    @api.one
    @api.depends('product_uom_qty')
    def _get_product_uom_qty_default(self):
        if not self.product_uom_qty_default:
            self.product_uom_qty_default = self.product_uom_qty
