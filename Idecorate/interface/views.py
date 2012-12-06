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

from category.services import get_categories, get_cat, category_tree_crumb, search_category, get_cat_ids
from category.models import Categories
from cart.services import get_product
from cart.models import Product, CartTemp, ProductPopularity
from cart.services import generate_unique_id, clear_cart_temp, add_to_cart
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
from django.core.urlresolvers import reverse
import re
from admin.services import getExtensionAndFileName
from idecorate_settings.models import IdecorateSettings
from admin.models import TextFonts, Embellishments, EmbellishmentsType
from customer.services import get_user_styleboard, get_styleboard_cart_item

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

	info['max_emb_size'] = settings.MAX_UPLOAD_EMBELLISHMENT_IMAGE_SIZE
	info['text_items'] = TextFonts.objects.filter(is_active=True, is_deleted=False)

	"""
	save styleboard personalize or modify
	"""
	try:
		del request.session['customer_styleboard']
	except:
		pass
	sbid = request.GET.get('sbid',None)
	if sbid:
		personalize_styleboard = get_user_styleboard(None, sbid)
		if personalize_styleboard:
			if personalize_styleboard.user.id:
				clear_styleboard_session(request)			
				info['save_styleboard'] = personalize_styleboard
				info['personalize_item'] = mark_safe(personalize_styleboard.styleboard_item.item.replace("'","\\'"))
				info['global_default_quantity'] = personalize_styleboard.styleboard_item.item_guest
				info['global_guest_table'] = personalize_styleboard.styleboard_item.item_tables			
				if request.user.is_authenticated():					
					if int(personalize_styleboard.user.id) == int(request.user.id):
						request.session['customer_styleboard'] = personalize_styleboard
				else:
					request.session['personalize_styleboard'] = personalize_styleboard					

	return render_to_response('interface/styleboard2.html', info,RequestContext(request))

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

	info['filename'] = "%s?filename=%s" % (reverse('crop_view'), re.sub(r'\?[0-9].*','', str(id)).replace('/',''))
	info['file_only'] = re.sub(r'\?[0-9].*','', str(id)).replace('/','')

	task = request.GET.get('task',None)
	otherdata = request.GET.get('otherdata',None)
	dimensions = request.GET.get('dimensions', None)

	info['pre_task'] = task if task else ''
	info['pre_otherdata'] = otherdata if otherdata else ''
	info['pre_dimensions'] = dimensions if dimensions else ''

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
		embellishment_objects = request.POST.get('embellishment_objects','')
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
			'embellishment_objects': str(embellishment_objects),
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
		keyword = request.GET.get('term',None)
		if keyword:
			products = Product.objects.filter(Q(name__icontains=keyword) | Q(description__icontains=keyword), is_active=True, is_deleted=False).order_by('-id')[:7]			
			categories = Categories.objects.filter(name__icontains=keyword, deleted=False).order_by('-created')[:7]

			results = []

			for prod in products:
				prod_json = {}
				prod_json['id'] = prod.id
				prod_json['label'] = prod.name
				prod_json['category'] = "Products"
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

def search_products(request):
	if request.method == "POST":
		cat_id = request.POST.get('cat_id',None)
		search_keyword = request.POST.get('search_keyword',None)

		if cat_id != '0':
			cat_ids = get_cat_ids(cat_id)			
			product_list = Product.objects.filter(categories__id__in=cat_ids, is_active=True, is_deleted=False, categories__deleted=0)
			product_list = product_list.order_by('ordering').distinct()	
		else:
			keywords = search_keyword.split(' ')

			q = None
			for k in keywords:

				if k.strip() != "":
					if q is not None:
						q.add(Q(name__icontains=k), Q.OR)
					else:
						q = Q(name__icontains=k)

			for l in keywords:
				if l.strip() != "":
					if q is not None:
						q.add(Q(description__icontains=l), Q.OR)
					else:
						q = Q(description__icontains=l)
			cats_ids = []
			categories = Categories.objects.filter(name__icontains=search_keyword, deleted=False)
			if categories.count() > 0:
				for cat in categories:
					cats_ids += get_cat_ids(cat.id)
				q.add(Q(categories__id__in=cats_ids), Q.OR)

			product_list = Product.objects.filter(q).distinct()
			product_list = product_list.filter(categories__deleted=0, is_active=True, is_deleted=False)
			product_list = product_list.distinct()
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

def generate_text(request):
	#parameters
	font_size = request.GET.get('font_size','')
	image_text = request.GET.get('font_text','')
	font_color = request.GET.get('font_color','')
	font_thumbnail = request.GET.get('font_thumbnail','0')
	font_id = request.GET.get('font_id','')

	fontObj = TextFonts.objects.get(id=int(font_id))

	font_color = (int(font_color[0:3]), int(font_color[3:6]), int(font_color[6:9]))
	#load font with size
	font = ImageFont.truetype("%s%s%s" % (settings.MEDIA_ROOT, "fonts/", fontObj.font), int(font_size))
	
	splittedTexts = image_text.split("\n")
	totalHeight = 0
	upperWidth = 0
	heightList = [0]


	#compute the final width and height first
	for splittedText in splittedTexts:
		textSize = font.getsize(splittedText)
		totalHeight += textSize[1]
		heightList.append(totalHeight)

		if upperWidth == 0:
			upperWidth = textSize[0]
		else:
			if textSize[0] > upperWidth:
				upperWidth = textSize[0]

	#image with background transparent
	img = Image.new("RGBA", (upperWidth, totalHeight), (255,255,255, 0))

	#create draw object	
	draw = ImageDraw.Draw(img)

	#draw the text
	ctr = 0

	for splittedText in splittedTexts:
		#draw text
		draw.text((0,heightList[ctr]), splittedText, font_color, font=font)
		ctr += 1

	if font_thumbnail == "0":
		#not thumbnail
		response = HttpResponse(mimetype="image/png")
		img.save(response, "PNG")
	else:
		#create thumbnail 
		img.thumbnail((int(font_size),int(font_size)),Image.ANTIALIAS)
		bgImg = Image.new('RGBA', (int(font_size),int(font_size)), (255, 255, 255, 0))
		bgImg.paste(img,((int(font_size) - img.size[0]) / 2, (int(font_size) - img.size[1]) / 2))

		response = HttpResponse(mimetype="image/jpg")
		bgImg.save(response, "JPEG")

	return response

def generate_embellishment(request):

	embellishment_id = request.GET.get('embellishment_id',0)
	embellishment_color = request.GET.get('embellishment_color','')
	embellishment_thumbnail = request.GET.get('embellishment_thumbnail','0')
	embellishment_size = request.GET.get('embellishment_size','')

	embellishment_color = (int(embellishment_color[0:3]), int(embellishment_color[3:6]), int(embellishment_color[6:9]))

	directory = ""
	retImage = None

	embObj = Embellishments.objects.get(id=int(embellishment_id))

	if embObj.e_type.id == 1:
		directory = "images"
	elif embObj.e_type.id == 2:
		directory = "textures"
	elif embObj.e_type.id == 3:
		directory = "patterns"
	elif embObj.e_type.id == 4:
		directory = "shapes"
	elif embObj.e_type.id == 5:
		directory = "borders"

	img = Image.open("%s%s%s" % (settings.MEDIA_ROOT, "embellishments/%s/" % directory, embObj.image)).convert("RGBA")
	newImg = Image.new("RGBA", img.size, embellishment_color)
	r, g, b, alpha = img.split()

	response = HttpResponse(mimetype="image/png")

	if embObj.e_type.id == 1 or embObj.e_type.id == 5:
		retImage = img
	elif embObj.e_type.id == 3:
		newImg.paste(img, mask=b)
		retImage = newImg
	elif embObj.e_type.id == 2 or embObj.e_type.id == 4:
		img.paste(newImg, mask=alpha)
		retImage = img 

	if embellishment_thumbnail == "0":
		#not thumbnail
		retImage.save(response, "PNG")
	else:
		#return thumbnail
		retImage.thumbnail((int(embellishment_size),int(embellishment_size)),Image.ANTIALIAS)
		bgImg = Image.new('RGBA', (int(embellishment_size),int(embellishment_size)), (255, 255, 255, 0))
		bgImg.paste(retImage,((int(embellishment_size) - retImage.size[0]) / 2, (int(embellishment_size) - retImage.size[1]) / 2))
		bgImg.save(response, "PNG")

	return response

def clear_styleboard_session(request):
	try:
		del request.session['customer_styleboard']
	except:
		pass

	try:		
		clear_cart_temp(request.session['cartsession'])
		del request.session['cartsession']
	except:
		pass

	try:
		del request.session['product_positions']
	except:
		pass

def new_styleboard(request):
	clear_styleboard_session(request)
	return redirect('styleboard')

@csrf_exempt
def get_embellishment_items(request):
	if request.is_ajax():
		typ = request.POST['type']
		offset = request.GET.get('offset',25)
		page = request.GET.get('page')
		if typ != 'text':
			embellishment_items = Embellishments.objects.filter(e_type__id=typ, is_active=True, is_deleted=False)

			item_counts = embellishment_items.count()
			paginator = Paginator(embellishment_items, offset)			
			try:
				embellishments = paginator.page(page)
			except PageNotAnInteger:
				embellishments = paginator.page(1)
			except EmptyPage:
				embellishments = paginator.page(paginator.num_pages)

			json_embellishments = serializers.serialize("json", embellishments, fields=('id','description'))
			response_data = {}
			response_data['data'] = json_embellishments
			response_data['page_number'] = embellishments.number
			response_data['num_pages'] = embellishments.paginator.num_pages
			response_data['product_counts'] = item_counts
			response_data['type'] = EmbellishmentsType.objects.get(id=typ).name
		else:
			text_items = TextFonts.objects.filter(is_active=True, is_deleted=False)
			text_counts = text_items.count()
			paginator = Paginator(text_items, offset)
			page = request.GET.get('page')
			try:
				texts = paginator.page(page)
			except PageNotAnInteger:
				texts = paginator.page(1)
			except EmptyPage:
				texts = paginator.page(paginator.num_pages)

			json_data = serializers.serialize("json", texts, fields=('id','description'))
			response_data = {}
			response_data['data'] = json_data
			response_data['page_number'] = texts.number
			response_data['num_pages'] = texts.paginator.num_pages
			response_data['product_counts'] = text_counts
			response_data['type'] = 'Text'

		return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")

	else:
		return HttpResponseNotFound()

@csrf_exempt
def get_personalize_cart_items(request):
	if request.is_ajax():
		id = request.GET.get('id',None)
		cart_items = get_styleboard_cart_item(None,id)
		sessionid = request.session.get('cartsession',None)
		if not sessionid:
			sessionid = generate_unique_id()
			request.session['cartsession'] = sessionid
		
		responsedata = []
		for cart in cart_items:
			datas = {}
			product = get_product(cart.product.id)
			data = {}
			data['product'] = product.product
			data['sessionid'] = sessionid
			data['quantity'] = cart.quantity
			data['guests'] = cart.styleboard_item.item_guest
			data['tables'] = cart.styleboard_item.item_tables
			add_to_cart(data)
			datas['price'] = product._unit_price
			datas['quatity'] = cart.quantity
			datas['sub_total'] = product._unit_price*cart.quantity
			datas['name'] = product.product.name
			datas['original_image_thumbnail'] = product.product.original_image_thumbnail
			datas['default_quantity'] = product.product.default_quantity
			datas['currency'] = product.currency
			datas['id'] = product.product.id
			try:
				guest_table = product.product.guest_table.name
			except:
				pass
			datas['guest_table'] = guest_table
			responsedata.append(datas)

		return HttpResponse(simplejson.dumps(responsedata), mimetype="application/json")		
	else:
		return HttpResponseNotFound()
