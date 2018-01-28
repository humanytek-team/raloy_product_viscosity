# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import UserError, RedirectWarning, ValidationError

import logging
_logger = logging.getLogger(__name__)



class PurchaseOrderLine(models.Model):
    _inherit = ['purchase.order.line']

    @api.multi
    def get_format_uom(self):
        #print 'get_format_uom'
        _logger.info(u'get_format_uom')
        partner = self.order_id.partner_id
        _logger.info(u'seller.name %s' % partner.name)
        if not self.format_uom:
            seller = self.product_id._select_seller_viscosity(partner)
            #seller = self.product_id._select_seller(partner,self.product_qty,self.order_id.date_order,self.product_uom)
            _logger.info(u'no format_uom found...looking')
            if seller:
                _logger.info(u'seller.name %s' % seller.name)
                return seller.format_uom.name
        _logger.info(u'fail')
        return self.product_uom.name


    @api.multi
    def get_new_qty(self):
        #print 'get_new_qty'
        _logger.info(u'get_new_qty')
        partner = self.order_id.partner_id
        new_qty = 0

        format_uom = self.format_uom
        if not format_uom:
            format_uom = self.get_format_uom()
        #     seller = self.product_id._select_seller(partner,self.product_qty,self.order_id.date_order,self.product_uom)
            
        #     if seller:
        #         print 'seller.name: ',seller.name
        #         format_uom = seller.format_uom.name
        #     else:
        #         format_uom = 
        # else:
        #     format_uom = self.format_uom.name

        if format_uom.lower() in ('kg'):
            new_qty = self.product_qty / self.viscosity
            
        elif format_uom.lower() in ('liter(s)','litro(s)'):
            new_qty = self.product_qty * self.viscosity

        return new_qty




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
            quantity_uom_seller = quantity
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