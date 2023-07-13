# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from odoo.exceptions import ValidationError


class AdmonSummaryReportWizard(models.TransientModel):
    _name = 'admon.summary.report.wizard'

    date_start = fields.Date(string='Start Date', required=True, default=fields.Date.today())
    date_end = fields.Date(string= 'End Date', required=True, default=fields.Date.today())
    operating_unit_id = fields.Many2one(
        'operating.unit',
        'Sucursal',
        default=lambda self: self.env['res.users'],
        required=True
        )
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        default=lambda self: self.env.user.company_id.currency_id)

    @api.onchange('date_start')
    def _onchange_date_start(self):
        if self.date_start and self.date_end and self.date_end < self.date_start:
            self.date_end = self.date_start

    @api.onchange('date_end')
    def _onchange_date_end(self):
        if self.date_end and self.date_end < self.date_start:
            self.date_start = self.date_end

    @api.multi
    def print_report(self):
        """
        data
        """
        data = {
            'model': self._name,
            'ids': self.ids,
            'currency_id': self.currency_id,
            'form': {
                'date_start': self.date_start, 
                'date_end': self.date_end,
                'operating_unit_id': self.operating_unit_id.id
            },
        }
        return self.env.ref('chickengo_admin_report.admon_summary_report').report_action(
            self, data=data)


class ReportAdmonSummaryReportView(models.AbstractModel):
    """
        Abstract Model specially for report template.
        _name = Use prefix `report.` along with `module_name.report_name`
    """
    _name = 'report.chickengo_admin_report.admon_summary_report_view'

    @api.multi
    def _get_report_values(self, docids, data=None):
        date_start = (data['form']['date_start'])
        date_end = (data['form']['date_end'])
        operating_unit_id = (data['form']['operating_unit_id'])
        
        start_date = datetime.strptime(date_start, '%Y-%m-%d')
        end_date = datetime.strptime(date_end, '%Y-%m-%d')
        docs = []
        total_orders = 0
        total_sales = 0
        other_expense = 0
        taxes = 0
        services = 0
        bank_comission = 0
        ads = 0
        loans = 0
        payroll = 0
        total_purchase = 0
        
        if start_date < end_date:
            orders = self.env['pos.order'].search([
                ('state', 'in', ['paid', 'done', 'invoiced']),
                ('date_order', '>=', start_date.strftime(DATETIME_FORMAT)),
                ('date_order', '<', end_date.strftime(DATETIME_FORMAT)),
                ('operating_unit_id', '=', operating_unit_id)
            ])
            sos = len(orders)
            sales = sum(order.amount_total for order in orders)
            total_orders += sos
            total_sales += sales
            purchases = self.env['account.invoice'].search([
                ('date_invoice', '>=', start_date.strftime(DATETIME_FORMAT)),
                ('date_invoice', '<', end_date.strftime(DATETIME_FORMAT)),
                ('state', 'in', ['open', 'paid']),
                ('type', '=', 'in_invoice'),
                ('journal_id', 'in', [2, 23]),
                ('operating_unit_id', '=', operating_unit_id)
                ])
            purchase = sum(purc.amount_total for purc in purchases)
            total_purchase += purchase
            
            invoices = self.env['account.invoice'].search([
                ('date_invoice', '>=', start_date.strftime(DATETIME_FORMAT)),
                ('date_invoice', '<', end_date.strftime(DATETIME_FORMAT)),
                ('state', 'in', ['open', 'paid']), ('type', '=', 'in_invoice'),
                ('journal_id', 'not in', [2, 23]),
                ('operating_unit_id', '=', operating_unit_id)
                ])
            
            for inv in invoices:
                if inv.partner_id.category_id:
                    if inv.partner_id.category_id.name == 'IMPUESTOS':
                        taxes += inv.amount_total
                    elif inv.partner_id.category_id.name == 'COMISION BANCO':
                        bank_comission += inv.amount_total
                    elif inv.partner_id.category_id.name == 'NOMINA':
                        payroll += inv.amount_total
                    elif inv.partner_id.category_id.name == 'SERVICIOS':
                        services += inv.amount_total
                    elif inv.partner_id.category_id.name == 'PUBLICIDAD':
                        ads += inv.amount_total
                    elif inv.partner_id.category_id.name == 'PRESTAMOS':
                        loans += inv.amount_total
                else: 
                    other_expense += inv.amount_total
            total_expenses = (
                taxes + bank_comission + payroll +
                services + ads + loans + other_expense +
                total_purchase)
            docs.append({
                'total_orders': total_orders,
                'total_sales': total_sales,
                'taxes': taxes,
                'payroll': payroll,
                'total_purchase': total_purchase,
                'services': services,
                'ads': ads,
                'bank_comission': bank_comission,
                'loans': loans,
                'utility': (total_sales - total_expenses),
                'p_utility': (((total_sales - total_expenses) * 100) / total_sales) if 'p_utiity' else 0,
                'p_ref': (((total_sales / total_purchase) * 100) - 100),
                'other_expense': other_expense,
                'prom': (total_sales / total_orders if total_orders != 0 else False),
                'currency_id': self.env.user.company_id.currency_id,
                'company': self.env.user.company_id
            })

            docargs = {
                'date_start': data['form']['date_start'],
                'date_end': data['form']['date_end'],
                'doc_ids': data['ids'],
                'doc_model': data['model'],
                'docs': docs,
            }
        return docargs
