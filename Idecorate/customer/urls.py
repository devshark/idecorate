from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns =  patterns('customer.views',
    url(r'^login_signup$', 'login_signup', {}, name='login_signup'),
    url(r'^logout$', 'customer_logout', {}, name='logout'),
    url(r'^forgot$', 'forgot_password', {}, name='forgot_password'),
)