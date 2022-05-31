# -*- coding: utf-8 -*-
# Copyright (c) 2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
	_inherit = "product.template"

	branch_id = fields.Many2one('res.branch', 'Sucursal', index=1, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

	@api.constrains('branch_id', 'company_id')
	def _check_branch_id(self):
		for obj in self:
			if obj.branch_id and not obj.company_id:
				raise ValidationError(_('Comapny is required with Sucursal.'))
			if obj.branch_id and obj.branch_id not in obj.company_id.branch_ids:
				raise ValidationError(_('Sucursal should belongs to the selected Company.'))

class SupplierInfo(models.Model):
	_inherit = "product.supplierinfo"

	branch_id = fields.Many2one('res.branch', 'Sucursal', default=lambda self: self.env.company.default_branch_id.id or self.env.branch.id, index=1, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

class ProductPackaging(models.Model):
	_inherit = "product.packaging"

	branch_id = fields.Many2one('res.branch', 'Sucursal', index=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
