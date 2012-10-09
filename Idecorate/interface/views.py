from django.contrib.auth.decorators import login_required
from django.shortcuts import HttpResponse, redirect, render_to_response
from django.contrib.auth import authenticate, login, logout
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.template import RequestContext
from django.utils import simplejson
from django.http import HttpResponseNotFound
from django.core import serializers

from category.services import get_categories, get_cat, category_tree_crumb
from cart.models import Product

def home(request):
	info = {}
	return render_to_response('interface/home.html',info,RequestContext(request))

def styleboard(request, cat_id=None):

	"""
	check if category is exist
	"""
	if cat_id:
		if not get_cat(cat_id):
			return redirect('styleboard')

	info = {}
	categories = get_categories(cat_id)
	if categories.count() > 0:
		info['categories'] = categories
	else:
		info['products'] = Product.objects.filter(categories__id=cat_id)
	info['cat_id'] = cat_id
	return render_to_response('interface/styleboard.html', info,RequestContext(request))

def styleboard_ajax(request):
	if request.method == "POST":
		cat_id = request.POST.get('cat_id',None)
		if cat_id == '':
			cat_id = None
		items = None
		categories = get_categories(cat_id)
		if categories.count() > 0:
			categories = categories.order_by('order')
			data = serializers.serialize("xml", categories)
		else:
			products = Product.objects.filter(categories__id=cat_id)
			data = serializers.serialize("xml", products)

		return HttpResponse(data, mimetype='application/xml')
	else:
		return HttpResponseNotFound()

def get_category_tree_ajax(request):
	if request.method == "POST":
		cat_id = request.POST.get('cat_id',None)
		if cat_id == '':
			cat_id = None
		cat_tree = category_tree_crumb(cat_id)
		return HttpResponse(cat_tree)
	else:
		return HttpResponseNotFound()