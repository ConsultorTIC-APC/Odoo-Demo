# -*- coding: utf-8 -*-
# Copyright (c) 2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
	_inherit = "sale.order"

	branch_id = fields.Many2one('res.branch', 'Sucursal', index=True, default=lambda self:  self.env.branch.id or self.env.company.default_branch_id.id, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

	@api.constrains('branch_id', 'order_line', 'company_id')
	def _check_order_line_branch_id(self):
		for order in self:
			if order.branch_id not in order.company_id.branch_ids:
				raise ValidationError(_('Sucursal should belongs to the selected Company.'))
			branches = order.order_line.product_id.branch_id
			if branches and branches != order.branch_id:
				bad_products = order.order_line.product_id.filtered(lambda p: p.branch_id and p.branch_id != order.branch_id)
				raise ValidationError((_("Your quotation contains products from branch %s whereas your quotation belongs to branch %s. \n Please change the branch of your quotation or remove the products from other branches (%s).") % (', '.join(branches.mapped('display_name')), order.branch_id.display_name, ', '.join(bad_products.mapped('display_name')))))

class SaleOrderLine(models.Model):
	_inherit = 'sale.order.line'

	branch_id = fields.Many2one(related='order_id.branch_id', string='Sucursal', store=True, readonly=True, index=True)

class SaleOrderTemplate(models.Model):
	_inherit = "sale.order.template"

	branch_id = fields.Many2one('res.branch', 'Sucursal', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

	@api.constrains('branch_id', 'company_id', 'sale_order_template_line_ids', 'sale_order_template_option_ids')
	def _check_branch_id(self):
		for template in self:
			if template.branch_id and not template.company_id:
				raise ValidationError(_('Comapny is required with Sucursal.'))
			if template.branch_id and template.branch_id not in template.company_id.branch_ids:
				raise ValidationError(_('Sucursal should belongs to the selected Company.'))
			branches = template.mapped('sale_order_template_line_ids.product_id.branch_id') | template.mapped('sale_order_template_option_ids.product_id.branch_id')
			if len(branches) > 1:
				raise ValidationError(_("Your template cannot contain products from multiple branches."))
			elif branches and branches != template.branch_id:
				raise ValidationError((_("Your template contains products from branch %s whereas your template belongs to branch %s. \n Please change the branch of your template or remove the products from other branches.") % (branches.mapped('display_name'), template.branch_id.display_name)))

	@api.onchange('sale_order_template_line_ids', 'sale_order_template_option_ids')
	def _onchange_template_line_ids(self):
		super(SaleOrderTemplate, self)._onchange_template_line_ids()
		branches = self.mapped('sale_order_template_option_ids.product_id.branch_id') | self.mapped('sale_order_template_line_ids.product_id.branch_id')
		if branches and self.branch_id not in branches:
			self.branch_id = branches[0]

class SaleOrderTemplateLine(models.Model):
	_inherit = "sale.order.template.line"

	branch_id = fields.Many2one('res.branch', related='sale_order_template_id.branch_id', store=True, index=True)

class SaleOrderTemplateOption(models.Model):
	_inherit = "sale.order.template.option"

	branch_id = fields.Many2one('res.branch', related='sale_order_template_id.branch_id', store=True, index=True)

