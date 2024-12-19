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
import io
import xlrd
from datetime import datetime
from odoo.tools.misc import xlsxwriter

class ProductPriceListUpload(models.TransientModel):
    _name = 'product.price.list.upload'
    _description = "Product Price List Upload"

    file = fields.Binary(string='Upload File')
    filename = fields.Char(string='Filename')

    def action_process_file(self):
        if not self.file:
            raise UserError(_("Please upload a file."))
        file_data = base64.b64decode(self.file)
        workbook = xlrd.open_workbook(file_contents=file_data)
        sheet = workbook.sheet_by_index(0)
        today = fields.Datetime.now()
        pricelist = self.env['product.pricelist'].search(
            [('company_id', '=', self.env.company.id), ('is_bulk_upload', '=', True)], limit=1)
        if not pricelist:
            pricelist = self.env['product.pricelist'].sudo().create({
                'name': self.env.company.name + ' - Price List',
                'company_id': self.env.company.id,
                'currency_id': self.env.company.currency_id.id,
                'is_bulk_upload': True,
            })
        for row_no in range(1, sheet.nrows):
            prod_sku = str(sheet.cell(row_no, 0).value).strip()
            product_id = self.env['product.product'].search([('prod_sku', '=', prod_sku)])
            if not product_id:
                raise UserError(_("Product With SKU Code  %s Not Found", prod_sku))
            if len(product_id) > 1:
                raise UserError(_("Multiple Product Found With Same SKU Code %s !!", prod_sku))
            price = float(sheet.cell(row_no, 2).value)
            price_list_item = self.env['product.pricelist.item'].search(
                [('pricelist_id', '=', pricelist.id), ('product_id', '=', product_id.id),('date_end','=',False)])
            if price_list_item:
                price_list_item.date_end = today
            self.env['product.pricelist.item'].create({
                'pricelist_id': pricelist.id,
                'compute_price': 'fixed',
                'applied_on': '0_product_variant',
                'product_id': product_id.id,
                'product_tmpl_id': product_id.product_tmpl_id.id,
                'fixed_price': price,
                'date_start': today,
            })

    def action_export_template(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Import Price list')
        headers = ['SKU Code', 'Barcode', 'Price']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header)
        workbook.close()
        output.seek(0)
        attachment = self.env['ir.attachment'].create({
            'name': 'Import Price List.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'self'
        }