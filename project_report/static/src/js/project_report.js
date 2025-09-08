/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";

export class ProjectReportKanbanRenderer extends Component {
    static template = "project_report.ProjectReportKanbanRenderer";
    static props = ["*"];

    get cardClass() {
        return {
            'o_kanban_card': true,
            'o_kanban_global_click': true,
            'border-primary': this.props.record.data.state === 'draft',
            'border-warning': this.props.record.data.state === 'submitted',
            'border-success': this.props.record.data.state === 'approved',
            'border-danger': this.props.record.data.state === 'rejected',
        };
    }

    get statusColor() {
        const statusColors = {
            'draft': 'text-muted',
            'submitted': 'text-warning',
            'approved': 'text-success',
            'rejected': 'text-danger',
        };
        return statusColors[this.props.record.data.state] || 'text-muted';
    }
}

registry.category("view_widgets").add("project_report_kanban", ProjectReportKanbanRenderer);
