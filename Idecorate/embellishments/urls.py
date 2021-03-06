from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns =  patterns('embellishments.views',
    url(r'^embellishments/upload$', 'upload_embellishment', {}, name='upload_embellishment'),#upload_form
    url(r'^embellishments/upload_action$', 'upload_embellishment_action', {}, name='upload_embellishment_action'),
    url(r'^embellishments/upload_progress$', 'upload_embellishment_progress', {}, name='upload_embellishment_progress'),
    url(r'^embellishments/template_upload_action$', 'template_upload_embellishment_action', {}, name='template_upload_embellishment_action'),
    url(r'^embellishments/save_template/$', 'save_styleboard_template', {}, name='save_styleboard_template'),
    url(r'^template/items$', 'get_template_items', {}, name='get_template_items'),
    
    
)