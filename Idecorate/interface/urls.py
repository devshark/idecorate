from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns =  patterns('interface.views',
    url(r'^$', 'home', {}, name='home'),
    url(r'^styleboard/$', 'styleboard', {}, name='styleboard'),
    url(r'^styleboard2/$', 'styleboard2', {}, name='styleboard2'),
    url(r'^styleboard/(?P<cat_id>\d+)$', 'styleboard', {}, name='styleboard_cat'),
    url(r'^styleboard_ajax/$', 'styleboard_ajax', {}, name='styleboard_ajax'),
    url(r'^styleboard_product_ajax/$', 'styleboard_product_ajax', {}, name='styleboard_product_ajax'),    
    url(r'^get_category_tree_ajax/$', 'get_category_tree_ajax', {}, name='get_category_tree_ajax'),
    url(r'^get_product_original_image/$', 'get_product_original_image', {}, name='get_product_original_image'),
    url(r'^styleboard_ajax/product_detail$', 'get_product_details', {}, name='get_product_details'),    
    url(r'^crop/(?P<id>.*)$', 'crop', {}, name='crop'),
    url(r'^crop_view/$', 'crop_view', {}, name='crop_view'),
    url(r'^set_product_positions/$', 'set_product_positions', {}, name='set_product_positions'),    
)