from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'Idecorate.views.home', name='home'),
    # url(r'^Idecorate/', include('Idecorate.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^media/(?P<path>.*)$', "django.views.static.serve",{'document_root': settings.MEDIA_ROOT}),
    url(r'', include('interface.urls')),
    url(r'', include('customer.urls')),
    url(r'', include('cart.urls'))
)

"""
	BOS URL
"""
urlpatterns += patterns('admin.views',
    url(r'^admin/$', 'admin', {}, name='admin'),
    url(r'^admin/admin_login/$', 'admin_login', {}, name='admin_login'),
    url(r'^admin/admin_logout/$', 'admin_logout', {}, name='admin_logout'),
    url(r'^admin/admin_manage_menu/$', 'admin_manage_menu', {}, name='admin_manage_menu'),
    url(r'^admin/admin_delete_menu/(?P<id_delete>\d+)/(?P<menuType>\d+)/$','admin_delete_menu', {}, name='admin_delete_menu'),
    url(r'^admin/admin_create_product/$', 'admin_create_product', {}, name='admin_create_product'),
    url(r'^admin/admin_upload_product_image/$', 'admin_upload_product_image', {}, name='admin_upload_product_image'),
    url(r'^admin/admin_manage_product/$', 'admin_manage_product', {}, name='admin_manage_product'),
    url(r'^admin/admin_delete_product/(?P<id_delete>\d+)/$','admin_delete_product', {}, name='admin_delete_product'),
    url(r'^admin/admin_edit_product/(?P<prod_id>\d+)/$','admin_edit_product', {}, name='admin_edit_product'),
    url(r'^admin/edit_guests_tables/$', 'edit_guests_tables', {}, name='edit_guests_tables'),
    url(r'^admin/admin_manage_checkout/$', 'admin_manage_checkout', {}, name='admin_manage_checkout'),
    url(r'^admin/admin_upload_embellishment/$', 'admin_upload_embellishment', {}, name='admin_upload_embellishment'),
    url(r'^admin/admin_upload_embellishment_image/$', 'admin_upload_embellishment_image', {}, name='admin_upload_embellishment_image'),
    url(r'^admin/admin_manage_text_font/$', 'admin_manage_text_font', {}, name='admin_manage_text_font'),
    url(r'^admin/admin_generate_text_thumbnail/$', 'admin_generate_text_thumbnail', {}, name='admin_generate_text_thumbnail'),
    url(r'^admin/admin_upload_font/$', 'admin_upload_font', {}, name='admin_upload_font'),
)

"""
PRODUCT CATEGORY
"""
urlpatterns += patterns('category.views',
    url(r'^admin/category/$', 'category', {}, name='category'),
    url(r'^admin/category/(?P<cat_id>\d+)/', 'edit_category', {}, name='edit_category'),
    url(r'^admin/remove_category/$', 'remove_category', {}, name='remove_category'),
    url(r'^admin/order_category/$', 'order_category', {}, name='order_category'),
    url(r'^admin/category_thumbnail_upload/$', 'category_thumbnail_upload', {}, name='category_thumbnail_upload'),
    )