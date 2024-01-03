# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime
from odoo.tools.translate import _

class FleetMethodPayment(models.Model):
        _name = 'fleet.method.payment'
        _inherit = ['mail.thread', 'mail.activity.mixin']
        _description = 'Record Method Payment'
        
        _sql_constraints = [('number_uniq', 'unique (account_number)', 'This account number already exists!')]

        journal_id = fields.Many2one(
                'account.journal', 
                string='Journal', 
                domain="[('type', '=', 'bank'), ('l10n_do_payment_form', '=', 'card')]"
        )
        account_type = fields.Selection(string='Type', related='journal_id.type', readonly=True)
        payment_form = fields.Selection(string='Payment Form', related='journal_id.l10n_do_payment_form', readonly=True)
        account_number = fields.Char(string='Account Number', related='journal_id.bank_account_id.acc_number', readonly=True, store=True)
        bank = fields.Char(string='Bank', related='journal_id.bank_id.name', readonly=True)
        cutoff_date = fields.Integer('Cutting day', required=True, tracking=True, help='Enter the day of the month (1-31)')
        due_date = fields.Char(string='Due Date', required=True, tracking=True)
        state = fields.Selection([
                ('new', 'New'),
                ('active', 'Active'),
                ('expired', 'Expired'),
                ('cancel', 'Cancelled'),
                ], string='Status', default='new', tracking=True)
        
        def action_set_active(self):
                self.write({'state': 'active'})

        def action_set_cancel(self):
                self.write({'state': 'cancel'})
        
        def name_get(self):
                result = []

                for acc in self:                   
                        journal = acc.journal_id
                        payment_form_selection = dict(journal.fields_get(allfields=['l10n_do_payment_form'])['l10n_do_payment_form']['selection'])
                        payment_form_label = payment_form_selection.get(acc.payment_form, acc.payment_form)

                        account_number_short = acc.account_number[-6:] if acc.account_number else 'XXXXXX'

                        name = '{} - {}'.format(payment_form_label, account_number_short) if acc.payment_form else 'No Payment Form - {}'.format(account_number_short)
                        result.append((acc.id, name))

                return result
        
        @api.model
        def create(self, vals):
                try:
                        return super(FleetMethodPayment, self).create(vals)
                except ValidationError as e:
                        if "number_uniq" in e.name:
                                raise ValidationError(_("This account number already exists!"))
                        raise e

        @api.constrains('due_date')
        def _check_due_date_format(self):
                for record in self:
                        if record.due_date:
                                self._validate_date_format(record.due_date)

        @staticmethod
        def _validate_date_format(date):
                """Validate date format <MM/YYYY>"""
                if date is not None:
                        error = _('Error. Date format must be MM/YYYY')
                        if len(date) == 7:
                                try:
                                        datetime.strptime(date, '%m/%Y')
                                except ValueError:
                                        raise ValidationError(error)
                        else:
                                raise ValidationError(error)