# -*- coding: utf-8 -*-
# Copyright (c) 2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError
import logging
_logger = logging.getLogger(__name__)

class Users(models.Model):
	_inherit = "res.users"

	def _branches_count(self):
		return self.env['res.branch'].sudo().search_count([])

	def _compute_branches_count(self):
		branches_count = self._branches_count()
		for user in self:
			user.branches_count = branches_count

	branch_id = fields.Many2one('res.branch', string='Sucursal', required=True, ondelete='restrict', default=lambda self: self.env.branch.id, help='The default branch for this user.', domain="[('company_id','in',company_ids)]")
	branch_ids = fields.Many2many('res.branch', 'res_branch_users_rel', 'user_id', 'bid', string='Sucursales', ondelete='restrict', default=lambda self: self.env.branch.ids, domain="[('company_id','in',company_ids)]")
	branches_count = fields.Integer(compute='_compute_branches_count', string="Número de sucursales", default=_branches_count)

	@api.constrains('branch_id', 'branch_ids')
	def _check_branch(self):
		if any(user.branch_id and user.branch_id not in user.branch_ids for user in self):
			raise ValidationError(_('The chosen branch is not in the allowed branches for this user'))

	@api.constrains('company_ids', 'branch_ids')
	def _check_branch_cmp(self):
		for user in self:
			brch_cmp = [obj.company_id.id for obj in user.branch_ids] if user.branch_ids else []
			if any(user.company_ids and obj not in user.company_ids.ids for obj in brch_cmp):
				raise ValidationError(_('The branches are not in the allowed companies for this user'))

	@api.model
	def create(self, values):
		user = super(Users, self).create(values)
		group_multi_branch = self.env.ref('solse_multi_branch.group_multi_branch', False)
		if group_multi_branch and 'branch_ids' in values:
			if len(user.branch_ids) <= 1 and user.id in group_multi_branch.users.ids:
				user.write({'groups_id': [(3, group_multi_branch.id)]})
			elif len(user.branch_ids) > 1 and user.id not in group_multi_branch.users.ids:
				user.write({'groups_id': [(4, group_multi_branch.id)]})
		return user

	def write(self, values):
		res = super(Users, self).write(values)
		group_multi_branch = self.env.ref('solse_multi_branch.group_multi_branch', False)
		if group_multi_branch and 'branch_ids' in values:
			for user in self:
				if len(user.branch_ids) <= 1 and user.id in group_multi_branch.users.ids:
					user.write({'groups_id': [(3, group_multi_branch.id)]})
				elif len(user.branch_ids) > 1 and user.id not in group_multi_branch.users.ids:
					user.write({'groups_id': [(4, group_multi_branch.id)]})
		return res

class Partner(models.Model):
	_inherit = "res.partner"

	branch_id = fields.Many2one('res.branch', 'Sucursal')
	@api.constrains('branch_id', 'company_id')
	def _check_branch_id(self):
		for obj in self:
			if obj.branch_id and not obj.company_id:
				raise ValidationError(_('Company is required with Sucursal.'))
			if obj.branch_id and obj.branch_id not in obj.company_id.branch_ids:
				raise ValidationError(_('Sucursal should belongs to the selected Company.'))

class ResCompany(models.Model):
	_inherit = "res.company"

	branch_ids = fields.One2many("res.branch", "company_id", string="Sucursales", readonly=True)
	default_branch_id = fields.Many2one("res.branch", string="Default Sucursal", domain="[('id','in',branch_ids)]")

class ResPartnerBank(models.Model):
	_inherit = 'res.partner.bank'

	branch_id = fields.Many2one('res.branch', 'Sucursal', default=lambda self: self.env.branch, ondelete='restrict', domain="[('company_id','in',company_ids)]")
