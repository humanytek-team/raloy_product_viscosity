from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'


    check_viscosity = fields.Boolean(related='product_id.check_viscosity')
    kilograms = fields.Float('Kilos',digits=(10, 3))

    @api.multi
    @api.onchange('kilograms')
    def _compute_qty(self):
        print '_compute_qty'
        for rec in self:
            if rec.kilograms and rec.product_id and rec.product_id.check_viscosity:
                rec.product_qty = rec.kilograms * rec.product_id.viscosity
