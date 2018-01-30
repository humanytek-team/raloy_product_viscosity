from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import logging
_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"


    @api.depends('order_line.price_total')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                # FORWARDPORT UP TO 10.0
                if order.company_id.tax_calculation_rounding_method == 'round_globally':
                    #price_unit = line.get_new_price()
                    product_qty = line.get_new_qty()
                    taxes = line.taxes_id.compute_all(line.price_unit, line.order_id.currency_id, product_qty, product=line.product_id, partner=line.order_id.partner_id)
                    amount_tax += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                else:
                    amount_tax += line.price_tax
            order.update({
                'amount_untaxed': order.currency_id.round(amount_untaxed),
                'amount_tax': order.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax,
            })

    # amount_untaxed = fields.Monetary(string='Untaxed Amount Viscosity', store=False, readonly=True, compute='_amount_all')
    # amount_tax = fields.Monetary(string='Taxes Viscosity', store=False, readonly=True, compute='_amount_all')
    # amount_total = fields.Monetary(string='Total Viscosity', store=False, readonly=True, compute='_amount_all')


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'


    # @api.model
    # def create(self, values):
    #     print 'purchase create'
    #     line = super(PurchaseOrderLine, self).create(values)
        
    #     new_price = line.get_new_price()
    #     print 'new_price: ',new_price
    #     line.new_price = new_price
    #     print 'line.new_price: ',line.new_price
    #     return line

    # @api.multi
    # def write(self, values):
    #     print 'purchase write'
    #     result = super(PurchaseOrderLine, self).write(values)
    #     print 'result: ',result
    #     new_price = self.get_new_price()
    #     print 'new_price: ',new_price
    #     self.new_price = new_price
    #     print 'self.new_price: ',self.new_price

    #     return result

    @api.onchange('product_qty', 'product_uom')
    def _onchange_quantity(self):
        #print '_onchange_quantity'
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
        format_uom = False
        if seller:
            if seller.format_uom:
                format_uom = seller.format_uom
            else:
                format_uom = self.product_uom
            viscosity = seller.viscosity
        self.viscosity = viscosity
        self.format_uom = format_uom

        if viscosity > 0:
            price_unit = self.get_new_price(price_unit)
        ####
        self.price_unit = price_unit



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
                return seller.format_uom
        _logger.info(u'fail')
        return self.product_uom


    @api.multi
    def get_new_qty(self):
        #print 'get_new_qty'
        _logger.info(u'get_new_qty')
        #new_qty = 0
        new_qty = self.product_qty

        if self.viscosity > 0:
            #partner = self.order_id.partner_id
            format_uom = self.format_uom
            if not format_uom:
                format_uom = self.get_format_uom()
            if format_uom:
                if format_uom.name.lower() in ('kg'):
                    new_qty = self.product_qty / self.viscosity
                    
                elif format_uom.name.lower() in ('liter(s)','litro(s)'):
                    new_qty = self.product_qty * self.viscosity

        return new_qty

    @api.multi
    def get_new_price(self,default_price=False):
        _logger.info(u'get_new_price')

        new_price = default_price
        if not new_price:
            new_price = self.price_unit
        if self.viscosity > 0:
            #partner = self.order_id.partner_id
            format_uom = self.format_uom
            if not format_uom:
                format_uom = self.get_format_uom()
            if format_uom:
                if format_uom.name.lower() in ('kg'):
                    new_price = new_price / self.viscosity
                    #new_price = self.price_unit / self.viscosity
                    
                elif format_uom.name.lower() in ('liter(s)','litro(s)'):
                    new_price = new_price * self.viscosity
                    #new_price = self.price_unit * self.viscosity
        return new_price

    @api.depends('product_qty', 'price_unit', 'taxes_id', 'viscosity')
    def _compute_amount(self):
        for line in self:
            #price_unit = line.get_new_price()
            product_qty = line.get_new_qty()

            taxes = line.taxes_id.compute_all(line.price_unit, line.order_id.currency_id, product_qty, product=line.product_id, partner=line.order_id.partner_id)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    #CAMPOS
    format_uom = fields.Many2one('product.uom')
    viscosity = fields.Float(digits=(6, 4))
    #price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal Viscosity', store=False)
    #price_total = fields.Monetary(compute='_compute_amount', string='Total Viscosity', store=False)
    #price_tax = fields.Monetary(compute='_compute_amount', string='Tax Viscosity', store=False)