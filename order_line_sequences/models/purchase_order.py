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


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    sequence_cleanup_done = fields.Boolean(
        compute='_compute_sequence_cleanup_done',
        store=False,
    )

    def _compute_sequence_cleanup_done(self):
        for order in self:
            done = True
            lines = order.order_line
            if any(not l.sequence_number for l in lines):
                done = False
                for idx, line in enumerate(lines.sorted(lambda l: (l.sequence, l.id or 0)), start=1):
                    if line.sequence_number != idx:
                        line.sequence_number = idx
                done = True
            order.sequence_cleanup_done = done
