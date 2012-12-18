from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns =  patterns('sites.views',
    url(r'^help$', 'help', {}, name='help'),
    url(r'^about$', 'about', {}, name='about'),
    url(r'^contact$', 'contact', {}, name='contact'),
    url(r'^tos$', 'tos', {}, name='tos'),
    url(r'^returnspolicy$', 'returnspolicy', {}, name='returnspolicy'),
    url(r'^privacy$', 'privacy', {}, name='privacy'),
    url(r'^copyright$', 'copyright', {}, name='copyright'),
)