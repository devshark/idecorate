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

from category.services import get_categories, get_cat, category_tree_crumb
from cart.services import get_product
from cart.models import Product
from cart.services import generate_unique_id, clear_cart_temp
from django.conf import settings
from PIL import Image

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

	"""
	clear temporary cart
	"""
	sessionid = request.session.get('cartsession',None)
	if sessionid: 
		clear_cart_temp(sessionid)
		del request.session['cartsession']

	info = {}
	categories = get_categories(cat_id)
	if categories.count() > 0:
		info['categories'] = categories

	info['category_count'] = categories.count()

	session_id = generate_unique_id()
	request.session['cartsession'] = session_id

	if not cat_id:
		cat_id = 0
	info['cat_id'] = cat_id
	return render_to_response('interface/styleboard.html', info,RequestContext(request))

def styleboard_product_ajax(request):
	if request.method == "POST":
		cat_id = request.POST.get('cat_id',None)

		product_list = Product.objects.filter(categories__id=cat_id, is_active=True, is_deleted=False)
		product_list = product_list.order_by('ordering')		
		product_counts = product_list.count()		
		offset = request.GET.get('offset',25)

		paginator = Paginator(product_list, offset)
		page = request.GET.get('page')
		try:
			products = paginator.page(page)
		except PageNotAnInteger:
			products = paginator.page(1)
		except EmptyPage:
			products = paginator.page(paginator.num_pages)

		reponse_data = {}

		json_data = serializers.serialize("json", products, fields=('id','name','original_image_thumbnail','sku'))
		reponse_data['data'] = json_data
		reponse_data['page_number'] = products.number
		reponse_data['num_pages'] = products.paginator.num_pages
		reponse_data['product_counts'] = product_counts

		return HttpResponse(simplejson.dumps(reponse_data), mimetype="application/json")
	return HttpResponseNotFound()


def styleboard_ajax(request):
	if request.method == "POST":
		cat_id = request.POST.get('cat_id',None)
		if cat_id == '':
			cat_id = None
		items = None
		categories = get_categories(cat_id)
		reponse_data = {}
		if categories.count() > 0:
			categories = categories.order_by('order')
			reponse_data['data'] = serializers.serialize("json", categories, fields=('id','name','thumbnail'))
		else:
			product_list = Product.objects.filter(categories__id=cat_id, is_active=True)
			product_counts = product_list.count()
			product_list = product_list.order_by('ordering')
			offset = request.GET.get('offset',25)

			paginator = Paginator(product_list, offset)
			page = request.GET.get('page')
			try:
				products = paginator.page(page)
			except PageNotAnInteger:
				products = paginator.page(1)
			except EmptyPage:
				products = paginator.page(paginator.num_pages)
				
			json_data = serializers.serialize("json", products, fields=('id','name','original_image_thumbnail','sku'))
			reponse_data['data'] = json_data
			reponse_data['page_number'] = products.number
			reponse_data['num_pages'] = products.paginator.num_pages
			reponse_data['product_counts'] = product_counts

		return HttpResponse(simplejson.dumps(reponse_data), mimetype="application/json")
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

@csrf_exempt
def get_product_original_image(request):

	if request.method == "POST":

		ret = {}

		product_id = request.POST.get('product_id')

		product = Product.objects.get(id=int(product_id))
		ret['original_image'] = product.original_image
		ret['no_background'] = product.no_background


		img = Image.open("%s%s%s" % (settings.MEDIA_ROOT, "products/", product.original_image))
		

		width, height = img.size

		ret['original_image_w'] = width
		ret['original_image_h'] = height

		img = Image.open("%s%s%s" % (settings.MEDIA_ROOT, "products/", product.no_background))
		width, height = img.size

		ret['no_background_w'] = width
		ret['no_background_h'] = height
		return HttpResponse(simplejson.dumps(ret), mimetype="application/json")

def crop(request, id):
	info = {}

	return render_to_response('interface/iframe/crop.html', info,RequestContext(request))
