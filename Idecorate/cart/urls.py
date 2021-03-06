from django.conf.urls import patterns, include, url
from django.conf import settings
from cart.views import shop

urlpatterns =  patterns('cart.views',
    url(r'^cart/$', 'cart', {}, name='cart'),
    url(r'^cart/add/$', 'add_to_cart_ajax', {}, name='add_to_cart_ajax'),
    url(r'^cart/remove/$', 'remove_from_cart_ajax', {}, name='remove_from_cart_ajax'),
    url(r'^cart/update/$', 'update_cart', {}, name='update_cart'),
    url(r'^cart/checkout/$', 'checkout', {}, name='checkout'),
    url(r'^cart/remove_all/$', 'remove_all_cart_ajax', {}, name='remove_all_cart_ajax'),
    url(r'^cart/styleboard/checkout/$', 'checkout_from_view_styleboard', {}, name='checkout_from_view_styleboard'),
    url(r'^cart/paypal_return_url/$', 'paypal_return_url', {}, name='paypal_return_url'),
    url(r'^cart/paypal_ipn/$', 'paypal_ipn', {}, name='paypal_ipn'),
    url(r'^cart/order_checkout_email/$', 'order_checkout_email', {}, name='order_checkout_email'),
    #url(r'^cart/payment$', 'payment', {}, name='payment'),
)


urlpatterns += patterns('',
    url(r'^shop/', include(shop.urls)),
)