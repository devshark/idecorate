from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns =  patterns('customer.views',
    url(r'^login_signup/$', 'login_signup', {}, name='login_signup'),
    url(r'^logout/$', 'customer_logout', {}, name='logout'),
    url(r'^forgot/$', 'forgot_password', {}, name='forgot_password'),
    url(r'^profile/$', 'profile', {}, name='profile'),
    url(r'^edit_profile/$', 'edit_profile', {}, name='edit_profile'),
    url(r'^styleboard/save/$', 'save_styleboard', {}, name='save_styleboard'),
    url(r'^styleboard/view/(?P<sid>\d+)$', 'styleboard_view', {}, name='styleboard_view'),
    url(r'^styleboard/generate_styleboard_view/(?P<id>\d+)/(?P<w>\d+)/(?P<h>\d+)/$','generate_styleboard_view', {}, name='generate_styleboard_view'), 
    url(r'^social_redirect/$', 'social_redirect', {}, name='social_redirect'),
    url(r'^styleboard/generate_styleboard_template_view/(?P<id>\d+)/(?P<w>\d+)/(?P<h>\d+)/$','generate_styleboard_template_view', {}, name='generate_styleboard_template_view'),
)