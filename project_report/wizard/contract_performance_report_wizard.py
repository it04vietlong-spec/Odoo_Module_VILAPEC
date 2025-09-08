# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ContractPerformanceReportRejectWizard(models.TransientModel):
    _name = 'contract.performance.report.reject.wizard'
    _description = 'Contract Performance Report Rejection Wizard'

    report_id = fields.Many2one('contract.performance.report', string='Report', required=True)
    rejection_reason = fields.Text(string='Rejection Reason', required=True)

    def action_reject(self):
        """Reject the report with reason"""
        self.ensure_one()
        self.report_id.write({
            'state': 'rejected',
            'rejection_reason': self.rejection_reason,
        })
        self.report_id.message_post(body=_('Contract Performance Report rejected: %s') % self.rejection_reason)
        return {'type': 'ir.actions.act_window_close'}
