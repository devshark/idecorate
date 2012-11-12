from django.contrib.auth.decorators import login_required
from django.shortcuts import HttpResponse, redirect, render_to_response
from django.contrib.auth import authenticate, login, logout
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.template import RequestContext
from django.utils import simplejson
from django.http import HttpResponseNotFound
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.safestring import mark_safe
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from forms import LoginForm, SignupForm

def login_signup(request):

	info = {}
	login_form = LoginForm()
	signup_form = SignupForm()

	if request.method=="POST":
		action = request.POST['btnSubmit']
		if action=='Login':			
			login_form = LoginForm(request.POST)
			if login_form.is_valid():
				user = authenticate(username=login_form.cleaned_data['username'], password=login_form.cleaned_data['password'])
				if user is not None:
					login(request, user)
				else:
					messages.warning(request, _('Sorry we could not verify your email and password.'))
		else:
			login_form = SignupForm(request.POST)

	info['login_form'] = login_form
	info['signup_form'] = signup_form
	return render_to_response('customer/iframe/login_signup.html', info, RequestContext(request))
