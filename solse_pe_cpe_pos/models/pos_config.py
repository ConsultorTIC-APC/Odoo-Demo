# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class PosConfig(models.Model):
	_inherit = 'pos.config'
	
	# module_account
	# auto_open_invoice = fields.Boolean("Factura automática")

	iface_journals = fields.Boolean("Mostrar documentos de venta", help="Habilita el uso de documentos electrónicos desde el Punto de Venta", default=True)
	documento_venta_ids = fields.Many2many("l10n_latam.document.type", string="Documentos de venta", domain=[("sub_type", "=", "sale")])
