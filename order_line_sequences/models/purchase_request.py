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
