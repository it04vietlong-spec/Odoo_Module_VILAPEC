# -*- coding: utf-8 -*-
{
    'name': 'Daily Report',
    'version': '18.0.1.0.12',
    'category': 'Project/Project',
    'summary': 'Simple daily reporting with timesheet integration',
    'description': """
        Daily Report Module
        =================================
        
        This module provides simple daily reporting functionality:
        
        * Employee time tracking per project
        * Daily progress monitoring
        * Company-wide reporting
        * Timesheet integration
        * Advanced analytics and reporting
        * Approval workflow
        * Multi-company support
    """,
    'author': 'VILAPEC',
    'website': 'https://www.vilapec.com',
    'depends': [
        'base',
        'hr',
        'project',
        'hr_timesheet',
        'product',
        'web',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/project_report_data.xml',
        'views/project_report_views.xml',
        'views/contract_performance_report_views.xml',
        'views/information_receipt_form_views.xml',
        'wizard/project_report_wizard_views.xml',
        'wizard/contract_performance_report_wizard_views.xml',
        'wizard/information_receipt_form_wizard_views.xml',
        'reports/report_actions.xml',
        'reports/report_daily_report.xml',
        'reports/report_contract_performance.xml',
        'reports/report_information_receipt.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'project_report/static/src/js/project_report.js',
            'project_report/static/src/css/project_report.css',
            'project_report/static/src/xml/project_report.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
    'post_init_hook': 'post_init_hook',
}
