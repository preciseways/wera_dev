from odoo import models, fields, api

class AddonGroupProductWizard(models.TransientModel):
    _name = 'addon.group.product.wizard'
    _description = 'Addon Group Product Wizard'

    name = fields.Char(string='Name', readonly=True)
    addon_min_limit = fields.Integer(string='Addon Min Limit', readonly=True)
    addon_limit = fields.Integer(string='Addon Limit', readonly=True)
    addon_free_limit = fields.Integer(string='Addon Free Limit', readonly=True)
    order = fields.Integer(string='Order', readonly=True)
    
    def action_confirm(self):
        return {'type': 'ir.actions.act_window_close'}

    addons_product_ids = fields.One2many('addon.group.product.wizard.line', 'wizard_id', string="Addons Product", readonly=True)

    @api.model
    def default_get(self, fields_list):
        res = super(AddonGroupProductWizard, self).default_get(fields_list)
        addon_group_id = self.env.context.get('active_id')
        addon_group = self.env['addon.group'].browse(addon_group_id)

        if addon_group:
            res.update({
                'name': addon_group.name,
                'addon_min_limit': addon_group.addon_min_limit,
                'addon_limit': addon_group.addon_limit,
                'addon_free_limit': addon_group.addon_free_limit,
                'order': addon_group.order,
                'addons_product_ids': [(0, 0, {
                    'product_name': line.product_name,
                    'is_veg': line.is_veg,
                    'in_stock': line.in_stock,
                    'is_default': line.is_default,
                    'order': line.order,
                    'price': line.price,
                    'taxes_id': [(6, 0, line.taxes_id.ids)]
                }) for line in addon_group.addons_product_ids]
            })
        return res

class AddonGroupProductWizardLine(models.TransientModel):
    _name = 'addon.group.product.wizard.line'
    _description = 'Addon Group Product Wizard Line'

    wizard_id = fields.Many2one('addon.group.product.wizard', string="Wizard", required=True, ondelete='cascade')
    product_name = fields.Char(string="Product Name")
    is_veg = fields.Boolean(string="Is Veg")
    in_stock = fields.Boolean(string="In Stock")
    is_default = fields.Boolean(string="Is Default")
    order = fields.Integer(string="Order")
    price = fields.Float(string="Price")
    taxes_id = fields.Many2many('account.tax', string="Taxes")