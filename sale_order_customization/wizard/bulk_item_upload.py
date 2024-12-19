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

from odoo import fields, models, _
from odoo.exceptions import UserError
import base64
import xlrd


class BulkItemUpload(models.TransientModel):
    _name = 'bulk.item.upload'
    _description = "Bulk Item Upload"

    file = fields.Binary(string='Upload File', required=True)
    filename = fields.Char(string='Filename')

    def action_process_file(self):
        if not self.file:
            raise UserError(_("Please upload a file."))
        sale_order = self.env['sale.order'].sudo().search([('id', '=', self.env.context['active_id'])])
        file_data = base64.b64decode(self.file)
        workbook = xlrd.open_workbook(file_contents=file_data)
        sheet = workbook.sheet_by_index(0)
        for row_no in range(1, sheet.nrows):
            prod_sku = str(sheet.cell(row_no, 0).value).strip()
            qty = float(sheet.cell(row_no, 2).value)
            product_id = self.env['product.product'].search([('prod_sku', '=', prod_sku)])
            if not product_id:
                raise UserError(_("Product With SKU Code  %s Not Found", prod_sku))
            else:
                today = fields.Datetime.now()
                price_list_item = self.env['product.pricelist.item'].search(
                    [('product_id', '=', product_id.id), ('date_start', '<=', today), ('date_end', '=', False),
                     ('company_id', '=', self.env.company.id)], limit=1)
                self.env['sale.order.line'].create({
                    'order_id':sale_order.id,
                    'product_id': product_id.id,
                    'product_template_id': product_id.product_tmpl_id.id,
                    'product_uom_qty':qty,
                    'price_unit': price_list_item.fixed_price if price_list_item else False,
                })
