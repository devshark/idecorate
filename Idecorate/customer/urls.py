from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns =  patterns('customer.views',
    url(r'^login_signup/$', 'login_signup', {}, name='login_signup'),
    url(r'^logout/$', 'customer_logout', {}, name='logout'),
    url(r'^forgot_password/$', 'forgot_password', {}, name='forgot_password'),
    url(r'^profile/$', 'profile', {}, name='profile'),
    url(r'^customer_upload_image/$', 'customer_upload_image', {}, name='customer_upload_image'),
    url(r'^edit_profile/$', 'edit_profile', {}, name='edit_profile'),
    url(r'^styleboard/save/$', 'save_styleboard', {}, name='save_styleboard'),
    url(r'^styleboard/view/(?P<sid>\d+)$', 'styleboard_view', {}, name='styleboard_view'),
    url(r'^styleboard/generate_styleboard_view/(?P<id>\d+)/(?P<w>\d+)/(?P<h>\d+)/$','generate_styleboard_view', {}, name='generate_styleboard_view'), 
    url(r'^styleboard/generate_printable_styleboard/(?P<w>\d+)/(?P<h>\d+)/$','generate_printable_styleboard', {}, name='generate_printable_styleboard'), 
    url(r'^styleboard/generate_printable_styleboard/(?P<w>\d+)/(?P<h>\d+)/(?P<sbid>\d+)/$','generate_printable_styleboard', {}, name='generate_printable_styleboard'), 
    url(r'^social_redirect/$', 'social_redirect', {}, name='social_redirect'),
    url(r'^styleboard/generate_styleboard_template_view/(?P<id>\d+)/(?P<w>\d+)/(?P<h>\d+)/$','generate_styleboard_template_view', {}, name='generate_styleboard_template_view'),
    url(r'^keep_home_image/$', 'keep_home_image', {}, name='keep_home_image'),
    url(r'^saved_images/$', 'saved_images', {}, name='saved_images'),
    url(r'^orders/$', 'orders', {}, name='orders'),
    url(r'^view_order/$', 'view_order', {}, name='view_order'),
    url(r'^print_customer_sb/(?P<is_pdf>\d+)/(?P<sbid>\d+)/$', 'print_customer_sb', {}, name='print_customer_sb'),

    
)