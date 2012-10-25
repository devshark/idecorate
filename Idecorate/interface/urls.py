from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns =  patterns('interface.views',
    url(r'^$', 'home', {}, name='home'),
    url(r'^styleboard/$', 'styleboard', {}, name='styleboard'),
    url(r'^styleboard/(?P<cat_id>\d+)$', 'styleboard', {}, name='styleboard_cat'),
    url(r'^styleboard_ajax/$', 'styleboard_ajax', {}, name='styleboard_ajax'),
    url(r'^styleboard_product_ajax/$', 'styleboard_product_ajax', {}, name='styleboard_product_ajax'),    
    url(r'^get_category_tree_ajax/$', 'get_category_tree_ajax', {}, name='get_category_tree_ajax'),
    url(r'^get_product_original_image/$', 'get_product_original_image', {}, name='get_product_original_image'),
    url(r'^crop/$', 'crop', {}, name='crop'),    
)