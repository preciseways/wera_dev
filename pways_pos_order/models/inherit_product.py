from odoo import models, fields, api, _
from datetime import datetime, timedelta
import requests
import json
from odoo.exceptions import ValidationError, UserError

class PosConfig(models.Model):
    _inherit = "pos.config"

    online_order = fields.Boolean(string="Online Order")

class PosResCompany(models.Model):
    _inherit = "res.company"

    accept_url = fields.Char(string="Order Accept URL")
    reject_url = fields.Char(string="Order Reject URL")
    food_ready_url = fields.Char(string="Food Ready URL")
    call_support = fields.Char(string="Call Swiggy Partner URL")
    order_delivery_url = fields.Char(string="Get Delivery Agent URL")
    order_pickup_url = fields.Char(string="Order Picked-up URL")
    get_customer_url = fields.Char(string="Get Customer Number URL")
    menu_creation_url = fields.Char(string="Menu Creation URL")

class ProductCategory(models.Model):
    _inherit = 'product.category'

    description = fields.Char(string="Description")

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    wera_id = fields.Integer(string="Wera Item ID")
    is_veg = fields.Boolean(string="Is Veg")
    in_stock = fields.Boolean(string="In Stock")
    description = fields.Char(string="Description")
    cgst = fields.Float(string="CGST Tax")
    igst = fields.Float(string="IGST Tax")
    sgst = fields.Float(string="SGST Tax")
    addons_group_ids = fields.Many2many('addon.group')
    gst_liability = fields.Char(string="GST Liability")
    inclusive = fields.Boolean(string="Inclusive")
    packing_charges = fields.Float(string="Packing Charge")
    enable = fields.Boolean(string="Enable")
    addon_free_limit = fields.Integer(string='Addon Free Limit')
    addon_min_limit = fields.Integer(string="Addon Min Limit")
    addon_limit = fields.Integer(string='Addon Limit',)
    image_url = fields.Char(string='Image URL')
    image_url_swiggy = fields.Char(string='Swiggy Image URL')
    image_url_zomato = fields.Char(string='Zomato Image URL')
    is_goods = fields.Boolean(string='Is Goods')
    order = fields.Integer(string="Order")
    preparation_time = fields.Integer(string="Preparation Time")
    slot_ids = fields.One2many('item.slots','slot_id')



class PosProductItemSlots(models.Model):
    _name = 'item.slots'

    slot_id = fields.Many2one('product.template')
    start_hour = fields.Float(string="Open Time")    
    end_hour = fields.Float(string="Close Time")
    week_ids = fields.Many2many('week.day')

class Weekday(models.Model):
    _name = 'week.day'
    _description = 'Week Day'

    name = fields.Char(string="Day Name", required=True)

class PosAddonGroup(models.Model):
    _name = 'addon.group'

    addon_group_id = fields.Many2one('product.template')
    name = fields.Char(string="Name")
    addon_min_limit = fields.Char(string="Addon Min Limit")
    addon_limit = fields.Char(string="Addon Limit")
    addon_free_limit = fields.Char(string="Addon Free Limit")
    addons_product_ids = fields.One2many('addon.group.product','addon_product_id')
    order = fields.Integer(string="Order")

        
class PosAddonGroup(models.Model):
    _name = 'addon.group.product'

    addon_product_id = fields.Many2one('addon.group')
    product_name = fields.Char(string="Product Name")
    is_veg = fields.Boolean(string="Is Veg")
    in_stock = fields.Boolean(string="In Stock")
    is_default = fields.Boolean(string="Is Default")
    order = fields.Integer(string="order")
    price = fields.Float(string="Price")
    taxes_id = fields.Many2many('account.tax')