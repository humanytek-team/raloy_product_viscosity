from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'


    check_viscosity = fields.Boolean(related='product_id.check_viscosity')
    # kilograms = fields.Float('Kilos',digits=(10, 3), compute='_compute_kg')

    # @api.multi
    # @api.onchange('product_qty')
    # def _compute_kg(self):
    #     print '_compute_kg'
    #     for rec in self:
    #         if rec.product_qty and rec.product_id and rec.product_id.check_viscosity:
    #             if rec.product_id.viscosity > 0:
    #                 rec.kilograms = rec.product_qty / rec.product_id.viscosity


    # @api.multi
    # @api.onchange('kilograms')
    # def _compute_qty(self):
    #     print '_compute_qty'
    #     for rec in self:
    #         if rec.kilograms and rec.product_id and rec.product_id.check_viscosity:
    #             rec.product_qty = rec.kilograms * rec.product_id.viscosity

    # @api.depends('product_qty', 'price_unit', 'taxes_id')
    # def _compute_amount(self):
    #     print '_compute_amount'
    #     for line in self:
    #         if line.kilograms and line.product_id and line.product_id.check_viscosity:
    #             taxes = line.taxes_id.compute_all(line.price_unit, line.order_id.currency_id, line.kilograms, product=line.product_id, partner=line.order_id.partner_id)
    #         else:
    #             taxes = line.taxes_id.compute_all(line.price_unit, line.order_id.currency_id, line.product_qty, product=line.product_id, partner=line.order_id.partner_id)
    #         line.update({
    #             'price_tax': taxes['total_included'] - taxes['total_excluded'],
    #             'price_total': taxes['total_included'],
    #             'price_subtotal': taxes['total_excluded'],
    #         })
