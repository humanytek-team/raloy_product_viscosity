from odoo import api, exceptions, fields, models, _
from odoo.tools.float_utils import float_compare, float_round, float_is_zero
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import time


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def check_backorder(self):
        # print 'check_backorder----------------'
        need_rereserve, all_op_processed = self.picking_recompute_remaining_quantities(
            done_qtys=True)

        # SE OBTIENE PRIMER PICKING
        # first_picking = self.get_first_picking(self.group_id)

        for move in self.move_lines:
            # if not move.ignore:
            if move.state != 'cancel':
                # if not self.ignore(move,first_picking): #SOLO TOMAR EN CUENTA SI NO ES DE VISCOSIDAD
                if float_compare(move.remaining_qty, 0, precision_rounding=move.product_id.uom_id.rounding) != 0:
                    return True
        return False

    # def ignore(self,move,first_picking):
    #     """
    #     REVISA SI EL MOVIMIENTO ES DE VISCOSIDAD
    #     SI REGRESA TRUE ES QUE SI
    #     """
    #     print 'ignore'
    #     if first_picking:
    #         if first_picking.picking_type_code == 'incoming':
    #             for operation in first_picking.pack_operation_ids:
    #                 if operation.viscosity and operation.viscosity > 0:
    #                     if operation.product_id.id == move.product_id.id:
    #                         print 'move.product_qty: ',move.product_qty
    #                         print 'abs(operation.ordered_qty-operation.product_qty)): ',abs(operation.ordered_qty-operation.product_qty)
    #                         # if float_compare(move.product_qty, abs(operation.ordered_qty-operation.product_qty), \
    #                         # precision_rounding=move.product_id.uom_id.rounding) != 0:
    #                         if move.product_qty == (abs(operation.ordered_qty-operation.product_qty)):
    #                             print 'TRUE'
    #                             return True
    #     return False

    # def get_first_picking(self,group_id):
    #     print 'get_first_picking'
    #     if group_id:
    #         group_id = group_id.id
    #         move_obj = self.env['stock.move']
    #         moves = move_obj.search([('group_id','=',group_id)])
    #         print 'moves: ',moves
    #         if moves:
    #             picking_ids = [move.picking_id.id for move in moves]
    #             picking_ids.sort()
    #             print 'picking_ids: ',picking_ids
    #             first_pick_id = picking_ids[0]
    #             first_picking = [move.picking_id for move in moves if first_pick_id == move.picking_id.id][0]
    #             return first_picking
    #     return False


class StopckPackOperation(models.Model):
    _inherit = 'stock.pack.operation'

    @api.model
    def create(self, vals):
        # print 'create'
        # print 'vals',vals
        vals['product_uom_qty_default'] = vals.get('product_qty')

        # BUSCAR PICKING
        picking_id = vals.get('picking_id', False)
        picking_obj = self.env['stock.picking']
        res = picking_obj.search([('id', '=', picking_id)])
        # print 'res: ',res
        if res and res.purchase_id:
            for line in res.purchase_id.order_line:
                print('line.product_id.id: ', line.product_id.id)
                if line.product_id.id == vals.get('product_id'):
                    vals['viscosity'] = line.viscosity
                    vals['format_uom'] = line.format_uom.id
                    vals['product_uom_qty_default'] = line.new_qty
                    vals['new_qty'] = line.product_qty
                    continue
                # if line.product_id.id == vals.get('product_id'):
                #     vals['viscosity'] = line.viscosity
                #     vals['format_uom'] = line.format_uom.id
                #     vals['product_uom_qty_default'] = line.product_qty
                #     vals['new_qty'] = line.new_qty
                #     continue

        return super(StopckPackOperation, self).create(vals)

    # check_viscosity = fields.Boolean(
    #     related="product_id.product_tmpl_id.check_viscosity",
    # )
    viscosity = fields.Float('Density',
                             # compute='_get_viscosity',
                             # inverse='_compute_new_qty',
                             digits=(6, 4),
                             # store=True,
                             )

    # format_uom = fields.Many2one('product.uom', compute='_get_viscosity')
    format_uom = fields.Many2one('product.uom')

    product_uom_qty_default = fields.Float('Supplier Units')

    new_qty = fields.Float(
        # compute='_get_new_qty',
        digits=(6, 4),
        # store=True,
    )

    picking_type_code = fields.Char(compute='_get_picking_type_code')

    @api.one
    @api.constrains('product_uom_qty_default')
    def _check_product_uom_qty_default(self):
        if self.viscosity and self.product_uom_qty_default <= 0:
            raise exceptions.ValidationError(
                _("The Supplier Units must be positive"))

    @api.multi
    @api.onchange('viscosity', 'product_uom_qty_default')
    def onchange_viscosity(self):
        print('onchange_viscosity')
        for r in self:
            if r.viscosity and r.viscosity > 0 and r.picking_type_code == 'incoming':
                r.new_qty = r.product_uom_qty_default / float(r.viscosity)
                # if r.format_uom.name.lower() in ('kg'):
                #     r.new_qty = r.product_uom_qty_default / float(r.viscosity)

                # elif r.format_uom.name.lower() in ('liter(s)','litro(s)'):
                #     r.new_qty = r.product_uom_qty_default * r.viscosity
                # print 'r.new_qty: ',r.new_qty

    # @api.multi
    # @api.depends('viscosity')
    # def _get_new_qty(self):
    #     for r in self:
    #         if r.viscosity and r.viscosity > 0 and r.picking_type_code == 'incoming':

    #             if r.format_uom.name.lower() in ('kg'):
    #                 r.new_qty = r.product_uom_qty_default / float(r.viscosity)

    #             elif r.format_uom.name.lower() in ('liter(s)','litro(s)'):
    #                 r.new_qty = r.product_uom_qty_default * r.viscosity
    #             print 'r.new_qty: ',r.new_qty

    # @api.multi
    # @api.depends('product_id')
    # def _get_viscosity(self):
    #     print '_get_viscosity'
    #     for r in self:
    #         if not r.viscosity and r.picking_type_code == 'incoming':
    #             #print '111111'
    #             #r.viscosity = r.product_id.product_tmpl_id.viscosity

    #             viscosity = 0
    #             partner_id = r.picking_id and r.picking_id.partner_id or False
    #             seller = r.product_id._select_seller_viscosity(partner_id)
    #             #seller = self.product_id._select_seller_viscosity(partner,self.product_qty,self.order_id.date_order,self.product_uom)

    #             if seller:
    #                 viscosity = seller.viscosity
    #                 format_uom = seller.format_uom.id
    #                 print 'format_uom'
    #                 r.format_uom = format_uom

    #             r.viscosity = viscosity

    @api.multi
    def _get_picking_type_code(self):
        print('_get_picking_type_code')
        for r in self:
            if r.picking_id and r.picking_id.picking_type_id:
                r.picking_type_code = r.picking_id.picking_type_id.code


class StockMove(models.Model):
    _inherit = 'stock.move'

    # INDICA SI EL MOV SERA IGNORADO AL CALCULAR LA CANTIDAD FALTANTE (remaining_qty)
    ignore = fields.Boolean()
