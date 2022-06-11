from odoo import models, fields, api
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    account_move_ids = fields.Many2many(
        'account.move', string='Facturas de proveedor', compute='_compute_account_move_ids', store=True)
    account_move_count = fields.Integer(string='# Facturas de proveedor', compute='_compute_account_move_ids', store=True)
    
    @api.depends('expense_line_ids','expense_line_ids.account_move_id')
    def _compute_account_move_ids(self):
        for record in self:
            account_move_ids = record.expense_line_ids.account_move_id.ids
            account_move_count = len(account_move_ids)
            record.account_move_ids = account_move_ids
            record.account_move_count = account_move_count
        
    def action_get_invoice_view(self):
        res = self.env['ir.actions.act_window']._for_xml_id('account.action_move_in_invoice_type')
        res['domain'] = [('id', 'in', self.account_move_ids.ids)]
        return res
    
    def _assign_outstanding_entry_to_invoice(self, move_id, line_id):
        _logger.info('assign_outstanding_entry_to_invoice')
        move_id.js_assign_outstanding_line(line_id)
    
    def _validate_posted_invoices(self):
        if self.account_move_ids and self.account_move_ids.filtered(lambda x: x.state != 'posted'):
            raise UserError('Una o más facturas de proveedor no han sido confirmadas.')
        
    def action_sheet_move_create(self):
        self._validate_posted_invoices()
        res = super(HrExpenseSheet, self).action_sheet_move_create()
        for record in self:
            if record.account_move_id:
                #line_id = record.line_ids.filtered(lambda x: x.account_id.reconcile == True and not x.reconciled)[0].id
                for line in record.account_move_id.line_ids.filtered(lambda x: x.account_id.reconcile == True and not x.reconciled):
                    if line.partner_invoice_id:
                        _logger.info(line.partner_invoice_id)
                        record._assign_outstanding_entry_to_invoice(line.partner_invoice_id, line.id)
            record.account_move_id
        return res