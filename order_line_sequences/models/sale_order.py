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
    _inherit = "sale.order.line"

    sequence_number = fields.Integer(
        string="#",
        default=0,
        index=True,
        help="Fixed line number (not resequenced after delete)"
    )

    _order = "sequence_number asc, id asc"

    @api.model
    def create(self, vals):
        """Assign fixed increasing sequence number"""
        if "order_id" in vals:
            order = self.env["sale.order"].browse(vals["order_id"])
            max_seq = max(order.order_line.mapped("sequence_number") or [0])
            vals["sequence_number"] = max_seq + 1
        return super().create(vals)

