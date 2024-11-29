# -*- coding: utf-8 -*-
#############################################################################

#    Alhodood Technologies.
#
#    Copyright (C) 2024-TODAY Alhodood Technologies(<https://www.alhodood.com>)
#    Author: Alhodood Technologies(<https://www.alhodood.com>)
#
#    You can modify it under the terms of the GNU Affero General Public License (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License (AGPL v3) for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from odoo import models, api, fields
from odoo.addons.test_new_api.tests.test_new_fields import insert


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    qty_returned = fields.Float(
        string="Returned Quantity",
        compute='_compute_qty_returned',
        default=0.0,
        digits='Product Unit of Measure',
        store=True, readonly=False, copy=False)
    qty_credited = fields.Float(
        string="Credited Quantity",
        compute='_compute_qty_credited',
        digits='Product Unit of Measure',
        store=True)

    @api.onchange('product_id')
    def _onchange_product_id_price(self):
        if self.product_id:
            today = fields.Datetime.now()
            price_list_item = self.env['product.pricelist.item'].search(
                [('product_id', '=', self.product_id.id), ('date_start', '<=', today), ('date_end', '=', False),
                 ('company_id', '=', self.env.company.id)], limit=1)
            if price_list_item:
                self.price_unit = price_list_item.fixed_price
                self.order_id.pricelist_id = price_list_item.pricelist_id.id

    @api.depends('move_ids.state', 'move_ids.scrapped', 'move_ids.quantity_done', 'move_ids.product_uom',
                 'qty_delivered_method',
                 'analytic_line_ids.so_line',
                 'analytic_line_ids.unit_amount',
                 'analytic_line_ids.product_uom_id')
    def _compute_qty_returned(self):
        for line in self:
            if line.qty_delivered_method == 'stock_move':
                qty = 0.0
                outgoing_moves = self.env['stock.move']
                moves = self.move_ids.filtered(
                    lambda r: r.state != 'cancel' and not r.scrapped and self.product_id == r.product_id)
                if self._context.get('accrual_entry_date'):
                    moves = moves.filtered(
                        lambda r: fields.Date.context_today(r, r.date) <= self._context['accrual_entry_date'])
                for move in moves:
                    if move.origin_returned_move_id:
                        outgoing_moves |= move
                for move in outgoing_moves:
                    if move.state != 'done':
                        continue
                    qty += move.product_uom._compute_quantity(move.quantity_done, line.product_uom, rounding_method='HALF-UP')
                line.qty_returned = qty

    @api.depends('qty_invoiced','qty_credited', 'qty_delivered', 'qty_returned','product_uom_qty', 'state')
    def _compute_qty_credited(self):
        for line in self:
            line.qty_credited = 0
            qty_credited = 0.0
            for invoice_line in line._get_invoice_lines():
                if invoice_line.move_id.state != 'cancel' or invoice_line.move_id.payment_state == 'invoicing_legacy':
                    if invoice_line.move_id.move_type == 'out_refund':
                        qty_credited = invoice_line.product_uom_id._compute_quantity(invoice_line.quantity,
                                                                                      line.product_uom)
            line.qty_credited = qty_credited
