from odoo import api, exceptions, fields, models, _
from odoo.tools.float_utils import float_compare, float_round, float_is_zero
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import time


class Picking(models.Model):
    _inherit = 'stock.picking'



    def check_backorder(self):
        #print 'check_backorder----------------'
        need_rereserve, all_op_processed = self.picking_recompute_remaining_quantities(done_qtys=True)

        #SE OBTIENE PRIMER PICKING
        #first_picking = self.get_first_picking(self.group_id)

        for move in self.move_lines:
            #if not move.ignore:
            if move.state != 'cancel':
            #if not self.ignore(move,first_picking): #SOLO TOMAR EN CUENTA SI NO ES DE VISCOSIDAD
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

    format_uom = fields.Many2one('product.uom', compute='_get_viscosity')

    product_uom_qty_default = fields.Float('Supplier Units')


    new_qty = fields.Float(
        compute='_get_new_qty',
        digits=(6, 4),
        store=True,
    )

    picking_type_code = fields.Char(compute='_get_picking_type_code')

    @api.multi
    @api.depends('viscosity')
    def _get_new_qty(self):
        for r in self:
            #if r.check_viscosity and r.viscosity:
            if r.viscosity and r.viscosity > 0 and r.picking_type_code == 'incoming':

                # print 'self.format_uom.name.lower(): ',self.format_uom.name.lower()
                # print 'r.product_uom_qty_default: ',r.product_uom_qty_default
                # print 'r.viscosity: ',r.viscosity
                if self.format_uom.name.lower() in ('kg'):
                    r.new_qty = r.product_uom_qty_default * r.viscosity
                elif self.format_uom.name.lower() in ('liter(s)','litro(s)'):
                    r.new_qty = r.product_uom_qty_default / float(r.viscosity)


    @api.multi
    @api.depends('product_id')
    def _get_viscosity(self):
        print '_get_viscosity'
        for r in self:
            if not r.viscosity and r.picking_type_code == 'incoming':
                #print '111111'
                #r.viscosity = r.product_id.product_tmpl_id.viscosity

                viscosity = 0
                partner_id = r.picking_id and r.picking_id.partner_id or False
                seller = r.product_id._select_seller_viscosity(partner_id)
                #seller = self.product_id._select_seller_viscosity(partner,self.product_qty,self.order_id.date_order,self.product_uom)


                if seller:
                    viscosity = seller.viscosity
                    format_uom = seller.format_uom.id
                    print 'format_uom'
                    r.format_uom = format_uom

                r.viscosity = viscosity
                


    @api.multi
    def _get_picking_type_code(self):
        print '_get_picking_type_code'
        for r in self:
            if r.picking_id and r.picking_id.picking_type_id:
                r.picking_type_code = r.picking_id.picking_type_id.code


class StockMove(models.Model):
    _inherit = 'stock.move'

    #INDICA SI EL MOV SERA IGNORADO AL CALCULAR LA CANTIDAD FALTANTE (remaining_qty)
    ignore = fields.Boolean()