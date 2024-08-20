from odoo import models, fields, api

class AddonGroupProductWizard(models.TransientModel):
    _name = 'addon.group.product.wizard'
    _description = 'Addon Group Product Wizard'

    name = fields.Char(string='Name', readonly=True)
    addon_min_limit = fields.Integer(string='Addon Min Limit', readonly=True)
    addon_limit = fields.Integer(string='Addon Limit', readonly=True)
    addon_free_limit = fields.Integer(string='Addon Free Limit', readonly=True)
    order = fields.Integer(string='Order', readonly=True)
    addons_product_ids = fields.One2many('addon.product', 'addon_group_id', string='Addon Products', readonly=True)
    
    def action_confirm(self):
        return {'type': 'ir.actions.act_window_close'}
