from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns =  patterns('interface.views',
    url(r'^$', 'home', {}, name='home'),
    url(r'^styleboard/$', 'styleboard', {}, name='styleboard'),
)