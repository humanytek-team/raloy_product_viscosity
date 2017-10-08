from odoo import api, exceptions, fields, models


class StopckPackOperation(models.Model):
    _inherit = 'stock.pack.operation'


    @api.model
    def create(self, vals):
        vals['product_uom_qty_default'] = vals.get('product_qty')
        return super(StopckPackOperation, self).create(vals)


    check_viscosity = fields.Boolean(
        related="product_id.product_tmpl_id.check_viscosity",
    )
    viscosity = fields.Float(
        compute='_get_viscosity',
        default=lambda self: self.product_id.product_tmpl_id.viscosity,
        digits=(6, 4),
        store=True,
    )

    product_uom_qty_default = fields.Float('Default Qty')

    kg = fields.Float(
        compute='_get_kilograms',
        digits=(6, 4),
        store=True,
    )

    @api.multi
    @api.depends('viscosity')
    def _get_kilograms(self):
        for r in self:
            if r.viscosity != 0:
                r.kg = r.product_uom_qty_default/r.viscosity

    @api.multi
    @api.onchange('viscosity')
    def _get_product_oum_qty_viscosity(self):
        for r in self:
            if r.check_viscosity:
                r.qty_done = (r.product_uom_qty_default/r.viscosity)*(r.product_id.viscosity or 0.0)


    @api.multi
    @api.depends('product_id')
    def _get_viscosity(self):
        for r in self:
            if not r.viscosity:
                r.viscosity = r.product_id.product_tmpl_id.viscosity
