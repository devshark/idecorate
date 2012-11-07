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

from category.services import get_categories, get_cat, category_tree_crumb, search_category
from category.models import Categories
from cart.services import get_product
from cart.models import Product, CartTemp, ProductPopularity
from cart.services import generate_unique_id, clear_cart_temp
from django.conf import settings
from PIL import Image
import ImageDraw
from django.core.urlresolvers import reverse
import re
from admin.services import getExtensionAndFileName
from idecorate_settings.models import IdecorateSettings

def home(request):
	info = {}
	return render_to_response('interface/home.html',info,RequestContext(request))

@csrf_exempt
def styleboard(request, cat_id=None):

	"""
	check if category is exist
	"""
	if cat_id:
		if not get_cat(cat_id):
			return redirect('styleboard')

	sessionid = request.session.get('cartsession',None)
	if not sessionid: 
		session_id = generate_unique_id()
		request.session['cartsession'] = session_id

	info = {}

	idecorateSettings = IdecorateSettings.objects.get(pk=1)
	info['global_default_quantity'] = idecorateSettings.global_default_quantity
	info['global_guest_table'] = idecorateSettings.global_table	

	info['mode'] = 'styleboard'
	search = request.POST.get('search',None)
	if search:
		info['keyword'] = search
		info['keyword_cat'] = 0
		search_result_cat = search_category(search)
		if search_result_cat:
			cat_id = search_result_cat.id
			info['keyword_cat'] = cat_id
		info['mode'] = 'search'	
		info['category_count'] = 0
	else:
		categories = get_categories(cat_id)
		if categories.count() > 0:
			info['categories'] = categories

		info['category_count'] = categories.count()

	if not cat_id:
		cat_id = 0
	info['cat_id'] = cat_id

	product_positions = request.session.get('product_positions', None)

	if product_positions:
		info['product_positions'] = mark_safe(str(product_positions))
		#del request.session['product_positions']
	else:
		info['product_positions'] = mark_safe("''")

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

def search_product(request):
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
		ret['default_quantity'] = product.default_quantity
		ret['guest_table'] = product.guest_table.name

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

	info['filename'] = "%s?filename=%s" % (reverse('crop_view'), re.sub(r'\?[0-9].*','', str(id)))
	info['file_only'] = re.sub(r'\?[0-9].*','', str(id))

	return render_to_response('interface/iframe/crop.html', info,RequestContext(request))

def get_product_details(request):
	if request.method == 'POST':
		product_id = request.POST.get('prod_id')
		product = get_product(product_id)
		reponse_data = {}
		reponse_data['id'] = product.product.id
		reponse_data['original_image_thumbnail'] = product.product.original_image_thumbnail
		reponse_data['sku'] = product.product.sku
		reponse_data['name'] = product.product.name
		reponse_data['default_quantity'] = product.product.default_quantity
		reponse_data['price'] = product._unit_price
		reponse_data['currency'] = product.currency
		reponse_data['original_image'] = product.product.original_image
		guest_table = 'Table'
		try:
			guest_table = product.product.guest_table.name
		except:
			pass
		reponse_data['guest_table'] = guest_table
		return HttpResponse(simplejson.dumps(reponse_data), mimetype="application/json")
	else:
		return HttpResponseNotFound()

@csrf_exempt
def set_product_positions(request):

	ret = ""

	if request.method == 'POST':
		obj_counter = request.POST.get('obj_counter','')
		unique_identifier = request.POST.get('unique_identifier','')
		changes_counter = request.POST.get('changes_counter','')
		product_objects = request.POST.get('product_objects','')
		action_url = request.POST.get('action_url','')
		total = request.POST.get('total','')
		quantity = request.POST.get('quantity','')
		selected_prev_prod_qty = request.POST.get('selected_prev_prod_qty','')
		buy_table_html = request.POST.get('buy_table_html','')
		tables = request.POST.get('tables','')
		guests = request.POST.get('guests','')

		request.session['product_positions'] = {
			'obj_counter':str(obj_counter),
			'unique_identifier': str(unique_identifier),
			'changes_counter': str(changes_counter),
			'product_objects':str(product_objects),
			'action_url': str(action_url),
			'total': str(total),
			'quantity': str(quantity),
			'selected_prev_prod_qty': str(selected_prev_prod_qty),
			'buy_table_html': str(buy_table_html),
			'tables': str(tables),
			'guests': str(guests)
		}

		ret = obj_counter

	return HttpResponse(ret)
def styleboard2(request, cat_id=None):

	"""
	check if category is exist
	"""
	if cat_id:
		if not get_cat(cat_id):
			return redirect('styleboard')

	"""
	clear temporary cart

	sessionid = request.session.get('cartsession',None)
	if sessionid: 
		clear_cart_temp(sessionid)
		del request.session['cartsession']
	"""
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

	product_positions = request.session.get('product_positions', None)

	if product_positions:
		info['product_positions'] = mark_safe(str(product_positions))
		#del request.session['product_positions']
	else:
		info['product_positions'] = mark_safe("''")

	return render_to_response('interface/styleboard2.html', info,RequestContext(request))

def crop_view(request):

	filename = request.GET.get('filename','')

	img = Image.open("%s%s%s" % (settings.MEDIA_ROOT, "products/", filename))
	imgBackground = Image.new('RGBA', (400,400), (255, 255, 255, 0))
	imgBackground.paste(img, ((400 - img.size[0]) / 2, (400 - img.size[1]) /2 ))
	#newImg = imgBackground.crop(((400 - img.size[0]) / 2, (400 - img.size[1]) /2 , ((400 - img.size[0]) / 2) + img.size[0], ((400 - img.size[1]) / 2) + img.size[1]))

	response = HttpResponse(mimetype="image/png")
	#newImg.save(response, "PNG")
	imgBackground.save(response, "PNG")
	return response


def cropped(request):

	filename = request.GET.get('filename')

	img = Image.open("%s%s%s" % (settings.MEDIA_ROOT, "products/", filename))
	back = Image.new('RGBA', (400,400), (255, 255, 255, 0))
	back.paste(img, ((400 - img.size[0]) / 2, (400 - img.size[1]) /2 ))

	poly = Image.new('RGBA', (settings.PRODUCT_WIDTH,settings.PRODUCT_HEIGHT), (255, 255, 255, 0))
	pdraw = ImageDraw.Draw(poly)

	dimensionList = []
	splittedPosts = request.GET.get('dimensions').split(',')

	if request.GET.get('task') == 'poly':
		for splittedPost in splittedPosts:
			spl = splittedPost.split(':')
			dimensionList.append((float(spl[0]),float(spl[1])))

		pdraw.polygon(dimensionList,fill=(255,255,255,255),outline=(255,255,255,255))

	elif request.GET.get('task') == 'rect':
		for splittedPost in splittedPosts:
			dimensionList.append(float(splittedPost))
		pdraw.rectangle(dimensionList,fill=(255,255,255,255),outline=(255,255,255,255))


	poly.paste(back,mask=poly)
	response = HttpResponse(mimetype="image/png")

	newImg = poly.crop(((400 - img.size[0]) / 2, (400 - img.size[1]) /2 , ((400 - img.size[0]) / 2) + img.size[0], ((400 - img.size[1]) / 2) + img.size[1]))
	
	splittedName = getExtensionAndFileName(filename)

	if splittedName[1] == '.jpg':
		newImg.save(response, "JPEG")
	else:	
		newImg.save(response, "PNG")

	return response

def search_suggestions(request):
	if request.is_ajax():
		keyword = request.GET['term']
		products = Product.objects.filter(name__icontains=keyword or Q(description__icontains=keyword)).order_by('-id')[:7]
		categories = Categories.objects.filter(name__icontains=keyword)

		results = []

		for prod in products:
			prod_json = {}
			prod_json['id'] = prod.id
			prod_json['label'] = prod.name
			prod_json['category'] = "Suggestion"
			results.append(prod_json)

		for cat in categories:
			cat_json = {}
			cat_json['id'] = cat.id
			cat_json['label'] = cat.name
			cat_json['category'] = "Category"
			results.append(cat_json)

		return HttpResponse(simplejson.dumps(results), mimetype="application/json")
	else:
		return HttpResponseNotFound()