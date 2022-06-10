from odoo import models, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    partner_invoice_id = fields.Many2one(
        'account.move', string='Factura de proveedor', readonly=True)
