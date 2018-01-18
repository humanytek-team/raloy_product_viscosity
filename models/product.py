# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import UserError, RedirectWarning, ValidationError

import logging
_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = ['product.product']

    @api.multi
    def _select_seller_viscosity(self, partner_id=False, quantity=0.0, date=None, uom_id=False):
        self.ensure_one()
        _logger.info(u'_select_seller')
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
       