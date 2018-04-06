  # -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare


class AccountInvoice(models.Model):
    _inherit = 'account.invoice' 

    @api.model
    def _anglo_saxon_purchase_move_lines(self, i_line, res):
        """Return the additional move lines for purchase invoices and refunds.

        i_line: An account.invoice.line object.
        res: The move line entries produced so far by the parent move_line_get.
        """
        inv = i_line.invoice_id
        company_currency = inv.company_id.currency_id
        if i_line.product_id and i_line.product_id.valuation == 'real_time' and i_line.product_id.type == 'product':
            # get the fiscal position
            fpos = i_line.invoice_id.fiscal_position_id
            # get the price difference account at the product
            acc = i_line.product_id.property_account_creditor_price_difference
            if not acc:
                # if not found on the product get the price difference account at the category
                acc = i_line.product_id.categ_id.property_account_creditor_price_difference_categ
            acc = fpos.map_account(acc).id
            # reference_account_id is the stock input account
            reference_account_id = i_line.product_id.product_tmpl_id.get_product_accounts(fiscal_pos=fpos)['stock_input'].id
            diff_res = []
            account_prec = inv.company_id.currency_id.decimal_places
            # calculate and write down the possible price difference between invoice price and product price
            for line in res:
                if line.get('invl_id', 0) == i_line.id and reference_account_id == line['account_id']:
                    valuation_price_unit = i_line.product_id.uom_id._compute_price(i_line.product_id.standard_price, i_line.uom_id)
                    if i_line.product_id.cost_method != 'standard' and i_line.purchase_line_id:
                        #for average/fifo/lifo costing method, fetch real cost price from incomming moves

                        #CAMBIOS
                        new_price_unit = i_line.purchase_line_id.price_unit
                        if i_line.purchase_line_id.viscosity > 0:
                            new_price_unit = i_line.purchase_line_id.new_price_unit
                        #valuation_price_unit = i_line.purchase_line_id.product_uom._compute_price(i_line.purchase_line_id.price_unit, i_line.uom_id)
                        valuation_price_unit = i_line.purchase_line_id.product_uom._compute_price(new_price_unit, i_line.uom_id)


                        stock_move_obj = self.env['stock.move']
                        valuation_stock_move = stock_move_obj.search([('purchase_line_id', '=', i_line.purchase_line_id.id), ('state', '=', 'done')])
                        if valuation_stock_move:
                            valuation_price_unit_total = 0
                            valuation_total_qty = 0
                            for val_stock_move in valuation_stock_move:
                                valuation_price_unit_total += val_stock_move.price_unit * val_stock_move.product_qty
                                valuation_total_qty += val_stock_move.product_qty
                            valuation_price_unit = valuation_price_unit_total / valuation_total_qty
                            valuation_price_unit = i_line.product_id.uom_id._compute_price(valuation_price_unit, i_line.uom_id)
                    if inv.currency_id.id != company_currency.id:
                            valuation_price_unit = company_currency.with_context(date=inv.date_invoice).compute(valuation_price_unit, inv.currency_id, round=False)
                    if valuation_price_unit != i_line.price_unit and line['price_unit'] == i_line.price_unit and acc:
                        # price with discount and without tax included
                        price_unit = i_line.price_unit * (1 - (i_line.discount or 0.0) / 100.0)
                        tax_ids = []
                        if line['tax_ids']:
                            #line['tax_ids'] is like [(4, tax_id, None), (4, tax_id2, None)...]
                            taxes = self.env['account.tax'].browse([x[1] for x in line['tax_ids']])
                            price_unit = taxes.compute_all(price_unit, currency=inv.currency_id, quantity=1.0)['total_excluded']
                            for tax in taxes:
                                tax_ids.append((4, tax.id, None))
                                for child in tax.children_tax_ids:
                                    if child.type_tax_use != 'none':
                                        tax_ids.append((4, child.id, None))
                        price_before = line.get('price', 0.0)
                        line.update({'price': round(valuation_price_unit * line['quantity'], account_prec)})
                        diff_res.append({
                            'type': 'src',
                            'name': i_line.name[:64],
                            'price_unit': round(price_unit - valuation_price_unit, account_prec),
                            'quantity': line['quantity'],
                            'price': round(price_before - line.get('price', 0.0), account_prec),
                            'account_id': acc,
                            'product_id': line['product_id'],
                            'uom_id': line['uom_id'],
                            'account_analytic_id': line['account_analytic_id'],
                            'tax_ids': tax_ids,
                            })
            return diff_res
        return []

    @api.onchange('currency_id')
    def _onchange_currency_id(self):
        print '_onchange_currency_id'
        if self.currency_id:
            for line in self.invoice_line_ids.filtered(lambda r: r.purchase_line_id):
                #################3
                price_unit = line.purchase_line_id.price_unit
                if line.purchase_line_id.viscosity > 0:
                    price_unit = line.purchase_line_id.new_price_unit
                #################
                #line.price_unit = line.purchase_id.currency_id.compute(line.purchase_line_id.price_unit, self.currency_id, round=False)
                line.price_unit = line.purchase_id.currency_id.compute(price_unit, self.currency_id, round=False)

    # def _prepare_invoice_line_from_po_line(self, line):
    #     print 'SOBREESCRITO _prepare_invoice_line_from_po_line'
    #     if line.product_id.purchase_method == 'purchase':
    #         qty = line.product_qty - line.qty_invoiced
    #     else:
    #         qty = line.qty_received - line.qty_invoiced

    #     ####################
    #     price_unit = line.price_unit
    #     #SI LA VISCOSIDAD > 0, SE UTILIZA LA CANTIDAD NUEVA
    #     #SI LA VISCOSIDAD > 0 SE UTILIZA PRECIO NUEVO
    #     print 'line.viscosity: ',line.viscosity
    #     print 'line.new_price_unit: ',line.new_price_unit
    #     if line.viscosity > 0:
    #         print '111'
    #         qty = line.new_qty
    #         price_unit = line.new_price_unit
    #     print 'price_unit: ',line.order_id.currency_id.compute(price_unit, self.currency_id, round=False)
    #     ####################

    #     if float_compare(qty, 0.0, precision_rounding=line.product_uom.rounding) <= 0:
    #         qty = 0.0
    #     taxes = line.taxes_id
    #     invoice_line_tax_ids = line.order_id.fiscal_position_id.map_tax(taxes)
    #     invoice_line = self.env['account.invoice.line']
    #     data = {
    #         'purchase_line_id': line.id,
    #         'name': line.order_id.name+': '+line.name,
    #         'origin': line.order_id.origin,
    #         'uom_id': line.product_uom.id,
    #         'product_id': line.product_id.id,
    #         'account_id': invoice_line.with_context({'journal_id': self.journal_id.id, 'type': 'in_invoice'})._default_account(),
    #         'price_unit': line.order_id.currency_id.compute(price_unit, self.currency_id, round=False),
    #         'quantity': qty,
    #         'discount': 0.0,
    #         'account_analytic_id': line.account_analytic_id.id,
    #         'analytic_tag_ids': line.analytic_tag_ids.ids,
    #         'invoice_line_tax_ids': invoice_line_tax_ids.ids
    #     }
    #     account = invoice_line.get_invoice_line_account('in_invoice', line.product_id, line.order_id.fiscal_position_id, self.env.user.company_id)
    #     if account:
    #         data['account_id'] = account.id
    #     #print 'data: ',data
    #     return data

    # Load all unsold PO lines
    # @api.onchange('purchase_id')
    # def purchase_order_change(self):
    #     print 'purchase_order_change'
    #     if not self.purchase_id:
    #         return {}
    #     if not self.partner_id:
    #         self.partner_id = self.purchase_id.partner_id.id

    #     new_lines = self.env['account.invoice.line']
    #     for line in self.purchase_id.order_line - self.invoice_line_ids.mapped('purchase_line_id'):
    #         data = self._prepare_invoice_line_from_po_line(line)
    #         new_line = new_lines.new(data)
    #         new_line._set_additional_fields(self)
    #         new_lines += new_line

    #     self.invoice_line_ids += new_lines
    #     self.purchase_id = False
    #     return {}




# class AccountInvoiceLine(models.Model):
#     _inherit = "account.invoice.line"

#     def _set_additional_fields(self, invoice):
#         print '_set_additional_fields'
#         print 'self.purchase_line_id.name: ',self.purchase_line_id.name
#         super(AccountInvoiceLine,self)._set_additional_fields(invoice)
#         if self.purchase_line_id.viscosity > 0:
#             print '222'
#             self.price_unit = self.purchase_line_id.new_price_unit
#             print 'self.price_unit: ',self.price_unit