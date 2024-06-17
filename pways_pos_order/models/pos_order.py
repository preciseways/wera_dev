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

    def pos_menu_creation(self):
        pos_category_ids = self.env['product.category'].sudo().search([('parent_id','=',False)])
        print("pos_category------------------------",pos_category_ids)
        pos_sub_category_ids = self.env['product.category'].sudo().search([('parent_id','in',pos_category_ids.ids)])
        print("pos sub category-----------------",pos_sub_category_ids)
        pos_product_ids = self.env['product.product'].sudo().search([('categ_id','in', pos_sub_category_ids.ids)])
        print("pos pos_product pos_product-----------------",pos_product_ids)
        main_categories = self.env['product.category'].sudo().search([('parent_id', '=', False)])
        category_structure = {"main_categories": []}

        for main_category in main_categories:
            # Fetch sub-categories for each main category
            sub_categories = self.env['product.category'].sudo().search([('parent_id', '=', main_category.id)])
            sub_category_list = []
            product_list = []
            product_list_without_sub = self.env['product.product'].sudo().search([('categ_id','=', main_category.id)])
            print("-----------------product_list_without_sub--------------------------",product_list_without_sub)
            for rec in product_list_without_sub:
                tax_list = []
                tax_list.append({
                    'cgst':rec.cgst,
                    'igst':rec.igst,
                    'sgst':rec.sgst
                })
                product_list.append({
                    "id": rec.id,
                    "name": rec.name,
                    "category_id": main_category.id ,
                    "price": rec.list_price,
                    'is_veg': rec.is_veg,
                    'in_stock': rec.in_stock,
                    "description": rec.description,
                    "gst_details": tax_list
                }) 
            for sub_category in sub_categories:
                # Fetch products for each sub-category
                products = self.env['product.product'].sudo().search([('categ_id', '=', sub_category.id)])
                    
                for product in products:
                    tax_list = []
                    tax_list.append({
                        'cgst':product.cgst,
                        'igst':product.igst,
                        'sgst':product.sgst
                    })
                    product_list.append({
                        "id": product.id,
                        "name": product.name,
                        "category_id": main_category.id ,
                        "sub_category_id": sub_category.id,
                        "price": product.list_price,
                        'is_veg': product.is_veg,
                        'in_stock': product.in_stock,
                        "description": product.description,
                        "gst_details": tax_list
                    })                
                sub_category_list.append({
                    "id": sub_category.id,
                    "name": sub_category.name,
                    "description": sub_category.description,
                    # "products": product_list
                })
            
            category_structure["main_categories"].append({
                "id": main_category.id,
                "name": main_category.name,
                "sub_categories": sub_category_list,
                'items': product_list
            })
        print("category_structure000-------------------",category_structure)

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
        data = {'merchand_id': self.restaurant_id ,'order_id': self.order_id}
        headers = {"charset": "utf-8", "Content-Type": "application/json"}
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
            # pos_order = self.env['pos.order'].search([('id','=',self.id)])
            # self.add_payment(data)
            # pos_order.action_pos_order_paid()
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