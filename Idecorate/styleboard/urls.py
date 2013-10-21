from django.conf.urls import patterns, include, url
from django.views.generic.simple import redirect_to

urlpatterns = patterns('styleboard.views',
	url(r'^$', redirect_to, {'url': '/app/create/'}),
	url(r'^create/$', 'create', name='create'),
	url(r'^create/(?P<category_id>\d+)/$', 'create', name='categorize'),
    url(r'^create/(?P<category_id>\d+)/(?P<styleboard_id>\d+)/$', 'create', name='customize'),
    url(r'^crop/(?P<product_id>\d+)/(?P<is_transparent>\d+)/$', 'crop', {}, name='crop'),
    url(r'^crop_image/$', 'crop_image', {}, name='crop_image'),
    url(r'^get_categories/$', 'get_categories', {}, name='get_categories'),
    url(r'^get_products/$', 'get_products', {}, name='get_products'),
    url(r'^get_product_info/$', 'get_product_info', {}, name='get_product_info'),
    url(r'^get_product_info/(?P<product_id>\d+)/$', 'get_product_info', {}, name='get_product_info'),
    url(r'^zoom_product_image/(?P<object_id>\d+)/(?P<size>\d+)/(?P<is_product>\d+)/$', 'zoom_product_image', {}, name='zoom_product_image'),
    url(r'^get_embellishment_categories/$', 'get_embellishment_categories', {}, name='get_embellishment_categories'),
    url(r'^get_embellishments/$', 'get_embellishments', {}, name='get_embellishments'),
    url(r'^get_templates/$', 'get_templates', {}, name='get_templates'),
    url(r'^sidebar_items/$', 'sidebar_items', {}, name='sidebar_items'),
)
