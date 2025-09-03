from odoo import api, fields, models

class TierValidationException(models.Model):
    _inherit = "tier.validation.exception"
    
    @api.model
    def _get_tier_validation_model_names(self):
        res = super()._get_tier_validation_model_names()
        if "purchase.request" not in res:
            res.append("purchase.request")
        return res
