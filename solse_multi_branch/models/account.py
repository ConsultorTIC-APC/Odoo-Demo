# -*- coding: utf-8 -*-
# Copyright (c) 2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
import logging
_logging = logging.getLogger(__name__)

class AccountJournalGroup(models.Model):
	_inherit = 'account.journal.group'

	branch_id = fields.Many2one('res.branch', default=lambda self: self.env.branch.id or self.env.company.default_branch_id.id)

	@api.constrains('branch_id', 'company_id')
	def _check_branch_id(self):
		for obj in self:
			if obj.branch_id and not obj.company_id:
				raise ValidationError(_('Comapny is required with Sucursal.'))
			if obj.branch_id and obj.branch_id not in obj.company_id.branch_ids:
				raise ValidationError(_('Sucursal should belongs to the selected Company.'))

class AccountJournal(models.Model):
	_inherit = "account.journal"

	branch_id = fields.Many2one('res.branch', string='Sucursal', index=True, default=lambda self: self.env.branch.id or self.env.company.default_branch_id.id, help="Sucursal related to this journal")

	@api.constrains('branch_id', 'company_id')
	def _check_branch_id(self):
		for obj in self:
			if obj.branch_id and not obj.company_id:
				raise ValidationError(_('Comapny is required with Sucursal.'))
			if obj.branch_id and obj.branch_id not in obj.company_id.branch_ids:
				raise ValidationError(_('Sucursal should belongs to the selected Company.'))

class account_payment(models.Model):
	_inherit = "account.payment"

	branch_id = fields.Many2one('res.branch', related='journal_id.branch_id', string='Sucursal', readonly=True)

class PaymentAcquirer(models.Model):
	_inherit = "payment.acquirer"

	branch_id = fields.Many2one('res.branch', 'Sucursal', default=lambda self: self.env.branch.id or self.env.company.default_branch_id.id)

	@api.constrains('branch_id', 'company_id')
	def _check_branch_id(self):
		for obj in self:
			if obj.branch_id and not obj.company_id:
				raise ValidationError(_('Comapny is required with Sucursal.'))
			if obj.branch_id and obj.branch_id not in obj.company_id.branch_ids:
				raise ValidationError(_('Sucursal should belongs to the selected Company.'))

class AccountPaymentTerm(models.Model):
	_inherit = "account.payment.term"

	branch_id = fields.Many2one('res.branch', string='Sucursal')

class AccountBankStatement(models.Model):
	_inherit = "account.bank.statement"

	branch_id = fields.Many2one('res.branch', related='journal_id.branch_id', string='Sucursal', store=True, readonly=True, default=lambda self: self.env.branch.id or self.env.company.default_branch_id.id)

class AccountBankStatementLine(models.Model):
	_inherit = "account.bank.statement.line"

	branch_id = fields.Many2one('res.branch', related='statement_id.branch_id', string='Sucursal', store=True, readonly=True)


"""
class AccountAccount(models.Model):
	_inherit = "account.account"

	branch_id = fields.Many2one('res.branch', string='Sucursal', default=lambda self: self.env.branch.id or self.env.company.default_branch_id.id)

class AccountRoot(models.Model):
	_inherit = 'account.root'

	branch_id = fields.Many2one('res.branch')

	def init(self):
		tools.drop_view_if_exists(self.env.cr, self._table)
		self.env.cr.execute('''
			CREATE OR REPLACE VIEW %s AS (
			SELECT DISTINCT ASCII(code) * 1000 + ASCII(SUBSTRING(code,2,1)) AS id,
				   LEFT(code,2) AS name,
				   ASCII(code) AS parent_id,
				   company_id,
				   branch_id
			FROM account_account WHERE code IS NOT NULL
			UNION ALL
			SELECT DISTINCT ASCII(code) AS id,
				   LEFT(code,1) AS name,
				   NULL::int AS parent_id,
				   company_id,
				   branch_id
			FROM account_account WHERE code IS NOT NULL
			)''' % (self._table,)
		)
"""

class AccountTax(models.Model):
	_inherit = 'account.tax'

	branch_id = fields.Many2one('res.branch', string='Sucursal', default=lambda self: self.env.branch.id or self.env.company.default_branch_id.id)

	@api.constrains('branch_id', 'company_id')
	def _check_branch_id(self):
		for obj in self:
			if obj.branch_id and not obj.company_id:
				raise ValidationError(_('Comapny is required with Sucursal.'))
			if obj.branch_id and obj.branch_id not in obj.company_id.branch_ids:
				raise ValidationError(_('Sucursal should belongs to the selected Company.'))

class AccountTaxRepartitionLine(models.Model):
	_inherit = "account.tax.repartition.line"

	branch_id = fields.Many2one(string="Sucursal", comodel_name='res.branch', default=lambda self: self.env.branch.id or self.env.company.default_branch_id.id, help="The branch this repartition line belongs to.")

class AccountFiscalPosition(models.Model):
	_inherit = 'account.fiscal.position'

	branch_id = fields.Many2one('res.branch', string='Sucursal', default=lambda self: self.env.branch.id or self.env.company.default_branch_id.id)

	@api.constrains('branch_id', 'company_id')
	def _check_branch_id(self):
		for obj in self:
			if obj.branch_id and not obj.company_id:
				raise ValidationError(_('Comapny is required with Sucursal.'))
			if obj.branch_id and obj.branch_id not in obj.company_id.branch_ids:
				raise ValidationError(_('Sucursal should belongs to the selected Company.'))


class AccountReconcileModel(models.Model):
	_inherit = 'account.reconcile.model'

	branch_id = fields.Many2one('res.branch', string='Sucursal', default=lambda self: self.env.branch.id or self.env.company.default_branch_id.id)

	@api.constrains('branch_id', 'company_id')
	def _check_branch_id(self):
		for obj in self:
			if obj.branch_id and not obj.company_id:
				raise ValidationError(_('Comapny is required with Sucursal.'))
			if obj.branch_id and obj.branch_id not in obj.company_id.branch_ids:
				raise ValidationError(_('Sucursal should belongs to the selected Company.'))

class AccountInvoiceReport(models.Model):
	_inherit = "account.invoice.report"

	branch_id = fields.Many2one('res.branch', string='Sucursal', readonly=True)

	def _select(self):
		return super(AccountInvoiceReport, self)._select() + ", move.branch_id as branch_id"

	def _group_by(self):
		return super(AccountInvoiceReport, self)._group_by() + ", move.branch_id"



