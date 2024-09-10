{
    'name': 'Payment Provider: AddisPay',
    'version': '1.0',
    'category': 'Hidden',
    'summary': 'AddisPay Payment Gateway For Website',
    'description': "This module enables seamless payments through AddisPay, "
                   "ensuring secure and convenient online transactions.",
    'author': "Addis Systems/Ahmed M.",
    'company': 'Addis Systems',
    'maintainer': 'Abdulselam M.',
    'website': "https://www.addissystems.et/",
    'depends': ['payment'],
    'data': [
        'views/payment_addispay_templates.xml',
        'views/payment_method_data.xml',
        'views/payment_provider_views.xml',
        'views/payment_transaction_views.xml',
        'data/payment_provider_data.xml',
        'data/invoice_payment_link.xml'
    ],
  
    'license': 'LGPL-3',
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
}
