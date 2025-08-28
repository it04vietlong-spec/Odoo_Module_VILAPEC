from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    """ Class for inherited model purchase order line. Contains a field for line
        numbers and a function for computing line numbers.
    """

    _inherit = 'purchase.order.line'

    _order = "sequence_number asc, id asc"

    sequence_number = fields.Integer(
        string="#",
        help="Line Numbers"
    )

    @api.model
    def create(self, vals):
        if 'order_id' in vals:
            order = self.env['purchase.order'].browse(vals['order_id'])
            max_seq = max(order.order_line.mapped('sequence_number') or [0])
            vals['sequence_number'] = max_seq + 1
        return super().create(vals)
