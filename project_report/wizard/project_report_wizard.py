# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class ProjectReportWizard(models.TransientModel):
    _name = 'project.report.wizard'
    _description = 'Daily Report Wizard'

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        default=lambda self: self.env.user.employee_id
    )
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        required=True
    )
    date_from = fields.Date(
        string='From Date',
        required=True,
        default=fields.Date.context_today
    )
    date_to = fields.Date(
        string='To Date',
        required=True,
        default=fields.Date.context_today
    )
    task_id = fields.Many2one(
        'project.task',
        string='Task',
        domain="[('project_id', '=', project_id)]"
    )

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for record in self:
            if record.date_from > record.date_to:
                raise ValidationError(_('From Date must be before To Date.'))

    def action_generate_report(self):
        """Generate daily report entries"""
        self.ensure_one()
        
        current_date = self.date_from
        reports_created = []
        
        while current_date <= self.date_to:
            existing_report = self.env['project.report'].search([
                ('employee_id', '=', self.employee_id.id),
                ('project_id', '=', self.project_id.id),
                ('date', '=', current_date)
            ])
            
            if not existing_report:
                report_vals = {
                    'employee_id': self.employee_id.id,
                    'project_id': self.project_id.id,
                    'task_id': self.task_id.id if self.task_id else False,
                    'date': current_date,
                    'company_id': self.employee_id.company_id.id,
                }
                new_report = self.env['project.report'].create(report_vals)
                reports_created.append(new_report.id)
            
            current_date += relativedelta(days=1)
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Generated Reports'),
            'res_model': 'project.report',
            'view_mode': 'list,form',
            'domain': [('id', 'in', reports_created)],
            'context': {'search_default_employee_id': self.employee_id.id}
        }
