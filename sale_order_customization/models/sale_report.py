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


from odoo import api, fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    qty_returned = fields.Float('Qty Returned', readonly=True)
    qty_credited = fields.Float('Qty Credited', readonly=True)

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res['qty_returned'] = "CASE WHEN l.product_id IS NOT NULL THEN SUM(l.qty_returned / u.factor * u2.factor) ELSE 0 END"
        res['qty_credited'] = "CASE WHEN l.product_id IS NOT NULL THEN SUM(l.qty_credited / u.factor * u2.factor) ELSE 0 END"
        return res
