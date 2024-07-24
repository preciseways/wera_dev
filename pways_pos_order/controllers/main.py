from odoo import http, _
from odoo.http import request
import operator
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError
import json
import requests
import yaml

class PwaysPOSOrder(http.Controller):

    # #menu creation url
    # @http.route('/menu/creation', type='json', auth='public')
    # def pos_menu_creation(self):
    #     pos_category = self.env['product.category'].sudo().search([('parent_id','=',False)])
    #     pos_product = self.env['product.product'].sudo().search([( )])

    #trial url for testing
    @http.route('/order/test', type='json', auth='public')
    def post_order_test(self):
        print("Data------Order Test----------------")

        data_in_json = json.loads(request.httprequest.data)
        response = json.dumps({"code":1,"msg":'',"details":[]})
        return json.dumps({"code":1,"msg":'',"details":[]})  


        #order creation 
    @http.route('/post/order', type='json', auth='public')
    def set_order_value(self):
        print("Data------Order Creation-------Function Called---------")
        today = datetime.now()
        data_in_json = json.loads(request.httprequest.data)
        # print("Data------Order Creation----------------", data_in_json)
        pos_session = request.env['pos.session'].sudo().search([('custom_session', '=', True)])
        order_line = []
        addons_val = []
        variant_price = 0
        if 'order_items' in data_in_json:
            for item in data_in_json['order_items']:
                variant_line = []
                for x in item['variants']:
                    var_val = {
                        'variant_id': x['variant_id'],
                        'variant_name': x['variant_name'],
                        'size_id': x['size_id'],
                        'size_name': x['size_name'],
                        'price': x['price'],
                    }
                    variant_line.append((0, 0, var_val))
                    variant_price = x['price']
                
                product_id = request.env['product.template'].sudo().search([('id', '=', item['item_id'])])
                print("item id----------------------------------", item['wera_item_id'])
                print("item id----------------------------------", item['item_name'])
                print("product--------------------id-----------", product_id)
                print("variant--------------------id-----------", product_id.product_variant_ids)
                print("variant--------------------price---------------------------",variant_price)
                if len(product_id.product_variant_ids)  > 1:
                    for rec in product_id.product_variant_ids:
                        print("product price_extra---------------",rec.price_extra)
                        if rec.price_extra == variant_price:
                            print("product name------------------------------",rec.name)
                            product_id = rec
                        else:
                            product_id = rec
                else:
                    product_id = product_id.product_variant_ids
                line_val = {
                    'product_id': product_id.id or False,
                    'full_product_name': item['item_name'] or False,
                    'qty': item['item_quantity'] or False,
                    'price_unit': item['item_unit_price'] or False,
                    'price_subtotal': item['subtotal'] or False,
                    'price_subtotal_incl': item['subtotal'] or False,
                    # 'variants': variant_line
                }
                order_line.append((0, 0, line_val))
                if 'addons' in item:
                    print("finded addons---------------------------")
                    # addon_line = []
                    for addon in item['addons']:
                        addon_val = {
                            'addon_id': int(addon['addon_id']),
                            'name': addon['name'],
                            'price': addon['price'],
                            'discount': addon['discount']
                        }
                        addons_val.append((0, 0, addon_val))
        
        values = {
            'order_id': data_in_json.get('order_id') or False,
            'pos_order': True,
            'lines': order_line,
            'partner_id': 1,
            'session_id': pos_session.id,
            'amount_tax': data_in_json.get('packaging_cgst_percent') or False,
            'amount_total': data_in_json.get('gross_amount') or False,
            'amount_paid': 0,
            'amount_return': 0,
            'wera_order_id': data_in_json.get('external_order_id'),
            'restaurant_id': data_in_json.get('restaurant_id'),
            'restaurant_name': data_in_json.get('restaurant_name'),
            'order_from': data_in_json.get('order_from'),
            'enable_delivery': data_in_json.get('enable_delivery'),
            'payment_mode': data_in_json.get('payment_mode'),
            'customer_name': data_in_json['customer_details'].get('name') or False,
            'customer_phone_number': data_in_json['customer_details'].get('phone_number') or False,
            'order_otp': data_in_json.get('order_otp') or False,
            'is_auto_accepted': data_in_json.get('is_auto_accepted') or False,
            'is_accepted': data_in_json.get('is_accepted') or False,
            'password': data_in_json.get('password') or False,
            'order_otp': data_in_json.get('order_otp') or False,
            'company_id': 1,
            'pricelist_id': 1,
            'order_addons_ids': addons_val
        }
        
        order_created = request.env['pos.order'].sudo().search([('order_id', '=', data_in_json.get('order_id'))])
        if order_created:
            order_created.write(values)
            response = json.dumps({'state': 200, 'message': 'Successful', 'Order_id': order_created.order_id})
        else:
            pos_order = request.env['pos.order'].sudo().create(values)
            response = json.dumps({'state': 200, 'message': 'Successful', 'Order_id': pos_order.order_id})
            if not pos_order:
                response = json.dumps({"code": 2, "message": "Error"})
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