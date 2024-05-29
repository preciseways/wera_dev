from odoo import http, _
from odoo.http import request
import operator
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError
import json
import requests
import yaml

class PwaysPOSOrder(http.Controller):

    #trial url for testing
    @http.route('/order/test', type='json', auth='public')
    def post_order_test(self):
        data_in_json = json.loads(request.httprequest.data)
        response = json.dumps({"code":1,"msg":'',"details":[]})
        return json.dumps({"code":1,"msg":'',"details":[]})  


    #order creation 
    @http.route('/post/order', type='json', auth='public')
    def set_order_value(self):
        today = datetime.now()
        data_in_json = json.loads(request.httprequest.data)
        print("Data------Order Creation----------------",data_in_json)
        pos_session = request.env['pos.session'].sudo().search([('custom_session','=',True)])
        order_line = []
        for item in data_in_json['order_items']:
            variant_line = []
            for x in item['variants']:
                var_val= {
                'variant_id': x['variant_id'],
                'variant_name': x['variant_name'],
                'size_id': x['size_id'],
                'size_name': x['size_name'],
                'price': x['price'],
                }
                variant_line.append((0,0, var_val))
            line_val = {
                'product_id': item['item_id'] or False,
                'full_product_name': item['item_name'] or False,
                'qty': item['item_quantity'] or False,
                'price_unit': item['item_unit_price'] or False,
                'price_subtotal': item['subtotal'] or False,
                'price_subtotal_incl': item['subtotal'] or False
            }
            order_line.append((0, 0, line_val))
        values= {
            'order_id': data_in_json['order_id'] or False,
            'pos_order': True,
            'lines': order_line,
            'partner_id': 1,
            'session_id': pos_session.id,
            'amount_tax': data_in_json['order_packaging_sgst_percent'] or False,
            'amount_total': 1000,
            'amount_paid': 0,
            'amount_return': 0,
            'wera_order_id': data_in_json.get('external_order_id'),
            'restaurant_id': data_in_json.get('restaurant_id'),
            'restaurant_name': data_in_json.get('restaurant_name'),
            'order_from': data_in_json.get('order_from'),
            'enable_delivery': data_in_json.get('enable_delivery'),
            'payment_mode': data_in_json.get('payment_mode'),
            'customer_name': data_in_json['customer_details']['name'] or False,
            'customer_phone_number': data_in_json['customer_details']['phone_number'] or False,
            'order_otp' : data_in_json['order_otp'] or False,
            'is_auto_accepted': data_in_json['is_auto_accepted'] or False,
            'is_accepted': data_in_json['is_accepted'] or False,
            'password': data_in_json['password'] or False,
            'order_otp': data_in_json['order_otp'] or False,
            'company_id': data_in_json['company_id'] or False,
            'pricelist_id': data_in_json['pricelist_id'] or False,
            # 'total_cgst': data_in_json.get('order_cgst'),
            # 'total_sgst': data_in_json.get('order_sgst'),
            # 'order_packaging': data_in_json.get('order_packaging'),
            # 'order_packaging_cgst': data_in_json.get('order_packaging_cgst'),
            # 'order_packaging_sgst': data_in_json.get('order_packaging_sgst'),
            # 'order_packaging_cgst_percent': data_in_json.get('order_packaging_cgst_percent'),
            # 'order_packaging_sgst_percent': data_in_json.get('order_packaging_sgst_percent'),
            # 'order_discount': data_in_json.get('discount'),
            # 'delivery_charge': data_in_json.get('delivery_charge'),
            # 'customer_email': data_in_json['customer_details']['email'] or False,
            # 'customer_address': data_in_json['customer_details']['address'] or False,
            # 'delivery_area': data_in_json['customer_details']['delivery_area'] or False,
            # 'address_instructions': data_in_json['customer_details']['address_instructions'] or False,
            # 'wera_item_id': data_in_json.get('wera_item_id'),
            # 'item_id': data_in_json.get('item_id'),
            # 'item_name': data_in_json.get('item_name'),
            # 'item_unit_price': data_in_json.get('item_unit_price'),
            # 'subtotal': data_in_json.get('subtotal'),
            # 'discount': data_in_json.get('order_discount'),
            # 'item_quantity': data_in_json.get('item_quantity'),
            # 'size_id': data_in_json.get('size_id'),
            # 'size_name': data_in_json.get('size_name'),
            # 'size_price': data_in_json.get('price'),
            # 'size_cgst': data_in_json.get('size_cgst'),
            # 'size_sgst': data_in_json.get('size_sgst'),
            # 'size_cgst_percent': data_in_json.get('size_cgst_percent'),
            # 'size_sgst_percent': data_in_json.get('size_sgst_percent'),
            # 'addons_id': data_in_json.get('addon_id'),
            # 'addons_name': data_in_json.get('addon_name'),
            # 'addons_price': data_in_json.get('addon_price'),
            # 'addons_cgst': data_in_json.get('addon_cgst'),
            # 'addons_sgst': data_in_json.get('addon_sgst'),
            # 'addons_cgst_percent': data_in_json.get('addon_cgst_percent'),
            # 'addons_sgst_percent': data_in_json.get('addon_sgst_percent')
        }
        order_created = request.env['pos.order'].sudo().search([('order_id','=',data_in_json.get('order_id'))])
        if order_created:
            order_created.write(values)
            response = json.dumps({'state':200, 'message': 'Successful','Order_id': order_created.order_id})
        else:
            pos_order = request.env['pos.order'].sudo().create(values)
            response = json.dumps({'state':200, 'message': 'Successful','Order_id': pos_order.order_id})
            if not pos_order:
                response = json.dumps({"code": 2 ,"message": "Error"})
        return response

    #action pos order cancel
    @http.route('/order/cancel' ,type='json', auth='public')
    def pos_order_cancel(self):
        data_in_json = json.loads(request.httprequest.data)
        print("Data-------------Order Cancel-----------------",data_in_json)
        pos_order = request.env['pos.order'].sudo().search([('order_id','=',data_in_json.get('order_id'))])
        if pos_order:
            pos_order.sudo().write({'rejection_reason': data_in_json.get('reason')})
            pos_order.action_reject()
            if pos_order.state == "cancel":
                response = json.dumps({"code":1,"msg":'',"details":[]})
            else:
                response = json.dumps({"code":2,"msg":'Could not update status at Swiggy/Zomato',"details":[]})
        else:
            response = json.dumps({"code":2,"msg":'Could not update status at Swiggy/Zomato',"details":[]})
        return response

    #action pos order auto accept
    @http.route('/order/auto/accept', type='json', auth='public')
    def pos_order_auto_accept(self):
        data_in_json = json.loads(request.httprequest.data)
        print("Data---------------ORDER--............ACCEPT-------------------",data_in_json)
        pos_order = request.env['pos.order'].sudo().search([('order_id','=',data_in_json.get('order_id'))])
        if pos_order:
            pos_order.sudo().write({'accept_reason': data_in_json.get('reason')})
            pos_order.action_auto_accept()
            if pos_order.state == "paid":
                response = json.dumps({"code":1,"msg":'',"details":[]})
            else:
                response = json.dumps({"code":2,"msg":'Could not update status at Swiggy/Zomato',"details":[]})
        else:
            response = json.dumps({"code":2,"msg":'Could not update status at Swiggy/Zomato',"details":[]})
        return response


    #action pos order push delivery agent
    @http.route('/order/push/delivery-agent', type='json', auth='public')
    def pos_order_push_delivery_agent(self):
        database_name = json.loads(request.httprequest.data)
        print("Data----------------PUSH DELIVERY AGENT--------------------------",database_name)
        pos_order = request.env['pos.order'].sudo().search([('order_id','=',database_name.get('order_id'))])
        if pos_order:
            if database_name.get('rider_name') and database_name.get('rider_number') and database_name.get('rider_status'):
                pos_order.sudo().write({'delivery_agent_assign': True,'rider_name': database_name.get('rider_name'),'rider_contact': database_name.get('rider_number'),'rider_status': database_name.get('rider_status')})
                response = json.dumps({"code":1,"msg":'',"details":[]})
            else:
                response = json.dumps({"code":2,"msg":'Could not update status at Swiggy/Zomato',"details":[]})
        else:
            response = json.dumps({"code":2,"msg":'Could not update status at Swiggy/Zomato',"details":[]})
        return response




#ORDER TESTING URL FOR DEMO 


    #order accept 
    @http.route('/pos/v2/order/accept', type='json', auth='public')
    def pos_url_order_accept(self):
        data_in_json = json.loads(request.httprequest.data)
        pos_order = request.env['pos.order'].sudo().search([('wera_order_id','=', data_in_json.get('order_id'))])
        if pos_order:
            pos_order.action_accept()
            if pos_order.state == 'paid':
                response = json.dumps({"code":1,"msg":'',"details":[]})
            else:
                response = json.dumps({"code":2,"msg":'Could not update status at Swiggy/Zomato',"details":[]})
        else:
            response = json.dumps({"code":2,"msg":'Could not update status at Swiggy/Zomato',"details":[]})
        return response

    #order reject
    @http.route('/pos/v2/order/reject', type='json', auth='public')
    def pos_url_order_reject(self):
        data_in_json = json.loads(request.httprequest.data)
        pos_order = request.env['pos.order'].sudo().search([('id','=', data_in_json.get('order_id'))])
        if pos_order:
            pos_order.sudo().write({'state': 'cancel','rejection_reason': data_in_json.get('rejection_id')})
            if pos_order.state == 'cancel':
                response = json.dumps({"code":1,"msg":'',"details":[]})
            else:
                response = json.dumps({"code":2,"msg":'Could not update status at Swiggy/Zomato',"details":[]})
        else:
            response = json.dumps({"code":2,"msg":'Could not update status at Swiggy/Zomato',"details":[]})
        return response

    #action Food Ready
    @http.route('/pos/v2/order/food-ready', type='json', auth='public')
    def pos_order_url_food_ready(self):
        data_in_json = json.loads(request.httprequest.data)
        pos_order = request.env['pos.order'].sudo().search([('id','=', data_in_json.get('order_id'))])
        if pos_order:
            pos_order.action_food_ready()
            if pos_order.food_ready == True:
                response = json.dumps({"code":1,"msg":'',"details":[]})
            else:
                response = json.dumps({"code":2,"msg":'Could not update status at Swiggy/Zomato',"details":[]})
        else:
            response = json.dumps({"code":2,"msg":'Could not update status at Swiggy/Zomato',"details":[]})
        return response


    #action call swiggy customer support
    @http.route('/pos/v2/order/callsupport', type='json', auth='public')
    def pos_order_url_call_support(self):
        data_in_json = json.loads(request.httprequest.data)
        pos_order = request.env['pos.order'].sudo().search([('id','=', data_in_json.get('order_id'))])
        if data_in_json.get('remark'):
            pos_order.write({'order_remarks': data_in_json.get('remark')})
        if pos_order:
            response = json.dumps({"code":1,"msg":'',"details":[]})
        else:
            response = json.dumps({"code":2,"msg":'Could not update status at Swiggy/Zomato',"details":[]})
        return response

    #action get Delivery Agent
    @http.route('/pos/v2/order/getde', type='json', auth='public')
    def pos_order_url_delivery_agent(self):
        data_in_json = json.loads(request.httprequest.data)
        pos_order = request.env['pos.order'].sudo().search([('id','=', data_in_json.get('order_id'))])
        if data_in_json.get('remark'):
            pos_order.write({'order_remarks': data_in_json.get('remark')})
        if pos_order:
            response = json.dumps({"code":1,"msg":'',"details":[{'rider_name': pos_order.rider_name,"rider_number": pos_order.rider_contact, "rider_status": pos_order.rider_status,"time_to_arrive": pos_order.time_to_arrive}]})
        else:
            response = json.dumps({"code":2,"msg":'Could not update status at Swiggy/Zomato',"details":[]})
        return response

  
    #action order pickuped by Delivery Agent
    @http.route('/pos/v2/order/pickedup', type='json', auth="public")
    def pos_order_url_pickup_delivery_agent(self): 
        data_in_json = json.loads(request.httprequest.data)
        pos_order = request.env['pos.order'].sudo().search([('id','=', data_in_json.get('order_id'))])
        if pos_order:
            if pos_order.enable_delivery == "1":
                response = json.dumps({"code":1,"msg":'',"details":[]})
            else:
                response = json.dumps({"code":2,"msg":'Could not update status at Swiggy',"details":[]})
        else:
            response = json.dumps({"code":2,"msg":'Could not update status at Swiggy',"details":[]})
        return response

    #action get customer name
    @http.route('/pos/v2/order/getcustomernumber', type="json", auth="public")
    def pos_order_url_get_customer_contact(self):
        data_in_json = json.loads(request.httprequest.data)
        pos_order = request.env['pos.order'].sudo().search([('id','=', data_in_json.get('order_id'))])
        if pos_order:
            if pos_order.order_from == "Swiggy":
                response = json.dumps({"code":1,"msg":'',"details": {"number": pos_order.customer_phone_number,"pin": "664908"}})
            else:
                response = json.dumps({"code":1,"msg":'',"details": {"number": pos_order.customer_phone_number}})
        else:
            response = json.dumps({"code":2,"msg":'Could not update status at Swiggy',"details":[]})
        return response