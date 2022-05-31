# -*- coding: utf-8 -*-
# Copyright (c) 2022 Juan Gabriel Fernandez More (kiyoshi.gf@gmail.com)
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from odoo import api, fields, models, registry, tools, _
from odoo.http import request
from odoo.exceptions import AccessError
from odoo.tools import lazy_property
from odoo.api import Environment
from odoo import SUPERUSER_ID
from functools import wraps
import logging
_logger = logging.getLogger(__name__)

def after_commit(func):
	@wraps(func)
	def wrapped(self, *args, **kwargs):
		dbname = self.env.cr.dbname
		context = self.env.context
		uid = self.env.uid

		@self.env.cr.postcommit.add
		def called_after():
			db_registry = registry(dbname)
			with api.Environment.manage(), db_registry.cursor() as cr:
				env = api.Environment(cr, uid, context)
				try:
					func(self.with_env(env), *args, **kwargs)
				except Exception as e:
					_logger.warning("Could not sync record now: %s" % self)
					_logger.exception(e)

	return wrapped

class IrRule(models.Model):
	_inherit = 'ir.rule'

	@api.model
	def _eval_context(self):
		res = super(IrRule, self)._eval_context()
		res['branch_ids'] = request.env.branches.ids
		res['branch_id'] = request.env.branch.id
		return res

class SucursalEnvironment(Environment):

	@lazy_property
	def branch(self):
		branch_ids = self.context.get('allowed_branch_ids', [])
		if branch_ids:
			if not self.su:
				user_branch_ids = self.user.branch_ids.ids
				if any(bid not in user_branch_ids for bid in branch_ids):
					raise AccessError(_("Access to unauthorized or invalid branches."))
			return self['res.branch'].browse(branch_ids[0])
		return self.user.branch_id

	@lazy_property
	def branches(self):
		branch_ids = self.context.get('allowed_branch_ids', [])
		if branch_ids:
			if not self.su:
				user_branch_ids = self.user.branch_ids.ids
				if any(bid not in user_branch_ids for bid in branch_ids):
					raise AccessError(_("Access to unauthorized or invalid branches."))
			return self['res.branch'].browse(branch_ids)
		return self.user.branch_ids

	Environment.branch = branch
	Environment.branches = branches

class SucursalHttp(models.AbstractModel):
	_inherit = 'ir.http'

	@after_commit
	def recalcular_variable(self):
		self.env['ir.model.access'].call_cache_clearing_methods()
		self.env['ir.rule'].clear_caches()
		api.Environment.reset()
		SucursalEnvironment.reset()


	def session_info(self):		
		result = super(SucursalHttp, self).session_info()
		user = request.env.user
		result.update({
			"user_branches": {
				'current_branch': (user.branch_id.id, user.branch_id.name, user.branch_id.company_id.id, user.branch_id.company_id.name), 
				'allowed_branches': [(brh.id, brh.name, brh.company_id.id, brh.company_id.name) for brh in user.branch_ids]
			}, 
			'display_switch_branch_menu': user.has_group('solse_multi_branch.group_multi_branch') and len(user.branch_ids)>1,
		})
		self.recalcular_variable()
		return result
