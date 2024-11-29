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

from odoo import models, api, fields, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        for move in self:
            if move.move_type == 'out_invoice' and move.invoice_origin:
                sale_order = self.env['sale.order'].search([('name', '=', move.invoice_origin)], limit=1)
                if sale_order:
                    for line in move.invoice_line_ids:
                        sale_line = sale_order.order_line.filtered(lambda l: l.product_id == line.product_id)
                        if sale_line:
                            qty_delivered = sum(sale_line.mapped('qty_delivered'))
                            # qty_invoiced = sum(sale_line.mapped('qty_invoiced'))
                            invoiced_moves = self.env['account.move.line'].search([
                                ('move_id.move_type', '=', 'out_invoice'),
                                ('move_id.invoice_origin', '=', sale_order.name),
                                ('product_id', '=', line.product_id.id),
                                ('move_id.id', '!=', move.id)
                            ])
                            qty_already_invoiced = sum(invoiced_moves.mapped('quantity'))
                            if line.quantity + qty_already_invoiced > qty_delivered:
                                raise UserError(_(
                                    "You can only invoice delivered quantities for the product '%s'. ") % (
                                                    line.product_id.display_name))
                        else:
                            raise UserError(_("You can only invoice delivered product"))
        return super(AccountMove, self).action_post()
