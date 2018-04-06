# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import UserError, RedirectWarning, ValidationError

import logging
_logger = logging.getLogger(__name__)


# class PurchaseOrder(models.Model):
#     _inherit = "purchase.order"


#     @api.depends('order_line.price_total_viscosity')
#     def _amount_all_viscosity(self):
#         for order in self:
#             amount_untaxed = amount_tax = 0.0
#             for line in order.order_line:
#                 amount_untaxed += line.price_subtotal_viscosity
#                 # FORWARDPORT UP TO 10.0
#                 if order.company_id.tax_calculation_rounding_method == 'round_globally':
#                     price_unit = line.get_new_price()
#                     product_qty = line.get_new_qty()
#                     taxes = line.taxes_id.compute_all(price_unit, line.order_id.currency_id, product_qty, product=line.product_id, partner=line.order_id.partner_id)
#                     amount_tax += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
#                 else:
#                     amount_tax += line.price_tax_viscosity
#             order.update({
#                 'amount_untaxed_viscosity': order.currency_id.round(amount_untaxed),
#                 'amount_tax_viscosity': order.currency_id.round(amount_tax),
#                 'amount_total_viscosity': amount_untaxed + amount_tax,
#             })

#     amount_untaxed_viscosity = fields.Monetary(string='Untaxed Amount Viscosity', store=False, readonly=True, compute='_amount_all_viscosity')
#     amount_tax_viscosity = fields.Monetary(string='Taxes Viscosity', store=False, readonly=True, compute='_amount_all_viscosity')
#     amount_total_viscosity = fields.Monetary(string='Total Viscosity', store=False, readonly=True, compute='_amount_all_viscosity')


# class PurchaseOrderLine(models.Model):
#     _inherit = ['purchase.order.line']

#     @api.multi
#     def get_format_uom(self):
#         #print 'get_format_uom'
#         _logger.info(u'get_format_uom')
#         partner = self.order_id.partner_id
#         _logger.info(u'seller.name %s' % partner.name)
#         if not self.format_uom:
#             seller = self.product_id._select_seller_viscosity(partner)
#             #seller = self.product_id._select_seller(partner,self.product_qty,self.order_id.date_order,self.product_uom)
#             _logger.info(u'no format_uom found...looking')
#             if seller:
#                 _logger.info(u'seller.name %s' % seller.name)
#                 return seller.format_uom.name
#         _logger.info(u'fail')
#         return self.product_uom.name


#     @api.multi
#     def get_new_qty(self):
#         #print 'get_new_qty'
#         _logger.info(u'get_new_qty')
#         #new_qty = 0
#         new_qty = self.product_qty

#         if self.viscosity > 0:
#             partner = self.order_id.partner_id
#             format_uom = self.format_uom
#             if not format_uom:
#                 format_uom = self.get_format_uom()

#             if format_uom.lower() in ('kg'):
#                 new_qty = self.product_qty / self.viscosity

#             elif format_uom.lower() in ('liter(s)','litro(s)'):
#                 new_qty = self.product_qty * self.viscosity

#         return new_qty

#     @api.multi
#     def get_new_price(self):
#         #print 'get_new_price'
#         _logger.info(u'get_new_price')
#         new_price = self.price_unit
#         if self.viscosity > 0:
#             partner = self.order_id.partner_id
#             format_uom = self.format_uom
#             if not format_uom:
#                 format_uom = self.get_format_uom()

#             if format_uom.lower() in ('kg'):
#                 new_price = self.price_unit / self.viscosity

#             elif format_uom.lower() in ('liter(s)','litro(s)'):
#                 new_price = self.price_unit * self.viscosity

#         return new_price

#     @api.depends('product_qty', 'price_unit', 'taxes_id')
#     def _compute_amount_viscosity(self):
#         for line in self:
#             price_unit = line.get_new_price()
#             product_qty = line.get_new_qty()

#             taxes = line.taxes_id.compute_all(price_unit, line.order_id.currency_id, product_qty, product=line.product_id, partner=line.order_id.partner_id)
#             line.update({
#                 'price_tax_viscosity': taxes['total_included'] - taxes['total_excluded'],
#                 'price_total_viscosity': taxes['total_included'],
#                 'price_subtotal_viscosity': taxes['total_excluded'],
#             })

#     price_subtotal_viscosity = fields.Monetary(compute='_compute_amount_viscosity', string='Subtotal Viscosity', store=False)
#     price_total_viscosity = fields.Monetary(compute='_compute_amount_viscosity', string='Total Viscosity', store=False)
#     price_tax_viscosity = fields.Monetary(compute='_compute_amount_viscosity', string='Tax Viscosity', store=False)


class ProductProduct(models.Model):
    _inherit = ['product.product']

    @api.multi
    def _select_seller_viscosity(self, partner_id=False, quantity=0.0, date=None, uom_id=False):
        self.ensure_one()
        _logger.info(u'_select_seller_viscosity')
        if date is None:
            date = fields.Date.today()
        res = self.env['product.supplierinfo']
        for seller in self.seller_ids:
            _logger.info(u'seller.name %s' % seller.name)
            # Set quantity in UoM of seller
            # quantity_uom_seller = quantity
            # if quantity_uom_seller and uom_id and uom_id != seller.product_uom:
            #     quantity_uom_seller = uom_id._compute_quantity(quantity_uom_seller, seller.product_uom)

            # if seller.date_start and seller.date_start > date:
            #     _logger.info(u'1111')
            #     continue
            # if seller.date_end and seller.date_end < date:
            #     _logger.info(u'2222')
            #     continue
            if partner_id and seller.name not in [partner_id, partner_id.parent_id]:
                _logger.info(u'3333')
                continue
            # if quantity_uom_seller < seller.min_qty:
            #     _logger.info(u'4444')
            #     continue
            if seller.product_id and seller.product_id != self:
                _logger.info(u'5555')
                continue

            res |= seller
            break
        return res
#
