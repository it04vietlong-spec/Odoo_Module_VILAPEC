from odoo import api, fields, models
from .money_to_text import MoneyToText

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    amount_in_words = fields.Char(
        string='Số tiền bằng chữ',
        compute='_compute_amount_in_words',
        store=True,
        help='Số tiền được viết bằng chữ tiếng Việt'
    )
    
    @api.depends('amount_total', 'currency_id')
    def _compute_amount_in_words(self):
        """Tính toán số tiền bằng chữ dựa trên tổng tiền và loại tiền tệ"""
        for record in self:
            if record.amount_total and record.currency_id:
                currency_code = record.currency_id.name
                amount_text = MoneyToText.number_to_text_vn(record.amount_total, currency_code)
                record.amount_in_words = amount_text
            else:
                record.amount_in_words = ''
