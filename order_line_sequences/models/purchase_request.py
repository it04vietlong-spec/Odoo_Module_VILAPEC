from odoo import api, fields, models

class PurchaseRequestLine(models.Model):
    _inherit = "purchase.request.line"

    _order = "sequence_number asc, id asc" 

    sequence_number = fields.Integer(
        string="#",
        help="Line Numbers"
    )

    @api.model
    def create(self, vals):
        if 'request_id' in vals:
            request = self.env['purchase.request'].browse(vals['request_id'])
            max_seq = max(request.line_ids.mapped('sequence_number') or [0])
            vals['sequence_number'] = max_seq + 1
        return super().create(vals)


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    sequence_cleanup_done = fields.Boolean(
        compute='_compute_sequence_cleanup_done',
        store=False,
    )

    def _compute_sequence_cleanup_done(self):
        for req in self:
            done = True
            lines = req.line_ids
            if any(not l.sequence_number for l in lines):
                done = False
                for idx, line in enumerate(lines.sorted(lambda l: (l.id or 0)), start=1):
                    if line.sequence_number != idx:
                        line.sequence_number = idx
                done = True
            req.sequence_cleanup_done = done
