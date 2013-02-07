from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import login, REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

from social_auth.utils import sanitize_redirect, setting, backend_setting, clean_partial_pipeline
from social_auth.decorators import dsa_view
import re
from django.core.validators import email_re

DEFAULT_REDIRECT = setting('SOCIAL_AUTH_LOGIN_REDIRECT_URL',
                           setting('LOGIN_REDIRECT_URL'))
LOGIN_ERROR_URL = setting('LOGIN_ERROR_URL', setting('LOGIN_URL'))
PIPELINE_KEY = setting('SOCIAL_AUTH_PARTIAL_PIPELINE_KEY', 'partial_pipeline')

@login_required
@dsa_view()
def disconnect(request, backend, association_id=None):

	if request.user.is_authenticated():
		if request.user.password == "!" or not email_re.search(request.user.username):
			request.session['last_page_idecorate'] = '/edit_profile/'
			request.session['fb_auth_error'] = "Ensure that you have updated your email and set password before disconnecting to your %s account." % str(backend.AUTH_BACKEND.name).capitalize()
		else:
			backend.disconnect(request.user, association_id)
	else:
		backend.disconnect(request.user, association_id)
	url = request.REQUEST.get(REDIRECT_FIELD_NAME, '') or backend_setting(backend, 'SOCIAL_AUTH_DISCONNECT_REDIRECT_URL') or DEFAULT_REDIRECT
	return HttpResponseRedirect(url)
