# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta


class ContractPerformanceReport(models.Model):
    _name = 'contract.performance.report'
    _description = 'Contract Performance Report'
    _order = 'date desc, id desc'
    _rec_name = 'display_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _check_company_auto = True

    name = fields.Char(
        string='Report Name', 
        required=True, 
        default=lambda self: _('New'),
        tracking=True,
        copy=False
    )
    date = fields.Date(
        string='Date', 
        required=True, 
        default=fields.Date.context_today,
        tracking=True
    )
    
    # Contract Performance Report fields theo yêu cầu
    contract_number = fields.Char(
        string='Contract Number',
        required=True,
        tracking=True
    )
    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        tracking=True,
        domain="[('is_company', '=', True)]"
    )
    execution_location = fields.Char(
        string='Execution Location',
        tracking=True
    )
    contract_execution_datetime = fields.Datetime(
        string='Contract Execution Period',
        tracking=True
    )
    task_description = fields.Text(
        string='Task Description',
        tracking=True
    )
    according_to_plan = fields.Text(
        string='According to Plan',
        tracking=True
    )
    actual_result = fields.Text(
        string='Actual Result',
        tracking=True
    )
    assessment = fields.Text(
        string='Assessment',
        tracking=True
    )
    notes = fields.Text(
        string='Notes',
        tracking=True
    )
    
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        default=lambda self: self.env.user.employee_id,
        tracking=True,
        domain="[('company_id', 'in', [company_id, False])]"
    )
    
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        tracking=True
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft', required=True, tracking=True)
    
    display_name = fields.Char(
        string='Display Name', 
        compute='_compute_display_name', 
        store=True
    )
    
    user_id = fields.Many2one(
        'res.users',
        string='User',
        default=lambda self: self.env.user,
        required=True,
        tracking=True
    )
    
    approved_by = fields.Many2one(
        'res.users',
        string='Approved By',
        readonly=True,
        tracking=True
    )
    approved_date = fields.Datetime(
        string='Approved Date',
        readonly=True,
        tracking=True
    )
    
    rejection_reason = fields.Text(
        string='Rejection Reason',
        readonly=True
    )

    @api.depends('name', 'employee_id', 'date', 'contract_number', 'customer_id')
    def _compute_display_name(self):
        for record in self:
            if record.name and record.name != 'New':
                record.display_name = record.name
            else:
                record.display_name = f"{record.contract_number or 'Contract'} - {record.customer_id.name or 'Customer'} - {record.date}"

    def _build_default_name(self, vals):
        """Build default name as: Contract Number - Customer - Date"""
        contract_number = None
        customer_name = None
        date_str = None

        if vals.get('contract_number'):
            contract_number = vals['contract_number']
        if vals.get('customer_id'):
            customer = self.env['res.partner'].browse(vals['customer_id'])
            customer_name = customer.name
        if vals.get('date'):
            date_str = vals['date']

        parts = [p for p in [contract_number, customer_name, date_str] if p]
        return ' - '.join(parts) if parts else _('New')

    @api.model
    def create(self, vals):
        # Default employee to current user if not provided
        if not vals.get('employee_id') and self.env.user.employee_id:
            vals['employee_id'] = self.env.user.employee_id.id
        # Build a readable default name
        if not vals.get('name') or vals.get('name') == _('New'):
            vals['name'] = self._build_default_name(vals)
        record = super(ContractPerformanceReport, self).create(vals)
        record.message_post(body=_('Contract Performance Report created'))
        return record

    def write(self, vals):
        # Check if user can edit approved reports
        for record in self:
            if record.state == 'approved':
                # Only managers can edit approved reports
                if not self.env.user.has_group('hr_timesheet.group_hr_timesheet_approver'):
                    raise UserError(_('You cannot edit approved reports. Only managers can modify approved reports.'))
        result = super(ContractPerformanceReport, self).write(vals)
        # Always record who updated
        self.message_post(body=_('Contract Performance Report updated'))
        return result

    @api.constrains('date')
    def _check_date(self):
        for record in self:
            if record.date > fields.Date.context_today(self):
                raise ValidationError(_('Report date cannot be in the future.'))

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id and self.employee_id.company_id:
            self.company_id = self.employee_id.company_id

    def action_submit(self):
        """Submit the report for approval"""
        for record in self:
            if record.state != 'draft':
                raise UserError(_('Only draft reports can be submitted.'))
            record.write({'state': 'submitted'})
            record.message_post(body=_('Contract Performance Report submitted for approval'))

    def action_approve(self):
        """Approve the report"""
        for record in self:
            if record.state != 'submitted':
                raise UserError(_('Only submitted reports can be approved.'))
            record.write({
                'state': 'approved',
                'approved_by': self.env.user.id,
                'approved_date': fields.Datetime.now(),
            })
            record.message_post(body=_('Contract Performance Report approved by %s') % self.env.user.name)

    def action_reject(self):
        """Reject the report"""
        for record in self:
            if record.state != 'submitted':
                raise UserError(_('Only submitted reports can be rejected.'))
            return {
                'type': 'ir.actions.act_window',
                'name': _('Reject Contract Performance Report'),
                'res_model': 'contract.performance.report.reject.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {'default_report_id': record.id}
            }

    def action_reset_to_draft(self):
        """Reset report to draft"""
        for record in self:
            record.write({
                'state': 'draft',
                'approved_by': False,
                'approved_date': False,
                'rejection_reason': False,
            })
            record.message_post(body=_('Contract Performance Report reset to draft'))


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
