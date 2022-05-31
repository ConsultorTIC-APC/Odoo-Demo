# -*- coding: utf-8 -*-
# Copyright (c) 2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
import logging
_logging = logging.getLogger(__name__)

TYPE2JOURNAL = {'out_invoice':'sale', 
 'in_invoice':'purchase',  'out_refund':'sale', 
 'in_refund':'purchase'}

class AccountMove(models.Model):
	_inherit = "account.move"

	branch_id = fields.Many2one('res.branch', string='Sucursal', default=lambda self: self.env.branch.id or self.env.company.default_branch_id.id)
	pe_branch_code = fields.Char("Codigo Sucursal", related="branch_id.code", store=True)
	auto_branch = fields.Boolean(string="Auto sucursal", help="asignar sucursal segun cambio de diario")

	def obtener_datos_entidad_emisora(self):
		invoice_id = self
		datos = {
			'comercial_name': invoice_id.branch_id.name.strip() or invoice_id.company_id.partner_id.commercial_name.strip() or '-',
			'legal_name': invoice_id.company_id.partner_id.legal_name.strip() or '-',
			'pe_branch_code': invoice_id.pe_branch_code or '0000',
		}
		if invoice_id.branch_id.city_id:
			datos['province_id'] = invoice_id.branch_id.city_id.name.strip()
		else:
			datos['province_id'] = invoice_id.company_id.partner_id.city_id.name.strip()

		if invoice_id.branch_id.state_id:
			datos['state_id'] = invoice_id.branch_id.state_id.name
		else:
			datos['state_id'] = invoice_id.company_id.partner_id.state_id.name

		if invoice_id.branch_id.l10n_pe_district:
			datos['district_id'] = invoice_id.branch_id.l10n_pe_district.name
			datos['ubigeo'] = invoice_id.branch_id.l10n_pe_district.code
		else:
			datos['district_id'] = invoice_id.company_id.partner_id.l10n_pe_district.name
			datos['ubigeo'] = invoice_id.company_id.partner_id.l10n_pe_district.code

		if invoice_id.branch_id.street:
			datos['street_id'] = invoice_id.branch_id.street
		else:
			datos['street_id'] = invoice_id.company_id.partner_id.street

		if invoice_id.branch_id.country_id:
			datos['country_code'] = invoice_id.branch_id.country_id.code
		else:
			datos['country_code'] = invoice_id.company_id.partner_id.country_id.code
		return datos

	@api.onchange('journal_id', 'auto_branch')
	def _onchange_diario(self):
		if self.auto_branch and self.journal_id.branch_id:
			self.branch_id = self.journal_id.branch_id.id


	@api.depends('l10n_latam_available_document_type_ids', 'debit_origin_id', 'branch_id')
	def _compute_l10n_latam_document_type(self):
		debit_note = self.debit_origin_id
		for rec in self.filtered(lambda x: x.state == 'draft'):
			document_types = rec.l10n_latam_available_document_type_ids._origin
			document_types = debit_note and document_types.filtered(lambda x: x.internal_type == 'debit_note') or document_types
			tipo_doc = self.obtener_tipo_documento()
			if not tipo_doc:
				rec.l10n_latam_document_type_id = False
			else:
				rec.l10n_latam_document_type_id = tipo_doc.id

	def _get_l10n_latam_documents_domain(self):
		self.ensure_one()
		if self.move_type in ['out_refund', 'in_refund']:
			internal_types = ['credit_note']
		else:
			internal_types = ['debit_note', 'invoice']
		
		if self.branch_id:
			return [('internal_type', 'in', internal_types), ('country_id', '=', self.company_id.country_id.id), ('company_id', '=', self.company_id.id), ('branch_id', '=', self.branch_id.id)]
		else:
			return [('internal_type', 'in', internal_types), ('country_id', '=', self.company_id.country_id.id), ('company_id', '=', self.company_id.id)]

	@api.depends('journal_id', 'partner_id', 'company_id', 'move_type', 'branch_id')
	def _compute_l10n_latam_available_document_types(self):
		self.l10n_latam_available_document_type_ids = False
		for rec in self.filtered(lambda x: x.journal_id and x.l10n_latam_use_documents and x.partner_id):
			rec.l10n_latam_available_document_type_ids = self.env['l10n_latam.document.type'].search(rec._get_l10n_latam_documents_domain())
		#self._onchange_partner_id()

	@api.onchange('partner_id', 'company_id', 'branch_id')
	def _onchange_partner_id(self):
		res = super(AccountMove, self)._onchange_partner_id()
		if not self.move_type or self.move_type not in TYPE2JOURNAL:
			return

		if not self.branch_id:
			return
		journal_type = TYPE2JOURNAL[self.move_type]
		tipo_documento = self.env['l10n_latam.document.type']
		if not all((self.partner_id, self.env.context.get('force_pe_journal'))):
			return res

		partner_id = self.partner_id.parent_id or self.partner_id
		doc_type = partner_id.doc_type
		tipo_doc_id = False
		if not doc_type:
			return res
		if doc_type in '6':
			if not self.env.context.get('is_pos_invoice'):
				if self.l10n_latam_document_type_id.code != '01':
					tipo_doc_id = tipo_documento.search([('code', '=', '01'), ('sub_type', '=', journal_type), ('branch_id', '=', self.branch_id.id)], limit=1)
					if tipo_doc_id:
						self.l10n_latam_document_type_id = tipo_doc_id.id
						return res
		if doc_type in ('6', ):
			tipo_doc_id = tipo_documento.search([('code', '=', '01'), ('sub_type', '=', journal_type), ('branch_id', '=', self.branch_id.id)], limit=1)
		else:
			if self.l10n_latam_document_type_id.code != '03':
				tipo_doc_id = tipo_documento.search([('code', '=', '03'), ('sub_type', '=', journal_type), ('branch_id', '=', self.branch_id.id)], limit=1)
		
		if tipo_doc_id:
			self.l10n_latam_document_type_id = tipo_doc_id.id
		return res

	def obtener_tipo_documento(self):
		if not self.move_type or self.move_type not in TYPE2JOURNAL:
			return False

		if not self.branch_id:
			return False
		journal_type = TYPE2JOURNAL[self.move_type]
		tipo_documento = self.env['l10n_latam.document.type']

		partner_id = self.partner_id.parent_id or self.partner_id
		doc_type = partner_id.doc_type
		tipo_doc_id = False
		if not doc_type:
			return tipo_doc_id
		if doc_type in '6':
			if not self.env.context.get('is_pos_invoice'):
				tipo_doc_id = tipo_documento.search([('code', '=', '01'), ('sub_type', '=', journal_type), ('branch_id', '=', self.branch_id.id)], limit=1)
				if tipo_doc_id:
					return tipo_doc_id
		if doc_type in ('6', ):
			tipo_doc_id = tipo_documento.search([('code', '=', '01'), ('sub_type', '=', journal_type), ('branch_id', '=', self.branch_id.id)], limit=1)
		else:
			tipo_doc_id = tipo_documento.search([('code', '=', '03'), ('sub_type', '=', journal_type), ('branch_id', '=', self.branch_id.id)], limit=1)
		
		return tipo_doc_id

	
class AccountMoveLine(models.Model):
	_inherit = "account.move.line"

	branch_id = fields.Many2one(related='move_id.branch_id', store=True, readonly=True)

class L10nLatamDocumentType(models.Model):
	_inherit = 'l10n_latam.document.type'

	branch_id = fields.Many2one('res.branch', string='Sucursal', default=lambda self: self.env.branch.id or self.env.company.default_branch_id.id)

	@api.constrains('branch_id', 'company_id')
	def _check_branch_id(self):
		for obj in self:
			if obj.branch_id and not obj.company_id:
				raise ValidationError(_('Comapny is required with Sucursal.'))
			if obj.branch_id and obj.branch_id not in obj.company_id.branch_ids:
				raise ValidationError(_('Sucursal should belongs to the selected Company.'))