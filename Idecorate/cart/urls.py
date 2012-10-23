from django.conf.urls import patterns, include, url
from django.conf import settings
from cart.views import shop

urlpatterns =  patterns('cart.views',
    url(r'^cart/add$', 'add_to_cart_ajax', {}, name='add_to_cart_ajax'),
    url(r'^cart/remove$', 'remove_from_cart_ajax', {}, name='remove_from_cart_ajax'),
    url(r'^cart/update$', 'update_cart', {}, name='update_cart'),
    url(r'^cart/checkout$', 'checkout', {}, name='checkout'),
)

urlpatterns += patterns('',
    url(r'^shop/', include(shop.urls)),
    )