from odoo import models, fields, _
from odoo.exceptions import UserError


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    account_move_id = fields.Many2one(
        'account.move', string='Factura de proveedor')

    def action_generate_invoice(self):
        invoice_data = {
            'currency_id': self.currency_id.id,
            'invoice_user_id': self.env.user.id,
            'move_type': 'in_invoice',
            'ref': self.reference,
            'invoice_line_ids':  [(0, 0, {
                'name': self.product_id.name,
                'product_id': self.product_id.id,
                'product_uom_id': self.product_id.uom_id.id,
                'quantity': self.quantity,
                'price_unit': self.unit_amount,
                'tax_ids': [(6, 0, self.tax_ids.ids)],
                'account_id': self.account_id.id
            })],
        }
        invoice_id = self.env['account.move'].create(invoice_data)
        # invoice_id._onchange_product_id()
        invoice_id._onchange_invoice_line_ids()
        """
        for line in invoice_id.line_ids:
            if not line.product_id or line.display_type in ('line_section', 'line_note'):
                continue
            line.name = line._get_computed_name()
            taxes = line._get_computed_taxes()
            if taxes and line.move_id.fiscal_position_id:
                taxes = line.move_id.fiscal_position_id.map_tax(
                    taxes, partner=line.partner_id)
            line.tax_ids = taxes
            line.product_uom_id = line._get_computed_uom()
        """
        invoice_id.invoice_line_ids._onchange_account_id()

        # invoice_id.line_ids._onchange_balance()
        invoice_id.invoice_line_ids._onchange_price_subtotal()
        # invoice_id.invoice_line_ids._onchange_mark_recompute_taxes()

        # invoice_id._onchange_recompute_dynamic_lines()
        self.account_move_id = invoice_id

    def _get_expense_account_source(self):
        self.ensure_one()
        if self.account_move_id.partner_id.property_account_payable_id:
            account = self.account_move_id.partner_id.property_account_payable_id
        elif self.account_id:
            account = self.account_id
        elif self.product_id:
            account = self.product_id.product_tmpl_id.with_company(
                self.company_id)._get_product_accounts()['expense']
            if not account:
                raise UserError(
                    _("No Expense account found for the product %s (or for its category), please configure one.") % (self.product_id.name))
        else:
            account = self.env['ir.property'].with_company(self.company_id)._get(
                'property_account_expense_categ_id', 'product.category')
            if not account:
                raise UserError(
                    _('Please configure Default Expense account for Product expense: `property_account_expense_categ_id`.'))
        return account

    def _get_account_move_line_values(self):
        move_line_values_by_expense = {}
        for expense in self:
            move_line_name = expense.employee_id.name + \
                ': ' + expense.name.split('\n')[0][:64]
            account_src = expense._get_expense_account_source()
            account_dst = expense._get_expense_account_destination()
            account_date = expense.sheet_id.accounting_date or expense.date or fields.Date.context_today(
                expense)

            company_currency = expense.company_id.currency_id

            move_line_values = []
            taxes = expense.tax_ids.with_context(round=True).compute_all(
                expense.unit_amount, expense.currency_id, expense.quantity, expense.product_id)
            total_amount = 0.0
            total_amount_currency = 0.0
            partner_dst_id = expense.employee_id.sudo().address_home_id.commercial_partner_id
            partner_src_id = expense.account_move_id.partner_id
            # source move line
            balance = expense.currency_id._convert(
                taxes['total_excluded'], company_currency, expense.company_id, account_date)
            amount_currency = taxes['total_excluded']
            move_line_src = {
                'name': move_line_name,
                'quantity': expense.quantity or 1,
                'debit': balance if balance > 0 else 0,
                'credit': -balance if balance < 0 else 0,
                'amount_currency': amount_currency,
                'account_id': account_src.id,
                'product_id': expense.product_id.id,
                'product_uom_id': expense.product_uom_id.id,
                'analytic_account_id': expense.analytic_account_id.id,
                'analytic_tag_ids': [(6, 0, expense.analytic_tag_ids.ids)],
                'expense_id': expense.id,
                'partner_id': partner_src_id.id,
                'tax_ids': [(6, 0, expense.tax_ids.ids)],
                'tax_tag_ids': [(6, 0, taxes['base_tags'])],
                'currency_id': expense.currency_id.id,
                'partner_invoice_id': expense.account_move_id.id,
            }
            move_line_values.append(move_line_src)
            total_amount -= balance
            total_amount_currency -= move_line_src['amount_currency']

            # taxes move lines
            for tax in taxes['taxes']:
                balance = expense.currency_id._convert(
                    tax['amount'], company_currency, expense.company_id, account_date)
                amount_currency = tax['amount']

                if tax['tax_repartition_line_id']:
                    rep_ln = self.env['account.tax.repartition.line'].browse(
                        tax['tax_repartition_line_id'])
                    base_amount = self.env['account.move']._get_base_amount_to_display(
                        tax['base'], rep_ln)
                else:
                    base_amount = None

                move_line_tax_values = {
                    'name': tax['name'],
                    'quantity': 1,
                    'debit': balance if balance > 0 else 0,
                    'credit': -balance if balance < 0 else 0,
                    'amount_currency': amount_currency,
                    'account_id': tax['account_id'] or move_line_src['account_id'],
                    'tax_repartition_line_id': tax['tax_repartition_line_id'],
                    'tax_tag_ids': tax['tag_ids'],
                    'tax_base_amount': base_amount,
                    'expense_id': expense.id,
                    'partner_id': partner_src_id.id,
                    'currency_id': expense.currency_id.id,
                    'analytic_account_id': expense.analytic_account_id.id if tax['analytic'] else False,
                    'analytic_tag_ids': [(6, 0, expense.analytic_tag_ids.ids)] if tax['analytic'] else False,
                }
                total_amount -= balance
                total_amount_currency -= move_line_tax_values['amount_currency']
                move_line_values.append(move_line_tax_values)

            # destination move line
            move_line_dst = {
                'name': move_line_name,
                'debit': total_amount > 0 and total_amount,
                'credit': total_amount < 0 and -total_amount,
                'account_id': account_dst,
                'date_maturity': account_date,
                'amount_currency': total_amount_currency,
                'currency_id': expense.currency_id.id,
                'expense_id': expense.id,
                'partner_id': partner_dst_id.id,
            }
            move_line_values.append(move_line_dst)

            move_line_values_by_expense[expense.id] = move_line_values
        return move_line_values_by_expense
