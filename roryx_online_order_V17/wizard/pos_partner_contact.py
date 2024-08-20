from odoo import api, fields, models
from datetime import date, datetime, timedelta
import requests
import json

class POSorderRejectWizard(models.TransientModel):
    _name = 'pos.order.connect.wizard'
    _description = "POS Order Connect Wizard"

    marks = fields.Char(string="Remarks")

    def action_confirm(self):
        active_id = self.env.context.get('active_id')
        if active_id:
            order_id = self.env['pos.order'].browse(active_id)
            if order_id:
                url = order_id.company_id.call_support
                products_v15= {'merchand_id': order_id.restaurant_id ,'order_id': order_id.id, 'rejection_id': self.marks}
                headers = {"charset": "utf-8", "Content-Type": "application/json"}
                response = requests.post(url=url, json=products_v15, headers=headers)
                response = json.dumps({'merchant_id': order_id.restaurant_id, 'order_id': order_id.id})
                if response:
                    order_id.write({'order_remarks': self.marks})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }