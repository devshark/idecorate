from django.contrib.auth.decorators import login_required
from django.shortcuts import HttpResponse, redirect, render_to_response
from django.contrib.auth import authenticate, login, logout
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.template import RequestContext

def home(request):
	info = {}
	return render_to_response('interface/home.html',info,RequestContext(request))

def styleboard(request):
	info= {}
	return render_to_response('interface/styleboard.html', info,RequestContext(request))
