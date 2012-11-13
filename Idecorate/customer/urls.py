from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns =  patterns('customer.views',
    url(r'^user/login_signup$', 'login_signup', {}, name='login_signup'),
    url(r'^user/logout$', 'customer_logout', {}, name='logout'),
)