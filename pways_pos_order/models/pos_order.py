from odoo import models, fields, api, _
from datetime import datetime, timedelta
import requests
import json
from odoo.exceptions import ValidationError, UserError

class PosSession(models.Model):
    _inherit = 'pos.session'

    state = fields.Selection(selection_add=[('draft','Draft')], ondelete={'draft': 'cascade'})
    custom_session = fields.Boolean(string="Online Order")

class PosResConfig(models.TransientModel):
    _inherit = "res.config.settings"

    custom_shop = fields.Boolean(related='pos_config_id.online_order',readonly=False)

    def create_new_session_for_orders(self):
        if self.custom_shop and self.pos_payment_method_ids:
            pos_session = self.env['pos.session'].sudo().search([('custom_session','=', True)])
            if not pos_session:
                pos_session_val = {
                'config_id': self.pos_config_id.id,
                'name': 'POS Session',
                'custom_session': True
                }
                pos_session = self.env['pos.session'].create(pos_session_val)
        return True
        
class PosOrderAddons(models.Model):
    _name = 'order.addons'

    order_addon = fields.Many2one('pos.order')
    addon_id = fields.Many2one('addon.group.product')
    name = fields.Char(string="Product Name", help="Insert the Product Name")
    price = fields.Float(string="Price", help="Insert Product Price")
    discount = fields.Float(string="Discount", help="Insert the Discount on Product")


class PosOrder(models.Model):
    _inherit = "pos.order"

    is_accepted = fields.Boolean(string="Is Accepted")
    is_auto_accepted = fields.Char(string="IS Auto False")
    order_otp = fields.Integer(string="Order OTP")
    password = fields.Char(string="Order Password")
    pos_order = fields.Boolean(string="POS online Order")
    order_id = fields.Integer(string="Order Id")
    rejection_reason = fields.Char(string="Rejection Reason")
    order_remarks = fields.Char(string="Order Remarks")
    accept_reason = fields.Char(string="Accept Reason")
    delivery_agent_assign = fields.Boolean(string="Delivery Agent")
    wera_order_id = fields.Char(string="Wera Order id")
    restaurant_id = fields.Char(string="Wera Outlet Id")
    restaurant_name = fields.Char(string="Restaurant Name")
    external_order_id = fields.Char(string="External Order ID")
    order_from = fields.Char(string="Order From")
    food_ready = fields.Boolean(string="Food Ready")
    order_pickup = fields.Boolean(string="Is Order Pickup")
    enable_delivery = fields.Selection([('0','Source Fulfilled order'),('1','Restaurant Fulfilled Order')], string="Enable Delivery")
    net_amount = fields.Float(string="Total Cost")
    payment_mode = fields.Selection([('CASH','CASH'),('ONLINE','ONLINE')], string="Payment Mode")
    order_type = fields.Selection([('DELIVERY','TAKEAWAY'),('DELIVERY','DELIVERY'),('DINEIN','DINEIN')], string="Order Type")
    total_cgst = fields.Float(string="Total CGST")
    total_sgst = fields.Float(string="Total SGST")
    order_packaging = fields.Float(string="Order Packing Charge")
    order_packaging_cgst = fields.Float(string='CGST on Order Packaging Charge')
    order_packaging_sgst = fields.Float(string='SGST on Order Packaging Charge')
    order_packaging_cgst_percent = fields.Float(string='CGST Percent on Order Packaging Charge')
    order_packaging_sgst_percent = fields.Float(string='SGST Percent on Order Packaging Charge')
    order_discount = fields.Float(string='Total Discount on Order')
    delivery_charge = fields.Float(string='Delivery Charge on Order')
    customer_name = fields.Char(string='Customer Name')
    customer_phone_number = fields.Char(string='Contact Number')
    customer_email = fields.Char(string='Email Address')
    customer_address = fields.Text(string='Complete Delivery Address')
    delivery_area = fields.Char(string='Source Delivery Area')
    address_instructions = fields.Text(string='Delivery Instructions')
    discount = fields.Float(string='Discount on Item')
    item_quantity = fields.Integer(string='Quantity of Item Ordered')
    size_id = fields.Char(string='Size ID')
    size_name = fields.Char(string='Size Name')
    size_price = fields.Float(string='Size Price')
    size_cgst = fields.Float(string='Size CGST')
    size_sgst = fields.Float(string='Size SGST')
    size_cgst_percent = fields.Float(string='Size CGST Percent')
    size_sgst_percent = fields.Float(string='Size SGST Percent')
    addons_id = fields.Char(string='Addon ID')
    addons_name = fields.Char(string='Addon Name')
    addons_price = fields.Float(string='Addon Price')
    addons_cgst = fields.Float(string='Addons CGST')
    addons_sgst = fields.Float(string='Addons SGST')
    addons_cgst_percent = fields.Float(string='Addons CGST Percent')
    addons_sgst_percent = fields.Float(string='Addons SGST Percent')
    rider_name = fields.Char(string="Rider Name")
    rider_contact = fields.Integer(string="Rider Number")
    rider_status = fields.Char(string="Rider Status")
    time_to_arrive = fields.Integer(string="Time to arrive")
    order_addons_ids = fields.One2many('order.addons','order_addon')

    # def fetch_categories(self):
    #     pos_categories = self.env['product.category'].sudo().search([])

    #     categories_dict = {}
    #     main_categories_set = set()

    #     for category in pos_categories:
    #         categories_dict[category.id] = {
    #             "id": category.id,
    #             "name": category.name,
    #             "description": category.description or "",
    #             "order": None,
    #             "sub_categories": []
    #         }
    #         if not category.parent_id:
    #             main_categories_set.add(category.id)

    #     for category in pos_categories:
    #         if category.parent_id:
    #             parent_id = category.parent_id.id
    #             if parent_id in categories_dict:
    #                 categories_dict[parent_id]["sub_categories"].append(categories_dict[category.id])
    #                 if category.id in main_categories_set:
    #                     main_categories_set.remove(category.id)

    #     def remove_empty_sub_categories(category):
    #         if not category["sub_categories"]:
    #             category.pop("sub_categories")
    #         else:
    #             for sub_category in category["sub_categories"]:
    #                 remove_empty_sub_categories(sub_category)

    #     main_categories = []
    #     for main_category_id in main_categories_set:
    #         main_category = categories_dict[main_category_id]
    #         remove_empty_sub_categories(main_category)
    #         main_categories.append(main_category)

    #     return main_categories

    # def fetch_tax_details(self, taxes):
    #     cgst = None
    #     igst = None
    #     sgst = None
    #     taxes_val = taxes.taxes_id
    #     for tax in taxes_val:
    #         if tax.amount_type == 'group':
    #             for child_tax in tax.children_tax_ids:
    #                 if 'CGST' in child_tax.name:
    #                     cgst = child_tax.amount
    #                 if 'SGST' in child_tax.name:
    #                     sgst = child_tax.amount
    #         if tax.amount_type == 'fixed':
    #             igst = tax.amount

    #     gst = {
    #         "igst": igst,
    #         "cgst": cgst,
    #         "sgst": sgst,
    #         "inclusive": False,
    #         "gst_liability": "SWIGGY"
    #     } if taxes else None

    #     return gst

    # def fetch_variant_group(self, product):
    #     variant_group = []

    #     if product.attribute_line_ids:
    #         for attribute_line in product.attribute_line_ids:
    #             variant_group_dict = {
    #                 "id": str(attribute_line.attribute_id.id),
    #                 "name": str(attribute_line.attribute_id.name),
    #                 "order": 0,
    #                 "variants": []
    #             }

    #             for value in attribute_line.product_template_value_ids:
    #                 variant = {
    #                     "id": str(value.product_attribute_value_id.id),
    #                     "name": str(value.name),
    #                     "price": int(value.price_extra),
    #                     "default": False,
    #                     "is_veg": 1,
    #                     "in_stock": 1,
    #                     "order": 1,
    #                     "gst_details": None
    #                 }
    #                 variant_group_dict["variants"].append(variant)

    #             variant_group.append(variant_group_dict)

    #     return variant_group

    # def fetch_addons_group(self, product):
    #     addons = []

    #     if product.addons_group_ids:
    #         for addon_group in product.addons_group_ids:
    #             addon_group_dict = {
    #                 "id": addon_group.id,
    #                 "name": addon_group.name,
    #                 "addon_free_limit": addon_group.addon_free_limit if addon_group.addon_free_limit else None,
    #                 "addon_limit": addon_group.addon_limit if addon_group.addon_limit else None,
    #                 "addon_min_limit": addon_group.addon_min_limit if addon_group.addon_min_limit else None,
    #                 "order": None,
    #                 "addons": []
    #             }

    #             for addon_product in addon_group.addons_product_ids:
    #                 gst = self.fetch_tax_details(addon_product)
    #                 addon = {
    #                     "id": str(addon_product.id),
    #                     "name": addon_product.product_name,
    #                     "price": int(addon_product.price),
    #                     "is_veg": addon_product.is_veg,
    #                     "in_stock": addon_product.in_stock,
    #                     "order": addon_product.order if addon_product.order else None,
    #                     "is_default": addon_product.is_default if addon_product.is_default else None,
    #                     "gst_details": gst
    #                 }
    #                 addon_group_dict["addons"].append(addon)

    #             addons.append(addon_group_dict)

    #     return addons

    # def get_item_slots(self,product):
    #     item_slot = [ ]

    #     if product.slot_ids:
    #         for slot in product.slot_ids:
    #             if slot.week_ids:
    #                 slot_dict = {
    #                     "open_time": "{:.1f}".format(slot.start_hour),
    #                     "close_time": "{:.1f}".format(slot.end_hour),
    #                     "day_of_week": []
    #                 }
    #                 for day in slot.week_ids:
    #                     slot_dict["day_of_week"].append(str(day.id))
    #                 item_slot.append(slot_dict)
    #             else:
    #                 slot_dict = {
    #                     "open_time": "{:.1f}".format(slot.start_hour),
    #                     "close_time": "{:.1f}".format(slot.end_hour),
    #                     "day_of_week": None                    
    #                 }
    #                 item_slot.append(slot_dict)
    #     return item_slot

    # def pos_menu_creation(self):
    #     category_structure = {
    #         "merchant_id": "2544",
    #         "menu": {
    #             "entity": {
    #                 "main_categories": [],
    #                 "items": []
    #             }
    #         }
    #     }

    #     category_structure["menu"]["entity"]["main_categories"] = self.fetch_categories()

    #     pos_products = self.env['product.template'].sudo().search([('enable', '=', True)])

    #     for product in pos_products:
    #         gst = self.fetch_tax_details(product)
    #         variant_group = self.fetch_variant_group(product)
    #         addons = self.fetch_addons_group(product)
    #         item_slot = self.get_item_slots(product)
    #         main_categorie_id = product.categ_id.parent_id.id if product.categ_id.parent_id else product.categ_id.id
    #         sub_category_id = product.categ_id.id if product.categ_id.parent_id else None
    #         item = {
    #             "id": product.id,
    #             "category_id": str(main_categorie_id),
    #             "sub_category_id": str(sub_category_id),
    #             "name": product.name,
    #             "is_veg": product.is_veg,
    #             "description": product.description or "",
    #             "price": 0,
    #             "gst_details": gst,
    #             "packing_charges": str(product.packing_charges) or "0",
    #             "enable": 1 if product.enable else 0,
    #             "in_stock": 1 if product.in_stock else 0,
    #             "addon_free_limit": product.addon_free_limit if product.addon_free_limit else None,
    #             "addon_limit": product.addon_limit if product.addon_limit else None,
    #             "addon_min_limit": product.addon_min_limit or None,
    #             "image_url": product.image_url or "",
    #             "item_slots": [],
    #             "image_url_swiggy": product.image_url_swiggy or "",
    #             "image_url_zomato": product.image_url_zomato or "",
    #             "is_goods": False,
    #             "variant_groups": variant_group,
    #             "addon_groups": addons,
    #             "pricing_combinations": [],
    #             "item_slots": item_slot,
    #             "order": 2,
    #             "recommended": False,
    #             "catalog_attributes": {
    #                 "spice_level": None,
    #                 "sweet_level": None,
    #                 "gravy_property": None,
    #                 "bone_property": None,
    #                 "contain_seasonal_ingredients": None,
    #                 "accompaniments": None,
    #                 "quantity": None,
    #                 "serves_how_many": None
    #             }
    #         }
    #         category_structure["menu"]["entity"]["items"].append(item)

    #     if not category_structure["menu"]["entity"]["items"]:
    #         category_structure["menu"]["entity"]["items"] = None

    #     headers = {"X-Wera-Api-Key": "8cab0be2-1972-480d-a077-5f5a905806dc", "Content-Type": "application/json", "Accept": "application/json"}
    #     url = self.company_id.menu_creation_url
    #     print("category_structure----------------", json.dumps(category_structure, indent=2))
    #     if not url:
    #         raise ValidationError(_('"Insert Menu Creation URL in Company."'))
    #     response = requests.post(url=url, json=category_structure, headers=headers)
    #     return category_structure

 
    def action_auto_accept(self):
        today = datetime.now()
        pos_order = self.env['pos.order'].search([('id','=',self.id)])
        if pos_order:
            payment_method = self.env['pos.payment.method'].search([('name','=', self.payment_mode)])
            data=  {'amount': self.amount_total , 'payment_date': today, 'payment_method_id': payment_method.id , 'card_type': '', 'cardholder_name': '', 'transaction_id': '', 'payment_status': '', 'ticket': '', 'pos_order_id': self.id}
            pos_order.sudo().write({'state': 'paid','is_auto_accepted': True})
            self.add_payment(data)
        return True

    def action_accept(self):
        today = datetime.now()
        url = self.company_id.accept_url
        print("url----------------------",url)
        max_preparation_time = 0
        for x in self.lines:
            print('x..........', x.product_id)
            print("x..............preparation_time...", x.product_id.preparation_time) 
            if x.product_id.preparation_time > max_preparation_time:
                max_preparation_time = x.product_id.preparation_time

        print("Highest preparation time:", max_preparation_time)

        data = {"merchant_id": self.restaurant_id ,"order_id": self.order_id, "preparation_time": max_preparation_time}
        headers = {"X-Wera-Api-Key": "8cab0be2-1972-480d-a077-5f5a905806dc", "Content-Type": "application/json","Accept": "application/json"}
        if not url or url == False:
            raise ValidationError(_('"Insert Order Accept URL in Company."'))
        response = requests.post(url=url, json=data, headers=headers)
        print('response------------------------',response)
        if response:
            print("response get-------------------------")
            # payment_method = None
            # if self.payment_mode == 'CASH':
            #     payment_method = "Cash"
            # if self.payment_mode == "ONLINE":
            #     payment_method = "Bank"
            # payment_method = self.env['pos.payment.method'].search([('name','=', payment_method)])
            # data=  {'amount': self.amount_total , 'payment_date': today, 'payment_method_id': payment_method.id , 'card_type': '', 'cardholder_name': '', 'transaction_id': '', 'payment_status': '', 'ticket': '', 'pos_order_id': self.id}
            pos_order = self.env['pos.order'].search([('id','=',self.id)])
            # self.add_payment(data)
            # pos_order.action_pos_order_paid()
            pos_order.sudo().write({'state': 'paid'})
            pos_order.sudo().write({'is_accepted': True})
        return True

    def action_reject(self):
        self.state = 'cancel'

    def action_food_ready(self):
        url = self.company_id.food_ready_url
        data = {'merchand_id': self.restaurant_id ,'order_id': self.order_id}
        headers = {"charset": "utf-8", "Content-Type": "application/json"}
        response = requests.post(url=url, json=data, headers=headers)
        if not url or url == False:
            raise ValidationError(_('"Insert Food Ready URL in Company."'))
        if response:
            self.food_ready = True
        return True

    def action_get_delivery_agent(self):
        url = self.company_id.order_delivery_url
        data = {'merchand_id':self.restaurant_id ,'order_id': self.order_id}
        headers = {"charset": "utf-8", "Content-Type": "application/json"}
        response = requests.post(url=url, json=data, headers=headers)
        if not url or url == False:
            raise ValidationError(_('"Insert Get Delivery Agent URL in Company."'))
        return True

    def action_order_pickup(self):
        url = self.company_id.order_pickup_url
        data = {'merchand_id':self.restaurant_id ,'order_id': self.order_id, 'rider_name': self.rider_name ,"rider_number": self.rider_contact}
        headers = {"charset": "utf-8", "Content-Type": "application/json"}
        response = requests.post(url=url, json=data, headers=headers)
        if not url or url == False:
            raise ValidationError(_('"Insert Order Pickup URL in Company."'))
        if response:
            if self.enable_delivery == "1":
                self._create_order_picking()
                # self._generate_pos_order_invoice()
                self.order_pickup = True
        return True

    def action_get_customer_contact(self):
        url = self.company_id.get_customer_url
        data = {'order_id': self.order_id}
        headers = {"charset": "utf-8", "Content-Type": "application/json"}
        response = requests.post(url=url, json=data, headers=headers)
        if not url or url == False:
            raise ValidationError(_('"Insert Customer Contact URL in Company."'))
        # if response:
        return True