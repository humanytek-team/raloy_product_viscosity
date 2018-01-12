# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import UserError, RedirectWarning, ValidationError


class PurchaseOrderLine(models.Model):
    _inherit = ['purchase.order.line']

    @api.multi
    def get_format_uom(self):
        #print 'get_format_uom'
        partner = self.order_id.partner_id
        seller = self.product_id._select_seller(partner_id=partner)
        if seller:
            return seller.format_uom.name
        #print 'fail'
        return self.product_uom.name

       