from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import odoo.addons.decimal_precision as dp
from openerp.tools import float_compare

import logging
_logger = logging.getLogger(__name__)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    # @api.onchange('product_qty', 'product_uom')
    # def _onchange_quantity(self):
    #     """
    #     SOBRESCRITURA DE METODO onchange
    #     PARA AGREGAR DATOS VISCOSIDAD, NEW CANTIDAD, NUEVO PRECIO
    #     EN LAS LINEAS DE COMPRA
    #     """
    #     print '_onchange_quantity'
    #     super(PurchaseOrderLine,self)._onchange_quantity()
    #     print 'self: ',self
    #     #NEW#################
    #     seller = self.product_id._select_seller(
    #         partner_id=self.partner_id,
    #         quantity=self.product_qty,
    #         date=self.order_id.date_order and self.order_id.date_order[:10],
    #         uom_id=self.product_uom)

    #     viscosity = 0
    #     format_uom = False
    #     if seller:
    #         if seller.format_uom:
    #             format_uom = seller.format_uom
    #         else:
    #             format_uom = self.product_uom
    #         viscosity = seller.viscosity
    #     self.viscosity = viscosity
    #     self.format_uom = format_uom

    #     if viscosity > 0:
    #         self.new_qty = self.get_new_qty()
    #         self.new_price_unit = self.get_new_price()
    #     #####################

    @api.onchange('product_qty', 'product_uom')
    def _onchange_quantity(self):
        """
        SOBRESCRITURA DE METODO onchange.

        PARA AGREGAR DATOS VISCOSIDAD, NEW CANTIDAD, NUEVO PRECIO
        EN LAS LINEAS DE COMPRA
        """
        print('_onchange_quantity')
        if not self.product_id:
            return

        seller = self.product_id._select_seller(
            partner_id=self.partner_id,
            quantity=self.product_qty,
            date=self.order_id.date_order and self.order_id.date_order[:10],
            uom_id=self.product_uom)

        if seller or not self.date_planned:
            self.date_planned = self._get_date_planned(
                seller).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        if not seller:
            return

        price_unit = self.env['account.tax']._fix_tax_included_price(
            seller.price, self.product_id.supplier_taxes_id, self.taxes_id) if seller else 0.0
        if price_unit and seller and self.order_id.currency_id and seller.currency_id != self.order_id.currency_id:
            price_unit = seller.currency_id.compute(
                price_unit, self.order_id.currency_id)

        if seller and self.product_uom and seller.product_uom != self.product_uom:
            price_unit = seller.product_uom._compute_price(
                price_unit, self.product_uom)

        self.price_unit = price_unit

        # NEW#################
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

            if format_uom.name.lower() in ('kg'):
                x_qty = self.new_qty / self.viscosity
            elif format_uom.name.lower() in ('liter(s)', 'litro(s)'):
                x_qty = self.new_qty * self.viscosity

            if float_compare(x_qty, self.product_qty, precision_digits=5) != 0:
                self.new_qty = self.product_qty

            self.new_price_unit = self.price_unit
            self.onchange_new_price_unit()
            # print 'self.new_price_unit: ',self.new_price_unit

        # if viscosity > 0:
        #     self.new_qty = self.get_new_qty()
        #     self.new_price_unit = self.get_new_price()
        #####################

    # @api.multi
    # def get_format_uom(self):
    #     """
    #     DEVUELVE LA UNIDAD DE MEDIDA DE PROVEEDOR
    #     LA QUE APARECERA EN LA IMPRESION DE PEDIDO DE COMPRA
    #     """
    #     print 'get_format_uom'
    #     _logger.info(u'get_format_uom')
    #     partner = self.order_id.partner_id
    #     _logger.info(u'seller.name %s' % partner.name)
    #     #print 'self.format_uom: ',self.format_uom
    #     if not self.format_uom:
    #         seller = self.product_id._select_seller_viscosity(partner)
    #         #seller = self.product_id._select_seller(partner,self.product_qty,self.order_id.date_order,self.product_uom)
    #         _logger.info(u'no format_uom found...looking')
    #         if seller:
    #             _logger.info(u'seller.name %s' % seller.name)
    #             return seller.format_uom
    #         else:
    #             _logger.info(u'fail')
    #             return self.product_uom
    #     else:
    #         return self.format_uom

    # @api.multi
    # def get_new_qty(self):
    #     """
    #     CALCULA Y DEVUELVE LA CANTIDAD CONVERTIDA EN LTS O KGS
    #     SEGUN CORRESPONDA
    #     ESTA CANTIDAD ES LA QUE SE QUIERE QUEDE GUARDADA EN odoo
    #     Y APARESCA EN LOS MOVIMIENTOS CONTABLES Y ALMACEN
    #     """
    #     print 'get_new_qty'
    #     _logger.info(u'get_new_qty')
    #     #new_qty = 0
    #     new_qty = self.product_qty

    #     if self.viscosity > 0:
    #         #partner = self.order_id.partner_id
    #         format_uom = self.format_uom
    #         if not format_uom:
    #             format_uom = self.get_format_uom()
    #         if format_uom:
    #             new_qty = self.product_qty / self.viscosity

    #     return new_qty

    # @api.multi
    # def get_original_price(self,default_price=False):
    #     print 'get_original_price'
    #     _logger.info(u'get_original_price')

    #     new_price = default_price
    #     if not new_price:
    #         new_price = self.price_unit
    #     if self.viscosity > 0:
    #         #partner = self.order_id.partner_id
    #         format_uom = self.format_uom
    #         if not format_uom:
    #             format_uom = self.get_format_uom()
    #         if format_uom:
    #             if format_uom.name.lower() in ('kg'):
    #                 new_price = new_price * self.viscosity

    #             elif format_uom.name.lower() in ('liter(s)','litro(s)'):
    #                 new_price = new_price / self.viscosity
    #     return new_price

    # @api.multi
    # def get_new_price(self,default_price=False):
    #     print 'get_new_price'
    #     _logger.info(u'get_new_price')

    #     new_price = default_price
    #     if not new_price:
    #         new_price = self.price_unit
    #     if self.viscosity > 0:
    #         #partner = self.order_id.partner_id
    #         format_uom = self.format_uom
    #         if not format_uom:
    #             format_uom = self.get_format_uom()
    #         if format_uom:
    #             if format_uom.name.lower() in ('kg'):
    #                 new_price = new_price / self.viscosity
    #                 #new_price = self.price_unit / self.viscosity

    #             elif format_uom.name.lower() in ('liter(s)','litro(s)'):
    #                 new_price = new_price * self.viscosity
    #                 #new_price = self.price_unit * self.viscosity
    #     return new_price

    # @api.multi
    # def get_new_price(self,default_price=False):
    #     """
    #     DIVIDE EL IMPORTE DE LINEA ENTRE LA CANTIDAD NUEVA
    #     PARA OBTENER EL PRECIO QUE TIENE QUE APARECER
    #     EN LOS MOVIMIENTOS CONTABLES
    #     APLICA SOLO CUANDO LA CONVERSION ES DE KILOS A LTS
    #     SI ES DE LTS A KG, EL NEW PRICE TENDRA L MISMO VALOR QUE PRICE UNIT
    #     """
    #     print 'get_new_price'
    #     _logger.info(u'get_new_price')
    #     new_price = 0
    #     if self.viscosity > 0 and self.new_qty > 0:
    #         if self.format_uom.name.lower() not in ('litro(s)','liter(s)') :
    #             new_price = self.price_subtotal / self.new_qty
    #         else:
    #             new_price = self.price_unit
    #     return new_price

    # @api.multi
    # @api.depends('price_unit')
    # def _compute_new_price_unit(self,):
    #     print '_compute_new_price_unit'
    #     for rec in self:
    #         rec.new_price_unit = rec.get_new_price()

    @api.onchange('new_qty')
    def onchange_new_qty(self):
        print('onchange_new_qty')
        if self.viscosity > 0:
            if self.format_uom.name.lower() in ('kg'):
                self.product_qty = self.new_qty / self.viscosity

            elif self.format_uom.name.lower() in ('liter(s)', 'litro(s)'):
                self.product_qty = self.new_qty * self.viscosity

    # @api.onchange('new_qty')
    # def onchange_new_qty(self):
    #     print 'onchange_new_qty'
    #     if self.viscosity > 0:
    #         self.product_qty = self.new_qty / self.viscosity
    #         print 'self.product_qty: ',self.product_qty

    @api.onchange('new_price_unit', 'new_qty')
    def onchange_new_price_unit(self):
        print('onchange_new_price_unit')
        if self.viscosity > 0:
            if self.format_uom.name.lower() in ('liter(s)', 'litro(s)'):
                return
            else:
                self.price_unit = self.new_price_unit * self.viscosity

    # @api.onchange('new_price_unit','new_qty')
    # def onchange_new_price_unit(self):
    #     print 'onchange_new_price_unit'
    #     if self.viscosity > 0:
    #         self.price_unit = self.new_price_unit * self.viscosity

    # CAMPOS
    # regular_price_unit = fields.Float(string='Original Unit Price', required=False, digits=dp.get_precision('Product Price'))

    viscosity = fields.Float('Density', digits=(6, 4))
    format_uom = fields.Many2one('product.uom')
    new_qty = fields.Float(
        string='New Qty', digits=dp.get_precision('Product Price'))
    new_price_unit = fields.Float(
        string='New Price', digits=dp.get_precision('Product Price'))
    # new_price_unit = fields.Float(string='New Price', digits=dp.get_precision('Product Price'),compute='_compute_new_price_unit')
