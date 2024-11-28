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

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        for rec in self:
            is_return = any(
                move.origin_returned_move_id for move in rec.move_ids
            )
            invoice_id = False
            if is_return and rec.sale_id:
                if rec.sale_id.invoice_ids:
                    for invoice in rec.sale_id.invoice_ids:
                        if invoice.move_type == 'out_invoice':
                            invoice_id = invoice
                    if invoice_id:
                        if invoice_id.state == 'posted':
                            credit_note_vals = {
                                'move_type': 'out_refund',
                                'partner_id': rec.sale_id.partner_id.id,
                                'invoice_origin': rec.sale_id.name,
                                'reversed_entry_id': invoice.id,
                                'ref': _("Return for %s") % invoice.name,
                                'invoice_line_ids': [],
                            }
                            for line in rec.move_ids_without_package:
                                inv_line_id = False
                                for inv_line in invoice_id.invoice_line_ids:
                                    if inv_line.product_id.id == line.product_id.id:
                                        inv_line_id = inv_line
                                credit_note_vals['invoice_line_ids'].append(
                                    (0, 0, {
                                        'product_id': line.product_id.id,
                                        'quantity': line.quantity_done,
                                        'price_unit': inv_line_id.price_unit if inv_line_id else False,
                                        'tax_ids': [(6, 0,
                                                     inv_line_id.tax_ids.ids)] if inv_line_id and inv_line_id.tax_ids else False,
                                    })
                                )
                            credit_note = self.env['account.move'].create(credit_note_vals)
        return res
