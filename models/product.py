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
            quantity_uom_seller = quantity
            if partner_id and seller.name not in [partner_id, partner_id.parent_id]:
                continue
            if seller.product_id and seller.product_id != self:
                continue

            res |= seller
            break
        return res
       