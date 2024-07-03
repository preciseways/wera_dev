{
    'name': 'Preciseways POS Order',
    'description': '''Preciseways POS Order''',
    'author': 'Preciseways',
    'depends': [
        'point_of_sale', 'portal', 'sale_management', 'product'
    ],
    'data': [ 
            'security/ir.model.access.csv',
            'wizard/pos_order_rejection_view.xml',
            'wizard/pos_partner_contact_view.xml',
            'wizard/pos_addon_product_view.xml',
            'views/pos_addon_group_view.xml',
            'views/pos_order_view.xml',
            'views/pos_order_line_view.xml',
            'views/pos_config_view.xml',
            'views/pos_online_order_view.xml',
         ],

    'assets': {
        'web.assets_backend': [
            'pways_pos_order/static/src/css/custome_button_style.css',
        ],
    },
}
