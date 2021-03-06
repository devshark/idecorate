from django.conf.urls import patterns, include, url
from django.conf import settings
from common.views import disconnect

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
    url(r'', include('cart.urls')),
    url(r'', include('embellishments.urls')),
    url(r'^disconnect/(?P<backend>[^/]+)/$', disconnect,
        name='socialauth_disconnect'),
    url(r'^disconnect/(?P<backend>[^/]+)/(?P<association_id>[^/]+)/$',
        disconnect, name='socialauth_disconnect_individual'),
    url(r'', include('social_auth.urls')),
    url(r'', include('sites.urls')),
    url(r'^app/', include('styleboard.urls')),
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
    url(r'^admin/admin_manage_embellishment/$', 'admin_manage_embellishment', {}, name='admin_manage_embellishment'),
    url(r'^admin/admin_delete_embellishment/(?P<id_delete>\d+)/$','admin_delete_embellishment', {}, name='admin_delete_embellishment'),
    url(r'^admin/admin_edit_embellishment/(?P<e_id>\d+)/$','admin_edit_embellishment', {}, name='admin_edit_embellishment'),
    url(r'^admin/admin_manage_font/$', 'admin_manage_font', {}, name='admin_manage_font'),
    url(r'^admin/admin_delete_font/(?P<id_delete>\d+)/$','admin_delete_font', {}, name='admin_delete_font'),
    url(r'^admin/admin_edit_font/(?P<t_id>\d+)/$','admin_edit_font', {}, name='admin_edit_font'),
    url(r'^admin/admin_manage_users/$', 'admin_manage_users', {}, name='admin_manage_users'),
    url(r'^admin/admin_stat_user/(?P<id>\d+)/$','admin_stat_user', {}, name='admin_stat_user'),
    url(r'^admin/admin_delete_user/(?P<id>\d+)/$','admin_delete_user', {}, name='admin_delete_user'),
    url(r'^admin/admin_edit_user/$','admin_edit_user', {}, name='admin_edit_user'),
    url(r'^admin/admin_add_user/$','admin_add_user', {}, name='admin_add_user'),
    url(r'^admin/manage_template/$','manage_template', {}, name='manage_template'),
    url(r'^admin/create_template/$','create_template', {}, name='create_template'),
    url(r'^admin/delete_template/$','delete_template', {}, name='delete_template'),
    url(r'^admin/manage_homepage$','manage_homepage', {}, name='manage_homepage'),
    url(r'^admin/upload_banner/$','homepage_upload_banner', {}, name='homepage_upload_banner'),
    url(r'^admin/upload_temp_banner$','upload_temp_banner', {}, name='upload_temp_banner'),
    url(r'^admin/edit_banner/(?P<hbid>\d+)/$','homepage_edit_banner', {}, name='homepage_edit_banner'),    
    url(r'^admin/delete_banner/(?P<hbid>\d+)/$','homepage_delete_banner', {}, name='homepage_delete_banner'), 
    url(r'^admin/is_keeped/$','homepage_is_keeped_banner', {}, name='homepage_is_keeped_banner'),   
    url(r'^admin/set_template_positions/$', 'set_template_positions', {}, name='set_template_positions'),
    url(r'^admin/new_template/$', 'new_template', {}, name='new_template'),
    url(r'^admin/info_graphic/$', 'manage_home_info_graphic', {}, name='manage_home_info_graphic'),
    url(r'^admin/info_graphic_upload/$', 'upload_info_graphic', {}, name='upload_info_graphic'),
    url(r'^admin/upload_temp_infographic/$', 'upload_temp_infographic', {}, name='upload_temp_infographic'),    
    url(r'^admin/set_infographic_status/$', 'set_infographic_status', {}, name='set_infographic_status'),
    url(r'^admin/management_reports/$', 'management_reports', {}, name='management_reports'),
    url(r'^admin/update_qty_sold/$', 'update_qty_sold', {}, name='update_qty_sold'),
    url(r'^admin/export_inventory_finance_report/$', 'export_inventory_finance_report', {}, name='export_inventory_finance_report'),
    url(r'^admin/csv_export_report/$', 'csv_export_report', {}, name='csv_export_report'),
    url(r'^admin/import_csv_report/$', 'import_csv_report', {}, name='import_csv_report'),
    url(r'^admin/admin_item_menu/$', 'item_menu', {}, name='admin_item_menu'),
    url(r'^admin/admin_delete_item_menu/(?P<id_delete>\d+)/$','admin_delete_item_menu', {}, name='admin_delete_item_menu'),
    url(r'^admin/admin_manage_styleboard/$', 'manage_styleboard', {}, name='admin_manage_styleboard'),
    url(r'^admin/update_styleboard_status/$', 'update_styleboard_status', {}, name='update_styleboard_status'),
    url(r'^admin/admin_manage_order/$', 'admin_manage_order', {}, name='admin_manage_order'),
    url(r'^admin/admin_view_order/$', 'admin_view_order', {}, name='admin_view_order'),
    url(r'^admin/admin_edit_order/$', 'admin_edit_order', {}, name='admin_edit_order'),
    url(r'^admin/admin_add_suggested_product/(?P<product_id>\d+)/$', 'admin_add_suggested_product', {}, name='admin_add_suggested_product'),
    url(r'^admin/admin_add_product_alternate_image/(?P<product_id>\d+)/$', 'admin_add_product_alternate_image', {}, name='admin_add_product_alternate_image'),
    url(r'^admin/admin_manage_product_images/(?P<product_id>\d+)/$', 'admin_manage_product_images', {}, name='admin_manage_product_images'),
    url(r'^admin/admin_edit_product_alternate_image/(?P<product_id>\d+)/(?P<alternate_id>\d+)/$', 'admin_edit_product_alternate_image', {}, name='admin_edit_product_alternate_image'),
    url(r'^admin/admin_manage_newsletter_subscribers/$', 'admin_manage_newsletter_subscribers', {}, name='admin_manage_newsletter_subscribers'),
    url(r'^admin/admin_download_newsletter_subscribers_csv/$', 'admin_download_newsletter_subscribers_csv', {}, name='admin_download_newsletter_subscribers_csv'),
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

urlpatterns += patterns('cms_item.views',
    url(r'^admin/flatpage_admin/$', 'flatpage_admin', {}, name='flatpage_admin'),
    url(r'^admin/add_page/$', 'add_flatpage', {}, name='add_flatpage'),
    url(r'^admin/edit_page/(?P<page_id>\d+)/', 'edit_flatpage', {}, name='edit_flatpage'),
    url(r'^admin/delete_flatpage/$', 'delete_flatpage', {}, name='delete_flatpage'),
)

urlpatterns += patterns('',
    ('^sites/', include('django.contrib.flatpages.urls')),
)

# urlpatterns += patterns('django.contrib.flatpages.views',
#     url(r'^about-us/$', 'flatpage', {'url': '/about-us/'}, name='about'),
#     url(r'^license/$', 'flatpage', {'url': '/license/'}, name='license'),
# )


"""
QUICK TIPS
"""
urlpatterns += patterns('admin.views',
    url(r'^admin/admin_manage_quick_tips/$', 'admin_manage_quick_tips', {}, name='admin_manage_quick_tips'),
    url(r'^admin/admin_add_quick_tip/$', 'admin_add_quick_tip', {}, name='admin_add_quick_tip'),
    url(r'^admin/admin_edit_quick_tip/(?P<tip_id>\d+)/$', 'admin_edit_quick_tip', {}, name='admin_edit_quick_tip'),
)


"""
HELP TOPICS
"""
urlpatterns += patterns('admin.views',
    url(r'^admin/admin_manage_help_topics/$', 'admin_manage_help_topics', {}, name='admin_manage_help_topics'),
    url(r'^admin/admin_add_help_topic/$', 'admin_add_help_topic', {}, name='admin_add_help_topic'),
    url(r'^admin/admin_edit_help_topic/(?P<topic_id>\d+)/$', 'admin_edit_help_topic', {}, name='admin_edit_help_topic'),
)


"""
NEWSLETTER TEMPLATES 
"""
urlpatterns += patterns('admin.views',
    url(r'^admin/admin_manage_newsletter_templates/$', 'admin_manage_newsletter_templates', {}, name='admin_manage_newsletter_templates'),
    url(r'^admin/admin_add_newsletter_template/$', 'admin_add_newsletter_template', {}, name='admin_add_newsletter_template'),
    url(r'^admin/admin_edit_newsletter_template/(?P<template_id>\d+)/$', 'admin_edit_newsletter_template', {}, name='admin_edit_newsletter_template'),    
    url(r'^admin/admin_upload_image/$', 'admin_upload_image', {}, name='admin_upload_image'),
    url(r'^admin/admin_send_newsletter/(?P<template_id>\d+)/$', 'admin_send_newsletter', {}, name='admin_send_newsletter'),    
)


"""
INSPIRATION
"""
urlpatterns += patterns('admin.views',
    url(r'^admin/admin_manage_inspirations/$', 'admin_manage_inspirations', {}, name='admin_manage_inspirations'),
    url(r'^admin/admin_add_inspiration/$', 'admin_add_inspiration', {}, name='admin_add_inspiration'),
)