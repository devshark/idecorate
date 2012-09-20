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
    url(r'', include('interface.urls'))
)

"""
	BOS URL
"""
urlpatterns += patterns('admin.views',
    url(r'^admin/$', 'admin', {}, name='admin'),
    url(r'^admin/admin_login/$', 'admin_login', {}, name='admin_login'),
    url(r'^admin/admin_logout/$', 'admin_logout', {}, name='admin_logout'),
    url(r'^admin/admin_manage_menu/$', 'admin_manage_menu', {}, name='admin_manage_menu'),
)
