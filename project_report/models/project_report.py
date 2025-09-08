# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta


class ProjectReport(models.Model):
    _name = 'project.report'
    _description = 'Daily Report'
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
    description = fields.Text(
        string='Description',
        help="Detailed description of the work performed"
    )

    task_content = fields.Text(string='Task Content', tracking=True)
    expected_result = fields.Text(string='Expected Result', tracking=True)
    expected_result_deadline = fields.Date(string='Expected Result Deadline', tracking=True)
    actual_result = fields.Text(string='Actual Work Result', tracking=True)
    actual_result_deadline = fields.Date(string='Actual Work Result Deadline', tracking=True)
    
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        default=lambda self: self.env.user.employee_id,
        tracking=True,
        domain="[('company_id', 'in', [company_id, False])]"
    )
    
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        required=True,
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

    @api.depends('name', 'employee_id', 'project_id', 'date')
    def _compute_display_name(self):
        for record in self:
            if record.name and record.name != 'New':
                record.display_name = record.name
            else:
                record.display_name = f"{record.employee_id.name or 'Employee'} - {record.project_id.name or 'Project'} - {record.date}"

    def _build_default_name(self, vals):
        """Build default name as: Employee - Project - Date"""
        employee_name = None
        project_name = None
        date_str = None

        if vals.get('employee_id'):
            employee_name = self.env['hr.employee'].browse(vals['employee_id']).name
        if vals.get('project_id'):
            project_name = self.env['project.project'].browse(vals['project_id']).name
        if vals.get('date'):
            date_str = vals['date']

        parts = [p for p in [employee_name, project_name, date_str] if p]
        return ' - '.join(parts) if parts else _('New')

    @api.model
    def create(self, vals):
        if not vals.get('employee_id') and self.env.user.employee_id:
            vals['employee_id'] = self.env.user.employee_id.id
        if not vals.get('name') or vals.get('name') == _('New'):
            vals['name'] = self._build_default_name(vals)
        record = super(ProjectReport, self).create(vals)
        record.message_post(body=_('Report created'))
        return record

    def write(self, vals):
        result = super(ProjectReport, self).write(vals)
        self.message_post(body=_('Report updated'))
        return result


    @api.constrains('date')
    def _check_date(self):
        for record in self:
            if record.date > fields.Date.context_today(self):
                raise ValidationError(_('Report date cannot be in the future.'))


    @api.onchange('employee_id', 'project_id', 'date')
    def _onchange_build_name(self):
        if self.state == 'draft':
            parts = [p for p in [self.employee_id.name, self.project_id.name, self.date] if p]
            self.name = ' - '.join([str(p) for p in parts]) if parts else self.name

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
            record.message_post(body=_('Report submitted for approval'))

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
            record.message_post(body=_('Report approved by %s') % self.env.user.name)

    def action_reject(self):
        """Reject the report"""
        for record in self:
            if record.state != 'submitted':
                raise UserError(_('Only submitted reports can be rejected.'))
            return {
                'type': 'ir.actions.act_window',
                'name': _('Reject Report'),
                'res_model': 'project.report.reject.wizard',
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
            record.message_post(body=_('Report reset to draft'))

    def action_view_timesheet(self):
        """View related timesheet entries"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Related Timesheets'),
            'res_model': 'account.analytic.line',
            'view_mode': 'list,form',
            'domain': [
                ('employee_id', '=', self.employee_id.id),
                ('project_id', '=', self.project_id.id),
                ('date', '=', self.date)
            ],
            'context': {'default_employee_id': self.employee_id.id, 'default_project_id': self.project_id.id}
        }

    @api.model
    def get_employee_daily_reports(self, employee_id, date):
        """Get all reports for an employee on a specific date"""
        return self.search([
            ('employee_id', '=', employee_id),
            ('date', '=', date)
        ])

    @api.model
    def get_project_reports(self, project_id, date_from=None, date_to=None):
        """Get all reports for a project within date range"""
        domain = [('project_id', '=', project_id)]
        if date_from:
            domain.append(('date', '>=', date_from))
        if date_to:
            domain.append(('date', '<=', date_to))
        return self.search(domain)


    @api.model
    def _cron_cleanup_old_drafts(self):
        """Cleanup old draft reports (older than 30 days)"""
        import logging
        _logger = logging.getLogger(__name__)
        cutoff_date = fields.Date.today() - timedelta(days=30)
        old_drafts = self.search([
            ('state', '=', 'draft'),
            ('date', '<', cutoff_date)
        ])
        if old_drafts:
            old_drafts.unlink()
            _logger.info(f"Cleaned up {len(old_drafts)} old draft reports")


def post_init_hook(env):
    """Post-installation hook (Odoo 17+ signature: env)"""
    if not env['ir.cron'].search([('name', '=', 'Daily Report: Cleanup Old Drafts')]):
        env['ir.cron'].create({
            'name': 'Daily Report: Cleanup Old Drafts',
            'model_id': env.ref('project_report.model_project_report').id,
            'state': 'code',
            'code': 'model._cron_cleanup_old_drafts()',
            'interval_number': 1,
            'interval_type': 'days',
            'nextcall': fields.Datetime.now(),
            'user_id': env.ref('base.user_root').id,
            'active': True,
        })


class ProjectReportRejectWizard(models.TransientModel):
    _name = 'project.report.reject.wizard'
    _description = 'Daily Report Rejection Wizard'

    report_id = fields.Many2one('project.report', string='Report', required=True)
    rejection_reason = fields.Text(string='Rejection Reason', required=True)
    def action_reject(self):
        """Reject the report with reason"""
        self.ensure_one()
        self.report_id.write({
            'state': 'rejected',
            'rejection_reason': self.rejection_reason,
        })
        self.report_id.message_post(body=_('Report rejected: %s') % self.rejection_reason)
        return {'type': 'ir.actions.act_window_close'}