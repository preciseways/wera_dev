{
    'name': 'Wera POS Order',
    'description': '''Wera POS Order''',
    'depends': [
        'point_of_sale', 'portal', 'sale_management', 'product'
    ],
    'data': [ 
            'security/ir.model.access.csv',
            'data/weekday_data.xml',
            'wizard/pos_order_rejection_view.xml',
            'wizard/pos_partner_contact_view.xml',
            'wizard/pos_addon_product_view.xml',
            'views/pos_config_view.xml',
            'views/pos_addon_group_view.xml',
            'views/pos_order_view.xml',
            'views/pos_order_line_view.xml',
            'views/pos_online_order_view.xml',
         ],

    'assets': {
        'web.assets_backend': [
            'roryx_online_order_V17/static/src/css/custome_button_style.css',
        ],
        'point_of_sale._assets_pos': [
            'roryx_online_order_V17/static/src/js/notification.js',
            'roryx_online_order_V17/static/src/js/pos_screen_order.js',
            'roryx_online_order_V17/static/src/js/control_button.js',
            'roryx_online_order_V17/static/src/xml/pos_screen_order_view.xml',            
            'roryx_online_order_V17/static/src/xml/controll_button_view.xml',
        ]
    },
}
