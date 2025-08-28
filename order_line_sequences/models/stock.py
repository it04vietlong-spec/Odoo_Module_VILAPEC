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


class StockMove(models.Model):
    """ Class for inherited model stock move. Contains a field for line
            numbers and a function for computing line numbers."""

    _inherit = 'stock.move'
    _order = "sequence_number asc, id asc"

    sequence_number = fields.Integer(
        string="#",
        default=1,
        help="Line Numbers"
    )

    @api.model
    def create(self, vals):
        if 'picking_id' in vals:
            picking = self.env['stock.picking'].browse(vals['picking_id'])
            max_seq = max(picking.move_ids_without_package.mapped('sequence_number') or [0])
            vals['sequence_number'] = max_seq + 1
        return super().create(vals)


class StockPicking(models.Model):
    """ Class for inherited model stock picking."""
    _inherit = 'stock.picking'
