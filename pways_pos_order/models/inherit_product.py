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
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company, ondelete='cascade')


    def fetch_categories(self):
        pos_categories = self.env['product.category'].sudo().search([])

        categories_dict = {}
        main_categories_set = set()

        for category in pos_categories:
            categories_dict[category.id] = {
                "id": category.id,
                "name": category.name,
                "description": category.description or "",
                "order": None,
                "sub_categories": []
            }
            if not category.parent_id:
                main_categories_set.add(category.id)

        for category in pos_categories:
            if category.parent_id:
                parent_id = category.parent_id.id
                if parent_id in categories_dict:
                    categories_dict[parent_id]["sub_categories"].append(categories_dict[category.id])
                    if category.id in main_categories_set:
                        main_categories_set.remove(category.id)

        def remove_empty_sub_categories(category):
            if not category["sub_categories"]:
                category.pop("sub_categories")
            else:
                for sub_category in category["sub_categories"]:
                    remove_empty_sub_categories(sub_category)

        main_categories = []
        for main_category_id in main_categories_set:
            main_category = categories_dict[main_category_id]
            remove_empty_sub_categories(main_category)
            main_categories.append(main_category)

        return main_categories

    def fetch_tax_details(self, taxes):
        cgst = None
        igst = None
        sgst = None
        taxes_val = taxes.taxes_id
        for tax in taxes_val:
            if tax.amount_type == 'group':
                for child_tax in tax.children_tax_ids:
                    if 'CGST' in child_tax.name:
                        cgst = child_tax.amount
                    if 'SGST' in child_tax.name:
                        sgst = child_tax.amount
            if tax.amount_type == 'fixed':
                igst = tax.amount

        gst = {
            "igst": igst,
            "cgst": cgst,
            "sgst": sgst,
            "inclusive": False,
            "gst_liability": "SWIGGY"
        } if taxes else None

        return gst

    def fetch_variant_group(self, product):
        variant_group = []

        if product.attribute_line_ids:
            for attribute_line in product.attribute_line_ids:
                variant_group_dict = {
                    "id": str(attribute_line.attribute_id.id),
                    "name": str(attribute_line.attribute_id.name),
                    "order": 0,
                    "variants": []
                }

                for value in attribute_line.product_template_value_ids:
                    variant = {
                        "id": str(value.product_attribute_value_id.id),
                        "name": str(value.name),
                        "price": int(value.price_extra),
                        "default": False,
                        "is_veg": 1,
                        "in_stock": 1,
                        "order": 1,
                        "gst_details": None
                    }
                    variant_group_dict["variants"].append(variant)

                variant_group.append(variant_group_dict)

        return variant_group

    def fetch_addons_group(self, product):
        addons = []

        if product.addons_group_ids:
            for addon_group in product.addons_group_ids:
                addon_group_dict = {
                    "id": addon_group.id,
                    "name": addon_group.name,
                    "addon_free_limit": addon_group.addon_free_limit if addon_group.addon_free_limit else None,
                    "addon_limit": addon_group.addon_limit if addon_group.addon_limit else None,
                    "addon_min_limit": addon_group.addon_min_limit if addon_group.addon_min_limit else None,
                    "order": None,
                    "addons": []
                }

                for addon_product in addon_group.addons_product_ids:
                    gst = self.fetch_tax_details(addon_product)
                    addon = {
                        "id": str(addon_product.id),
                        "name": addon_product.product_name,
                        "price": int(addon_product.price),
                        "is_veg": addon_product.is_veg,
                        "in_stock": addon_product.in_stock,
                        "order": addon_product.order if addon_product.order else None,
                        "is_default": addon_product.is_default if addon_product.is_default else None,
                        "gst_details": gst
                    }
                    addon_group_dict["addons"].append(addon)

                addons.append(addon_group_dict)

        return addons

    def get_item_slots(self,product):
        item_slot = [ ]

        if product.slot_ids:
            for slot in product.slot_ids:
                if slot.week_ids:
                    slot_dict = {
                        "open_time": "{:.1f}".format(slot.start_hour),
                        "close_time": "{:.1f}".format(slot.end_hour),
                        "day_of_week": []
                    }
                    for day in slot.week_ids:
                        slot_dict["day_of_week"].append(str(day.id))
                    item_slot.append(slot_dict)
                else:
                    slot_dict = {
                        "open_time": "{:.1f}".format(slot.start_hour),
                        "close_time": "{:.1f}".format(slot.end_hour),
                        "day_of_week": None                    
                    }
                    item_slot.append(slot_dict)
        return item_slot

    def pos_menu_creation(self):
        print("self--------------------------",self.company_id)
        category_structure = {
            "merchant_id": "2544",
            "menu": {
                "entity": {
                    "main_categories": [],
                    "items": []
                }
            }
        }

        category_structure["menu"]["entity"]["main_categories"] = self.fetch_categories()

        pos_products = self.env['product.template'].sudo().search([('enable', '=', True)])

        for product in pos_products:
            gst = self.fetch_tax_details(product)
            variant_group = self.fetch_variant_group(product)
            addons = self.fetch_addons_group(product)
            item_slot = self.get_item_slots(product)
            main_categorie_id = product.categ_id.parent_id.id if product.categ_id.parent_id else product.categ_id.id
            sub_category_id = product.categ_id.id if product.categ_id.parent_id else None
            item = {
                "id": product.id,
                "category_id": str(main_categorie_id),
                "sub_category_id": str(sub_category_id),
                "name": product.name,
                "is_veg": product.is_veg,
                "description": product.description or "",
                "price": 0,
                "gst_details": gst,
                "packing_charges": str(product.packing_charges) or "0",
                "enable": 1 if product.enable else 0,
                "in_stock": 1 if product.in_stock else 0,
                "addon_free_limit": product.addon_free_limit if product.addon_free_limit else None,
                "addon_limit": product.addon_limit if product.addon_limit else None,
                "addon_min_limit": product.addon_min_limit or None,
                "image_url": product.image_url or "",
                "item_slots": [],
                "image_url_swiggy": product.image_url_swiggy or "",
                "image_url_zomato": product.image_url_zomato or "",
                "is_goods": False,
                "variant_groups": variant_group,
                "addon_groups": addons,
                "pricing_combinations": [],
                "item_slots": item_slot,
                "order": 2,
                "recommended": False,
                "catalog_attributes": {
                    "spice_level": None,
                    "sweet_level": None,
                    "gravy_property": None,
                    "bone_property": None,
                    "contain_seasonal_ingredients": None,
                    "accompaniments": None,
                    "quantity": None,
                    "serves_how_many": None
                }
            }
            category_structure["menu"]["entity"]["items"].append(item)

        if not category_structure["menu"]["entity"]["items"]:
            category_structure["menu"]["entity"]["items"] = None

        headers = {"X-Wera-Api-Key": "8cab0be2-1972-480d-a077-5f5a905806dc", "Content-Type": "application/json", "Accept": "application/json"}
        url = self.company_id.menu_creation_url
        print("category_structure----------------", json.dumps(category_structure, indent=2))
        if not url:
            raise ValidationError(_('"Insert Menu Creation URL in Company."'))
        response = requests.post(url=url, json=category_structure, headers=headers)
        return category_structure

 

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