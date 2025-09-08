# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class InformationReceiptFormRejectWizard(models.TransientModel):
    _name = 'information.receipt.form.reject.wizard'
    _description = 'Information Receipt Form Rejection Wizard'

    form_id = fields.Many2one('information.receipt.form', string='Form', required=True)
    rejection_reason = fields.Text(string='Rejection Reason', required=True)

    def action_reject(self):
        """Reject the form with reason"""
        self.ensure_one()
        self.form_id.write({
            'state': 'rejected',
            'rejection_reason': self.rejection_reason,
        })
        self.form_id.message_post(body=_('Information Receipt Form rejected: %s') % self.rejection_reason)
        return {'type': 'ir.actions.act_window_close'}
