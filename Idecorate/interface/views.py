from django.contrib.auth.decorators import login_required
from django.shortcuts import HttpResponse, redirect, render_to_response
from django.contrib.auth import authenticate, login, logout
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.template import RequestContext

from category.services import get_categories
from cart.models import Product

def home(request):
	info = {}
	return render_to_response('interface/home.html',info,RequestContext(request))

def styleboard(request, cat_id=None):
	info = {}
	categories = get_categories(cat_id)
	if categories.count() > 0:
		info['categories'] = categories
	else:
		info['products'] = Product.objects.all()
	info['cat_id'] = cat_id
	return render_to_response('interface/styleboard.html', info,RequestContext(request))

def styleboard_ajax(request):
	return HttpResponse(200)
