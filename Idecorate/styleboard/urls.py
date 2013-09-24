from django.conf.urls import patterns, include, url
from django.views.generic.simple import redirect_to

urlpatterns = patterns('styleboard.views',
	url(r'^$', redirect_to, {'url': '/app/create/'}),
	url(r'^create/$', 'create', name='create'),
	url(r'^create/(?P<category_id>\d+)/$', 'create', name='categorize'),
    url(r'^create/(?P<category_id>\d+)/(?P<styleboard_id>\d+)/$', 'create', name='customize'),
    url(r'^sidebar_items/$', 'sidebar_items', {}, name='sidebar_items'),
    url(r'^get_all_categories/$', 'get_all_categories', {}, name='get_all_categories'),
    url(r'^get_all_products/$', 'get_all_products', {}, name='get_all_products'),
    url(r'^get_product_by_category/$', 'get_product_by_category', {}, name='get_product_by_category'),
)
