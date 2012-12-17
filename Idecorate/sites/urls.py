from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns =  patterns('sites.views',
    url(r'^help$', 'help', {}, name='help'),
)