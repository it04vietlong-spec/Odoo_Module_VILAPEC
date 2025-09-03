from odoo import api, fields, models

class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'
    
    validation_status_display = fields.Char(
        string='Trạng thái Validate',
        compute='_compute_validation_status_display',
        store=True,
        help='Hiển thị số người đã validate (ví dụ: 1/2)'
    )
    
    last_validation_date = fields.Datetime(
        string='Ngày Validate',
        compute='_compute_last_validation_date',
        store=True,
        help='Ngày validate gần nhất'
    )
    
    @api.depends('review_ids', 'review_ids.status', 'review_ids.reviewed_date')
    def _compute_validation_status_display(self):
        """Tính toán trạng thái validate hiển thị"""
        for record in self:
            if record.review_ids:
                # Đếm số review đã được approve
                approved_count = len(record.review_ids.filtered(lambda r: r.status == 'approved'))
                # Tổng số review
                total_count = len(record.review_ids)
                record.validation_status_display = f"{approved_count}/{total_count}"
            else:
                record.validation_status_display = "0/0"
    
    @api.depends('review_ids', 'review_ids.reviewed_date')
    def _compute_last_validation_date(self):
        """Tính toán ngày validate gần nhất"""
        for record in self:
            if record.review_ids:
                # Lấy ngày review gần nhất (có reviewed_date)
                reviewed_reviews = record.review_ids.filtered(lambda r: r.reviewed_date)
                if reviewed_reviews:
                    # Sắp xếp theo reviewed_date giảm dần và lấy ngày gần nhất
                    latest_review = max(reviewed_reviews, key=lambda r: r.reviewed_date)
                    record.last_validation_date = latest_review.reviewed_date
                else:
                    record.last_validation_date = False
            else:
                record.last_validation_date = False