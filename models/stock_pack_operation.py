from odoo import api, exceptions, fields, models


class StopckPackOperation(models.Model):
    _inherit = 'stock.pack.operation'


    @api.model
    def create(self, vals):
        vals['product_uom_qty_default'] = vals.get('product_qty')
        return super(StopckPackOperation, self).create(vals)


    # check_viscosity = fields.Boolean(
    #     related="product_id.product_tmpl_id.check_viscosity",
    # )
    viscosity = fields.Float(
        compute='_get_viscosity',
        digits=(6, 4),
        store=True,
    )

    product_uom_qty_default = fields.Float('Supplier Units')


    new_qty = fields.Float(
        compute='_get_new_qty',
        digits=(6, 4),
        store=True,
    )

    @api.multi
    @api.depends('viscosity')
    def _get_new_qty(self):
        for r in self:
            #if r.check_viscosity and r.viscosity:
            if r.viscosity and r.viscosity > 0:
                 r.new_qty = r.product_uom_qty_default * r.viscosity


    @api.multi
    @api.depends('product_id')
    def _get_viscosity(self):
        #print '_get_viscosity'
        for r in self:
            if not r.viscosity:
                #print '111111'
                #r.viscosity = r.product_id.product_tmpl_id.viscosity

                viscosity = 0
                partner_id = r.picking_id and r.picking_id.partner_id or False
                seller = r.product_id._select_seller_viscosity(partner_id)
                #seller = self.product_id._select_seller_viscosity(partner,self.product_qty,self.order_id.date_order,self.product_uom)


                if seller:
                    viscosity = seller.viscosity

                r.viscosity = viscosity
