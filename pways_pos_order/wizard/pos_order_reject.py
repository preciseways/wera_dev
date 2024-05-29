from odoo import api, fields, models
from datetime import date, datetime, timedelta
import requests
import json

class POSorderRejectWizard(models.TransientModel):
    _name = 'pos.order.reject.wizard'
    _description = "POS Order Reject Wizard"

    rejection_reason = fields.Selection([
        ('1', 'Items out of stock'),
        ('2', 'No delivery boys available'),
        ('3', 'Nearing closing time'),
        ('4', 'Out of Subzone/Area'),
        ('5', 'Kitchen is Full')
    ], string='Rejection Reason')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company, ondelete='cascade')

    def action_confirm(self):
        active_id = self.env.context.get('active_id')
        headers = {"charset": "utf-8", "Content-Type": "application/json"}
        if active_id:
            order_id = self.env['pos.order'].sudo().search([('id','=', active_id)])
            if order_id:
                url = order_id.company_id.reject_url
                data = {'merchand_id': order_id.restaurant_id ,'order_id': order_id.id}
                headers = {"charset": "utf-8", "Content-Type": "application/json"}
                response = requests.post(url=url, json=data, headers=headers)
                if response:
                    order_id.write({'rejection_reason': self.rejection_reason})
                    order_id.write({'state':'cancel'})
                else:
                    products_v15= {'code':2, 'msg':'Could not update status at zomato','details':[]}
                    response = requests.post(url=url, json=products_v15, headers=headers)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }