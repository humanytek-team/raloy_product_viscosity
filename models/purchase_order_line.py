from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'


    @api.onchange('product_qty', 'product_uom')
    def _onchange_quantity(self):
        if not self.product_id:
            return

        seller = self.product_id._select_seller(
            partner_id=self.partner_id,
            quantity=self.product_qty,
            date=self.order_id.date_order and self.order_id.date_order[:10],
            uom_id=self.product_uom)

        if seller or not self.date_planned:
            self.date_planned = self._get_date_planned(seller).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        if not seller:
            return

        price_unit = self.env['account.tax']._fix_tax_included_price(seller.price, self.product_id.supplier_taxes_id, self.taxes_id) if seller else 0.0
        if price_unit and seller and self.order_id.currency_id and seller.currency_id != self.order_id.currency_id:
            price_unit = seller.currency_id.compute(price_unit, self.order_id.currency_id)

        if seller and self.product_uom and seller.product_uom != self.product_uom:
            price_unit = seller.product_uom._compute_price(price_unit, self.product_uom)

        #NEW
        viscosity = 0
        if seller:
            viscosity = seller.viscosity
        self.viscosity = viscosity
        ####
        
        self.price_unit = price_unit

        

    #CAMPOS
    viscosity = fields.Float(
            digits=(6, 4)
        )
    #check_viscosity = fields.Boolean(related='product_id.check_viscosity')
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
