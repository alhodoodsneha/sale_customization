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


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

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
