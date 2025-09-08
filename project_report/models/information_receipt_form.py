# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta


class InformationReceiptForm(models.Model):
    _name = 'information.receipt.form'
    _description = 'Information Receipt Form'
    _order = 'date desc, id desc'
    _rec_name = 'display_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _check_company_auto = True

    name = fields.Char(
        string='Form Name', 
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
    
    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        tracking=True,
        domain="[('is_company', '=', True)]"
    )
    address = fields.Text(
        string='Execution Address',
        tracking=True,
        help="Address where the contract/information request will be executed"
    )
    request_contract_number = fields.Char(
        string='Request/Contract Number',
        tracking=True
    )
    product_name = fields.Many2one(
        'product.product',
        string='Product Name',
        tracking=True,
        domain="[('company_id', 'in', [company_id, False])]"
    )
    received_information = fields.Text(
        string='Received Information',
        tracking=True
    )
    internal_processing_datetime = fields.Datetime(
        string='Internal Processing Time',
        tracking=True,
        help="Date and time when internal processing is completed (can be planned for future)"
    )
    response_delivery_datetime = fields.Datetime(
        string='Response/Delivery Time to Customer',
        tracking=True,
        help="Date and time when response is delivered to customer (can be planned for future)"
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

    @api.depends('name', 'employee_id', 'date', 'customer_id')
    def _compute_display_name(self):
        for record in self:
            if record.name and record.name != 'New':
                record.display_name = record.name
            else:
                record.display_name = f"{record.customer_id.name or 'Customer'} - {record.product_name.name if record.product_name else 'Product'} - {record.date}"

    def _build_default_name(self, vals):
        """Build default name as: Customer - Product - Date"""
        customer_name = None
        product_name = None
        date_str = None

        if vals.get('customer_id'):
            customer = self.env['res.partner'].browse(vals['customer_id'])
            customer_name = customer.name
        if vals.get('product_name'):
            product = self.env['product.product'].browse(vals['product_name'])
            product_name = product.name
        if vals.get('date'):
            date_str = vals['date']

        parts = [p for p in [customer_name, product_name, date_str] if p]
        return ' - '.join(parts) if parts else _('New')

    @api.model
    def create(self, vals):
        if not vals.get('employee_id') and self.env.user.employee_id:
            vals['employee_id'] = self.env.user.employee_id.id
        if not vals.get('name') or vals.get('name') == _('New'):
            vals['name'] = self._build_default_name(vals)
        record = super(InformationReceiptForm, self).create(vals)
        record.message_post(body=_('Information Receipt Form created'))
        return record

    def write(self, vals):
        # Check if user can edit approved forms
        for record in self:
            if record.state == 'approved':
                # Only managers can edit approved forms
                if not self.env.user.has_group('hr_timesheet.group_hr_timesheet_approver'):
                    raise UserError(_('You cannot edit approved forms. Only managers can modify approved forms.'))
        result = super(InformationReceiptForm, self).write(vals)
        self.message_post(body=_('Information Receipt Form updated'))
        return result

    @api.constrains('date')
    def _check_date(self):
        for record in self:
            if record.date > fields.Date.context_today(self):
                raise ValidationError(_('Report date cannot be in the future.'))

    @api.constrains('internal_processing_datetime', 'response_delivery_datetime')
    def _check_processing_times(self):
        for record in self:
            if record.internal_processing_datetime and record.response_delivery_datetime:
                if record.internal_processing_datetime > record.response_delivery_datetime:
                    raise ValidationError(_('Internal Processing Time cannot be later than Response/Delivery Time.'))
            # Allow future dates for planning purposes
            # Removed validation for future dates

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id and self.employee_id.company_id:
            self.company_id = self.employee_id.company_id

    @api.onchange('customer_id')
    def _onchange_customer_id(self):
        pass

    def action_submit(self):
        """Submit the form for approval"""
        for record in self:
            if record.state != 'draft':
                raise UserError(_('Only draft forms can be submitted.'))
            record.write({'state': 'submitted'})
            record.message_post(body=_('Information Receipt Form submitted for approval'))

    def action_approve(self):
        """Approve the form"""
        for record in self:
            if record.state != 'submitted':
                raise UserError(_('Only submitted forms can be approved.'))
            record.write({
                'state': 'approved',
                'approved_by': self.env.user.id,
                'approved_date': fields.Datetime.now(),
            })
            record.message_post(body=_('Information Receipt Form approved by %s') % self.env.user.name)

    def action_reject(self):
        """Reject the form"""
        for record in self:
            if record.state != 'submitted':
                raise UserError(_('Only submitted forms can be rejected.'))
            return {
                'type': 'ir.actions.act_window',
                'name': _('Reject Information Receipt Form'),
                'res_model': 'information.receipt.form.reject.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {'default_form_id': record.id}
            }

    def action_reset_to_draft(self):
        """Reset form to draft"""
        for record in self:
            record.write({
                'state': 'draft',
                'approved_by': False,
                'approved_date': False,
                'rejection_reason': False,
            })
            record.message_post(body=_('Information Receipt Form reset to draft'))


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
