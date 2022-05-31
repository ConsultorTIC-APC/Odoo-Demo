# -*- coding: utf-8 -*-
# Copyright (c) 2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from odoo import api, fields, models, tools, _
import base64
import os
import re
from odoo.exceptions import ValidationError, UserError

class ResSucursal(models.Model):
	_name = "res.branch"
	_description = "Sucursales"
	_order = 'name'

	def _get_logo(self):
		return base64.b64encode(open(os.path.join(tools.config['root_path'], 'addons', 'base', 'static', 'img', 'res_company_logo.png'), 'rb') .read())

	@api.model
	def _get_user_currency(self):
		return self.env['res.currency.rate'].search([('rate', '=', 1)], limit=1).currency_id

	name = fields.Char(string="Nombre", required=True)
	company_id = fields.Many2one('res.company', string='Empresa', required=True, default=lambda self: self.env.company)
	currency_id = fields.Many2one('res.currency', string='Moneda', required=True, default=lambda self: self._get_user_currency())
	partner_id = fields.Many2one('res.partner', string='Socio', required=True, related="company_id.partner_id")
	user_ids = fields.Many2many('res.users', 'res_branch_users_rel', 'bid', 'user_id', string='Usuarios aceptados')
	logo = fields.Binary(default=_get_logo, string="Logo de Sucursal",)
	street = fields.Char()
	street2 = fields.Char()
	zip = fields.Char()
	country_id = fields.Many2one('res.country', string="Country")
	state_id = fields.Many2one('res.country.state', string="Fed. State")
	city_id = fields.Many2one('res.city', string='City of Address')
	l10n_pe_district = fields.Many2one(
		'l10n_pe.res.city.district', string='District',
		help='Districts are part of a province or city.')
	email = fields.Char(string="E-mail")
	phone = fields.Char(string="Telefono")
	code = fields.Char("Código", default="0000", required=True)

	_sql_constraints = [
		('name_uniq', 'unique (company_id, name)', 'El nombre de la sucursal debe ser único !'),
		('name_uniq_branch', 'unique (company_id, code)', 'El código de la sucursal debe ser único !')
	]

	@api.onchange('l10n_pe_district')
	def _onchange_district_id(self):
		if self.l10n_pe_district:
			self.zip = self.l10n_pe_district.code
			if not self.city_id:
				self.city_id = self.l10n_pe_district.city_id.id

	@api.onchange('city_id')
	def _onchange_province_id(self):
		if self.city_id:
			return {'domain': {'l10n_pe_district': [('city_id', '=', self.city_id.id)]}}
		else:
			return {'domain': {'l10n_pe_district': []}}

	@api.onchange('state_id')
	def _onchange_state_id(self):
		if self.state_id:
			return {'domain': {'city_id': [('state_id', '=', self.state_id.id)]}}
		else:
			return {'domain': {'city_id': []}}

	def on_change_country(self, country_id):
		# This function is called from account/models/chart_template.py, hence decorated with `multi`.
		self.ensure_one()
		currency_id = self._get_user_currency()
		if country_id:
			currency_id = self.env['res.country'].browse(country_id).currency_id
		return {'value': {'currency_id': currency_id.id}}

	@api.onchange('country_id')
	def _onchange_country_id_wrapper(self):
		res = {'domain': {'state_id': []}}
		if self.country_id:
			res['domain']['state_id'] = [('country_id', '=', self.country_id.id)]
		values = self.on_change_country(self.country_id.id)['value']
		for fname, value in values.items():
			setattr(self, fname, value)
		return res

	def copy(self, default=None):
		raise UserError(_('No se permite duplicar una sucursal. En su lugar, cree una nueva sucursal.'))

	@api.model
	def create(self, vals):
		branch = super(ResSucursal, self).create(vals)
		# The write is made on the user to set it automatically in the multi branch group.
		if branch.company_id in self.env.user.company_ids:
			self.env.user.write({'branch_ids': [(4, branch.id)]})
		return branch
