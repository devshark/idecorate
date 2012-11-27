from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns =  patterns('embellishments.views',
    url(r'^embellishments/upload$', 'upload_embellishment', {}, name='upload_embellishment'),#upload_form
    url(r'^embellishments/upload_action$', 'upload_embellishment_action', {}, name='upload_embellishment_action'),
    url(r'^embellishments/upload_progress$', 'upload_embellishment_progress', {}, name='upload_embellishment_progress'),
)