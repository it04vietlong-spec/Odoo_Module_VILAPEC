# -*- coding: utf-8 -*-
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    """ Class for inherited model sale order line. Contains a field for line
            numbers and a function for computing line numbers.
    """

    _inherit = 'sale.order.line'

    _order = "sequence_number asc, id asc"

    sequence_number = fields.Integer(
        string="#",
        help="Line Numbers"
    )

    @api.model
    def create(self, vals):
        if 'order_id' in vals:
            order = self.env['sale.order'].browse(vals['order_id'])
            max_seq = max(order.order_line.mapped('sequence_number') or [0])
            vals['sequence_number'] = max_seq + 1
        return super().create(vals)
