from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import HttpResponse, redirect, render_to_response
from django.contrib.auth import authenticate, login, logout
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from admin.models import LoginLog, EmbellishmentsType, Embellishments, TextFonts
from datetime import datetime, timedelta
from django.template import RequestContext
from admin.forms import MenuAddForm, FooterCopyRightForm, AddProductForm, SearchProductForm, EditProductForm, EditGuestTableForm, EditCheckoutPage,\
UploadEmbellishmentForm, UploadFontForm, SearchEmbellishmentForm, EditEmbellishmentForm, SearchFontForm, EditFontForm, SearchUsersForm, EditUsersForm,\
HomeBannerForm, HomeInfoGraphicForm
from menu.services import addMenu
from menu.models import InfoMenu, SiteMenu, FooterMenu, FooterCopyright
from django.contrib.sites.models import Site
from django.views.decorators.csrf import csrf_exempt
from django.template.defaultfilters import filesizeformat
from django.conf import settings
from services import getExtensionAndFileName
from cart.models import Product, ProductPrice, ProductGuestTable, ProductDetails
from plata.shop.models import TaxClass, Order
import shutil
from PIL import Image, ImageDraw, ImageFont
import os
from category.models import Categories
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.http import QueryDict
import urllib #urlencode
from idecorate_settings.models import IdecorateSettings
from django.contrib.auth.models import User
from customer.models import CustomerProfile, CustomerStyleBoard
from django.http import HttpResponseNotFound
from admin.services import home_banner, validate_banner, save_home_banner, validate_home_banner_form, get_home_banners, get_home_banner, get_home_banner_images,\
save_Infographics, manage_infographic, get_HomeInfographics, set_HomeInfographicStatus, validate_Infographic
from cart.services import generate_unique_id
from models import HomeBannerImages
import Image as pil
from django.utils.safestring import mark_safe
import decimal
from django.template import loader, Context
from django.utils import simplejson
import csv

@staff_member_required
def admin(request):
    info = {}

    return render_to_response('admin/index.html',info,RequestContext(request))

@staff_member_required
def admin_manage_menu(request):
    info = {}

    form_info_menu = MenuAddForm(initial={'menu_type':'1'})
    form_site_menu = MenuAddForm(initial={'menu_type':'2'})
    form_footer_menu = MenuAddForm(initial={'menu_type':'3'})

    footer_copyright = FooterCopyright.objects.get(id=1)
    form_footer_copyright = FooterCopyRightForm(initial={'task':'copyright','menu_type':'3','copyright':footer_copyright.copyright})

    info_menus = InfoMenu.objects.filter(parent__id=None,deleted=False).order_by('order')
    site_menus = SiteMenu.objects.filter(parent__id=None,deleted=False).order_by('order')
    footer_menus = FooterMenu.objects.filter(parent__id=None,deleted=False).order_by('order')

    task = request.POST.get('task', None)

    if 'menu_type' in request.session:
    	info['menu_type'] = request.session['menu_type']
    	del request.session['menu_type']

    	if str(info['menu_type']) == "3":

    		info['footer_message'] = True
    	elif str(info['menu_type']) == "2":
    		info['site_message'] = True
    	else:
    		info['info_message'] = True

    if request.method == 'POST':

		info['menu_type'] = request.POST.get('menu_type')
		
		if request.POST.get('menu_type') == "1":

			if task == "arrange":
				arrangement = request.POST.get('arrangement')

				arrangementList = arrangement.split(';')

				for a in arrangementList:
					if a != "":
						splitValues = a.split(':')
						arrange_info = InfoMenu.objects.get(id=int(splitValues[0]))
						arrange_info.order = int(splitValues[1])

						if splitValues[2].strip() == "None":
							arrange_info.parent = None
						else:
							arrange_info.parent = InfoMenu.objects.get(id=int(splitValues[2]))

						arrange_info.save()
				info['info_message'] = True
				messages.success(request, _('Arrangement saved.'))

			elif task == "edit":
				general_name = request.POST.get('general_name', '')
				general_id = request.POST.get('general_id','')
				general_link = request.POST.get('general_link','')

				info['info_message'] = True

				if general_name.strip() == "":
					info['error_edit'] = True
				else:
					info_menu = InfoMenu.objects.get(id=int(general_id))
					info_menu.name = general_name
					info_menu.link = general_link
					info_menu.save()

					messages.success(request, _('Menu saved.'))					
			else:

				form_info_menu = MenuAddForm(request.POST)

				info['info_message'] = True

				if form_info_menu.is_valid():
					addMenu(form_info_menu.cleaned_data['name'], form_info_menu.cleaned_data['link'], form_info_menu.cleaned_data['menu_type'])
					form_info_menu = MenuAddForm(initial={'menu_type':'1'})
					messages.success(request, _('Menu saved.'))

		elif request.POST.get('menu_type') == "2":

			if task == "arrange":
				arrangement = request.POST.get('arrangement')

				arrangementList = arrangement.split(';')

				for a in arrangementList:
					if a != "":
						splitValues = a.split(':')
						arrange_site = SiteMenu.objects.get(id=int(splitValues[0]))
						arrange_site.order = int(splitValues[1])

						if splitValues[2].strip() == "None":
							arrange_site.parent = None
						else:
							arrange_site.parent = SiteMenu.objects.get(id=int(splitValues[2]))

						arrange_site.save()
				info['site_message'] = True
				messages.success(request, _('Arrangement saved.'))
			elif task == "edit":
				general_name = request.POST.get('general_name', '')
				general_id = request.POST.get('general_id','')
				general_link = request.POST.get('general_link','')

				info['site_message'] = True

				if general_name.strip() == "":
					info['error_edit'] = True
				else:
					site_menu = SiteMenu.objects.get(id=int(general_id))
					site_menu.name = general_name
					site_menu.link = general_link
					site_menu.save()

					messages.success(request, _('Menu saved.'))	
			else:

				form_site_menu = MenuAddForm(request.POST)

				info['site_message'] = True

				if form_site_menu.is_valid():
					addMenu(form_site_menu.cleaned_data['name'], form_site_menu.cleaned_data['link'], form_site_menu.cleaned_data['menu_type'])
					form_site_menu = MenuAddForm(initial={'menu_type':'2'})
					messages.success(request, _('Menu saved.'))

		elif request.POST.get('menu_type') == "3":

			if task == "arrange":
				arrangement = request.POST.get('arrangement')

				arrangementList = arrangement.split(';')

				for a in arrangementList:
					if a != "":
						splitValues = a.split(':')
						arrange_footer = FooterMenu.objects.get(id=int(splitValues[0]))
						arrange_footer.order = int(splitValues[1])

						if splitValues[2].strip() == "None":
							arrange_footer.parent = None
						else:
							arrange_footer.parent = FooterMenu.objects.get(id=int(splitValues[2]))

						arrange_footer.save()
				info['footer_message'] = True
				messages.success(request, _('Arrangement saved.'))
			elif task == "copyright":
				form_footer_copyright = FooterCopyRightForm(request.POST)

				if form_footer_copyright.is_valid():
					footer_copyright = FooterCopyright.objects.get(id=1)
					footer_copyright.copyright = form_footer_copyright.cleaned_data['copyright']
					footer_copyright.save()

					form_footer_copyright = FooterCopyRightForm(initial={'task':'copyright','menu_type':'3','copyright':footer_copyright.copyright})

					info['footer_message'] = True
					messages.success(request, _('Copyright saved.'))
			elif task == "edit":
				general_name = request.POST.get('general_name', '')
				general_id = request.POST.get('general_id','')
				general_link = request.POST.get('general_link','')

				info['footer_message'] = True

				if general_name.strip() == "":
					info['error_edit'] = True
				else:
					footer_menu = FooterMenu.objects.get(id=int(general_id))
					footer_menu.name = general_name
					footer_menu.link = general_link
					footer_menu.save()

					messages.success(request, _('Menu saved.'))	
			else:

				form_footer_menu = MenuAddForm(request.POST)

				info['footer_message'] = True

				if form_footer_menu.is_valid():
					addMenu(form_footer_menu.cleaned_data['name'], form_footer_menu.cleaned_data['link'], form_footer_menu.cleaned_data['menu_type'])
					form_footer_menu = MenuAddForm(initial={'menu_type':'3'})
					messages.success(request, _('Menu saved.'))

    info['form_info_menu'] = form_info_menu
    info['form_site_menu'] = form_site_menu
    info['form_footer_menu'] = form_footer_menu
    info['info_menus'] = info_menus
    info['site_menus'] = site_menus
    info['footer_menus'] = footer_menus
    info['form_footer_copyright'] = form_footer_copyright
    return render_to_response('admin/admin_manage_menu.html',info,RequestContext(request))


@staff_member_required
def admin_delete_menu(request,id_delete,menuType):
	
	menu = None

	if str(menuType) == "1":
		menu = InfoMenu.objects.get(id=int(id_delete))
	elif str(menuType) == "2":
		menu = SiteMenu.objects.get(id=int(id_delete))
	else:
		menu = FooterMenu.objects.get(id=int(id_delete))

	menu.deleted = True
	menu.save()

	request.session['menu_type'] = menuType
	messages.success(request, _('Menu deleted.'))

	return redirect('admin_manage_menu')

@staff_member_required
def admin_delete_product(request,id_delete):
	
	product = Product.objects.get(id=int(id_delete))

	product.is_deleted = True
	product.is_active = False
	product.save()

	messages.success(request, _('Product deleted.'))

	if request.session.get('manage_product_redirect', False):
		return redirect(reverse('admin_manage_product') + request.session['manage_product_redirect'])
	else:
		return redirect('admin_manage_product')

def admin_login(request):

	if request.method == 'POST':
		logout(request)

		loginLog = LoginLog.objects.filter(created__gte=(datetime.now() - timedelta(minutes=5)), ip_address=request.META['REMOTE_ADDR'])

		username = request.POST['username']
		password = request.POST['password']

		request.session['admin_username'] = username
		request.session['admin_password'] = password
		request.session['admin_login_post'] = True

		user = authenticate(username=username, password=password)

		if loginLog.count() >= 5:
			request.session['showMessages'] = True
			messages.error(request, _('Please try to login after 5 minutes'))
			return redirect('admin')

		if str(username).strip() != "" and str(password).strip() != "":
			request.session['showMessages'] = True

		if user is not None:

			if user.is_active and user.is_staff:
				login(request, user)
				del request.session['admin_username']
				del request.session['admin_password']
				del request.session['admin_login_post']

				try:
					request.session['showMessages']
				except KeyError:
					pass

				#Successfull login, delete all the log attempts
				LoginLog.objects.filter(ip_address=request.META['REMOTE_ADDR']).delete()

			else:
				if "showMessages" in request.session:
					messages.error(request, _('Sorry this account is disabled'))
		else:
			if "showMessages" in request.session:
				#log ip address
				loginLog = LoginLog()
				loginLog.created = datetime.now()
				loginLog.ip_address = request.META['REMOTE_ADDR']
				loginLog.save()

				messages.error(request, _('Sorry we could not verify your username and password'))

	return redirect('admin')


def admin_logout(request):

	logout(request)

	return redirect('admin')


@staff_member_required
def admin_create_product(request):
    info = {}
    form = AddProductForm()
    info['categories'] = Categories.objects.filter(parent__id=None,deleted=False).order_by('order')
    categories = Categories.objects.filter(deleted=False).order_by('order')    

    catList = []
    for category in categories:
    	catList.append((str(category.id),category.name))

    form.fields['categories'].choices = tuple(catList)

    if request.method == "POST":

    	form = AddProductForm(request.POST)
    	form.fields['categories'].choices = tuple(catList)

    	if form.is_valid():

    		
    		imgSize = (settings.PRODUCT_THUMBNAIL_WIDTH, settings.PRODUCT_THUMBNAIL_HEIGHT)
    		imgSizeProduct = (settings.PRODUCT_WIDTH, settings.PRODUCT_HEIGHT)
    		splittedName = getExtensionAndFileName(form.cleaned_data['original_image'])
    		thumbName = "%s%s" % (splittedName[0], '_thumbnail.jpg')
    		prodName ="%s%s" % (splittedName[0], '.jpg')

    		#CREATE THUMBNAIL
    		img = Image.open("%s%s%s" % (settings.MEDIA_ROOT, "products/temp/", form.cleaned_data['original_image']))
    		img = img.convert('RGBA')
    		img.thumbnail(imgSize,Image.ANTIALIAS)
    		bgImg = Image.new('RGBA', imgSize, (255, 255, 255, 0))
    		bgImg.paste(img,((imgSize[0] - img.size[0]) / 2, (imgSize[1] - img.size[1]) / 2))
    		bgImg.save("%s%s%s" % (settings.MEDIA_ROOT, "products/", thumbName))

    		img = Image.open("%s%s%s" % (settings.MEDIA_ROOT, "products/temp/", form.cleaned_data['original_image']))
    		img = img.convert('RGBA')

    		if img.size[0] > 400 or img.size[1] > 400:
    			#RESIZE MAIN IMAGE
	    		img.thumbnail(imgSizeProduct,Image.ANTIALIAS)
	    		bgImg = Image.new('RGBA', imgSizeProduct, (255, 255, 255, 0))
	    		bgImg.paste(img,((imgSizeProduct[0] - img.size[0]) / 2, (imgSizeProduct[1] - img.size[1]) / 2))
	    		bgImg.save("%s%s%s" % (settings.MEDIA_ROOT, "products/", prodName))
	    	else:
	    		img.save("%s%s%s" % (settings.MEDIA_ROOT, "products/", prodName))

    		img = Image.open("%s%s%s" % (settings.MEDIA_ROOT, "products/temp/", form.cleaned_data['no_background']))
    		
    		if img.size[0] > 400 or img.size[1] > 400:
    			#RESIZE NO BACKGROUND IMAGE
	    		img.thumbnail(imgSizeProduct,Image.ANTIALIAS)
	    		bgImg = Image.new('RGBA', imgSizeProduct, (255, 255, 255, 0))
	    		bgImg.paste(img,((imgSizeProduct[0] - img.size[0]) / 2, (imgSizeProduct[1] - img.size[1]) / 2))
	    		bgImg.save("%s%s%s" % (settings.MEDIA_ROOT, "products/", form.cleaned_data['no_background']))
	    	else:
	    		img.save("%s%s%s" % (settings.MEDIA_ROOT, "products/", form.cleaned_data['no_background']))

    		"""
    		if img.mode != "RGB":
    			img = img.convert("RGB")

    		img.save("%s%s%s" % (settings.MEDIA_ROOT, "products/", thumbName))
    		"""
    		#Save product and price
    		product = Product()
    		product.is_active = bool(int(form.cleaned_data['product_status']))
    		product.name = form.cleaned_data['product_name']
    		product.slug = "%s-%s" % (form.cleaned_data['product_name'], form.cleaned_data['product_sku'])
    		product.description = form.cleaned_data['product_description']
    		product.original_image = prodName
    		product.no_background = form.cleaned_data['no_background']
    		product.original_image_thumbnail = thumbName
    		product.sku = form.cleaned_data['product_sku']
    		product.default_quantity = 1 if form.cleaned_data['default_quantity'] is None else form.cleaned_data['default_quantity']
    		product.guest_table = ProductGuestTable.objects.get(id=int(form.cleaned_data['guest_table']))
    		product.save()

    		#add category
    		catPostLists = request.POST.getlist('categories')
    		for catPostList in catPostLists:
    			cat = Categories.objects.get(id=int(catPostList))
    			product.categories.add(cat)

    			"""
    			#check if parent
    			childCats = Categories.objects.filter(parent=cat)

    			if childCats.count() > 0:
    				#parent
    				ignoreThis = False
    				for childCat in childCats:

    					if str(childCat.id) in catPostLists:
    						ignoreThis = True
    						break

    				if not ignoreThis:
    					product.categories.add(cat)
    			else:
    				#not parent
    				product.categories.add(cat)
    			"""

    		productPrice = ProductPrice()
    		productPrice.product = product
    		productPrice._unit_price = form.cleaned_data['price']
    		productPrice.currency = settings.CURRENCIES[0] #USD
    		productPrice.tax_included = False
    		productPrice.tax_class = TaxClass.objects.get(pk=1)
    		productPrice.save()

    		try:
	    		unit_price = form.cleaned_data['unit_price']
	    		pieces_carton = form.cleaned_data['pieces_carton']
	    		min_order_qty_carton = form.cleaned_data['min_order_qty_carton']
	    		min_order_qty_pieces = None
	    		if pieces_carton and min_order_qty_carton:
	    			min_order_qty_pieces = int(pieces_carton)*int(min_order_qty_carton)
	    		cost_min_order_qty = None
	    		if min_order_qty_pieces and unit_price:
	    			cost_min_order_qty = decimal.Decimal(min_order_qty_pieces) * decimal.Decimal(unit_price)
	    		productDetails = ProductDetails()
	    		productDetails.product = product
	    		productDetails.comment = form.cleaned_data['comment']
	    		productDetails.size = form.cleaned_data['size']
	    		productDetails.color = form.cleaned_data['color']
	    		productDetails.unit_price = unit_price
	    		productDetails.pieces_carton = pieces_carton
	    		productDetails.min_order_qty_carton = min_order_qty_carton
	    		productDetails.min_order_qty_pieces = min_order_qty_pieces
	    		productDetails.cost_min_order_qty = cost_min_order_qty
	    		productDetails.save()
	    	except Exception as e:	    		
	    		pass

    		#REMOVE FILES
    		try:
    			os.unlink("%s%s%s" % (settings.MEDIA_ROOT, "products/temp/", form.cleaned_data['original_image']))
    		except:
    			pass
    		try:

    			os.unlink("%s%s%s" % (settings.MEDIA_ROOT, "products/temp/", form.cleaned_data['no_background']))
    		except:
    			pass
    		#shutil.move("%s%s%s" % (settings.MEDIA_ROOT, "products/temp/", form.cleaned_data['original_image']), "%s%s%s" % (settings.MEDIA_ROOT, "products/", form.cleaned_data['original_image']))
    		#shutil.move("%s%s%s" % (settings.MEDIA_ROOT, "products/temp/", form.cleaned_data['no_background']), "%s%s%s" % (settings.MEDIA_ROOT, "products/", form.cleaned_data['no_background']))
    		
    		messages.success(request, _('Product Saved.'))
    		return redirect('admin_create_product')

    info['form'] = form
    return render_to_response('admin/admin_create_product.html',info,RequestContext(request))


@staff_member_required
def admin_edit_product(request, prod_id):
    info = {}

    product = Product.objects.get(id=int(prod_id))
    info['product'] = product
    productPrice = ProductPrice.objects.get(product=product)
    initCats = product.categories.all()
    listCats = [str(initCat.id) for initCat in initCats]

    request.listCats = listCats
    comment = ''
    size = ''
    unit_price = ''
    pieces_carton = ''
    min_order_qty_carton = ''
    color = ''

    try:
    	productDetails = ProductDetails.objects.get(product=product)
    	comment = productDetails.comment
    	size = productDetails.size
    	color = productDetails.color
    	unit_price = productDetails.unit_price
    	pieces_carton = productDetails.pieces_carton
    	min_order_qty_carton = productDetails.min_order_qty_carton
    	min_order_qty_pieces = 0
    	if pieces_carton and min_order_qty_carton:
    		min_order_qty_pieces = int(pieces_carton)*int(min_order_qty_carton)
    	cost_min_order_qty = 0
    	if min_order_qty_pieces and unit_price:
    		cost_min_order_qty = decimal.Decimal(min_order_qty_pieces) * decimal.Decimal(unit_price)
    	info['min_order_qty_pieces'] = min_order_qty_pieces
    	info['cost_min_order_qty'] = cost_min_order_qty
    	cost_min_order_qty = None
    except Exception as e:
    	pass

    info['initial_form_data'] = {
    	'product_status':str(int(product.is_active)),
    	'product_sku':product.sku,
    	'product_name':product.name,
    	'price':"%.2f" % float(productPrice._unit_price),
    	'categories': listCats,
    	'product_description':product.description,
    	'original_image':product.original_image,
    	'no_background':product.no_background,
    	'default_quantity':product.default_quantity,
    	'guest_table':str(product.guest_table.id),
    	'comment':comment,
    	'size':size,
    	'unit_price':unit_price,
    	'pieces_carton':pieces_carton,
    	'min_order_qty_carton':min_order_qty_carton,
    	'color':color
    }

    form = EditProductForm(initial=info['initial_form_data'],product_id=int(prod_id))

    info['categories'] = Categories.objects.filter(parent__id=None,deleted=False).order_by('order')
    categories = Categories.objects.filter(deleted=False).order_by('order')    

    catList = []
    for category in categories:
    	catList.append((str(category.id),category.name))

    form.fields['categories'].choices = tuple(catList)

    if request.method == "POST":

    	form = EditProductForm(request.POST,product_id=int(prod_id))
    	form.fields['categories'].choices = tuple(catList)

    	if form.is_valid():
    		imgSizeProduct = (settings.PRODUCT_WIDTH, settings.PRODUCT_HEIGHT)

    		product.is_active = bool(int(form.cleaned_data['product_status']))
    		product.name = form.cleaned_data['product_name']
    		product.slug = "%s-%s" % (form.cleaned_data['product_name'], form.cleaned_data['product_sku'])
    		product.description = form.cleaned_data['product_description']
    		product.default_quantity = 1 if form.cleaned_data['default_quantity'] is None else form.cleaned_data['default_quantity']
    		product.guest_table = ProductGuestTable.objects.get(id=int(form.cleaned_data['guest_table']))

    		if product.original_image != form.cleaned_data['original_image']:
	    		imgSize = (settings.PRODUCT_THUMBNAIL_WIDTH, settings.PRODUCT_THUMBNAIL_HEIGHT)
	    		splittedName = getExtensionAndFileName(form.cleaned_data['original_image'])
	    		thumbName = "%s%s" % (splittedName[0], '_thumbnail.jpg')
	    		prodName ="%s%s" % (splittedName[0], '.jpg')

	    		#CREATE THUMBNAIL
	    		img = Image.open("%s%s%s" % (settings.MEDIA_ROOT, "products/temp/", form.cleaned_data['original_image']))
	    		img = img.convert('RGBA')
	    		img.thumbnail(imgSize,Image.ANTIALIAS)
	    		bgImg = Image.new('RGBA', imgSize, (255, 255, 255, 0))
	    		bgImg.paste(img,((imgSize[0] - img.size[0]) / 2, (imgSize[1] - img.size[1]) / 2))
	    		bgImg.save("%s%s%s" % (settings.MEDIA_ROOT, "products/", thumbName))

	    		img = Image.open("%s%s%s" % (settings.MEDIA_ROOT, "products/temp/", form.cleaned_data['original_image']))
	    		img = img.convert('RGBA')

	    		if img.size[0] > 400 or img.size[1] > 400:
	    			#RESIZE MAIN IMAGE
		    		img.thumbnail(imgSizeProduct,Image.ANTIALIAS)
		    		bgImg = Image.new('RGBA', imgSizeProduct, (255, 255, 255, 0))
		    		bgImg.paste(img,((imgSizeProduct[0] - img.size[0]) / 2, (imgSizeProduct[1] - img.size[1]) / 2))
		    		bgImg.save("%s%s%s" % (settings.MEDIA_ROOT, "products/", prodName))
		    	else:
		    		img.save("%s%s%s" % (settings.MEDIA_ROOT, "products/", prodName))

		    	try:
	    			os.unlink("%s%s%s" % (settings.MEDIA_ROOT, "products/temp/", form.cleaned_data['original_image']))
	    		except:
	    			pass
	    		#shutil.move("%s%s%s" % (settings.MEDIA_ROOT, "products/temp/", form.cleaned_data['original_image']), "%s%s%s" % (settings.MEDIA_ROOT, "products/", form.cleaned_data['original_image']))

	    		product.original_image_thumbnail = thumbName
	    		product.original_image = prodName

	    	if product.no_background != form.cleaned_data['no_background']:
	    		product.no_background = form.cleaned_data['no_background']

	    		#RESIZE NO BACKGROUND IMAGE
	    		img = Image.open("%s%s%s" % (settings.MEDIA_ROOT, "products/temp/", form.cleaned_data['no_background']))

	    		if img.size[0] > 400 or img.size[1] > 400:

		    		img.thumbnail(imgSizeProduct,Image.ANTIALIAS)
		    		bgImg = Image.new('RGBA', imgSizeProduct, (255, 255, 255, 0))
		    		bgImg.paste(img,((imgSizeProduct[0] - img.size[0]) / 2, (imgSizeProduct[1] - img.size[1]) / 2))
		    		bgImg.save("%s%s%s" % (settings.MEDIA_ROOT, "products/", form.cleaned_data['no_background']))
		    	else:
		    		img.save("%s%s%s" % (settings.MEDIA_ROOT, "products/", form.cleaned_data['no_background']))
	    		
	    		try:
	    			os.unlink("%s%s%s" % (settings.MEDIA_ROOT, "products/temp/", form.cleaned_data['no_background']))
	    		except:
	    			pass
	    		#shutil.move("%s%s%s" % (settings.MEDIA_ROOT, "products/temp/", form.cleaned_data['no_background']), "%s%s%s" % (settings.MEDIA_ROOT, "products/", form.cleaned_data['no_background']))

    		product.sku = form.cleaned_data['product_sku']
    		product.save()

    		#delete all the categories
    		product.categories.clear()
    		#edit category
    		catPostLists = request.POST.getlist('categories')
    		for catPostList in catPostLists:
    			cat = Categories.objects.get(id=int(catPostList))
    			product.categories.add(cat)

    		productPrice = ProductPrice.objects.get(product=product)
    		productPrice._unit_price = form.cleaned_data['price']
    		productPrice.save()

    		try:
				unit_price = form.cleaned_data['unit_price']
				pieces_carton = form.cleaned_data['pieces_carton']
				min_order_qty_carton = form.cleaned_data['min_order_qty_carton']
				min_order_qty_pieces = None
				if pieces_carton and min_order_qty_carton:
					min_order_qty_pieces = int(pieces_carton)*int(min_order_qty_carton)
				cost_min_order_qty = None
				if min_order_qty_pieces and unit_price:
					cost_min_order_qty = decimal.Decimal(min_order_qty_pieces) * decimal.Decimal(unit_price)

				try:
					productDetails = ProductDetails.objects.get(product=product)
				except:
					productDetails = ProductDetails()
					productDetails.product = product
				productDetails.comment = form.cleaned_data['comment']
				productDetails.size = form.cleaned_data['size']
				productDetails.color = form.cleaned_data['color']
				productDetails.unit_price = unit_price
				productDetails.pieces_carton = pieces_carton
				productDetails.min_order_qty_carton = min_order_qty_carton
				productDetails.min_order_qty_pieces = min_order_qty_pieces
				productDetails.cost_min_order_qty = cost_min_order_qty
				productDetails.save()
	    	except Exception as e:	    		
	    		pass

    		messages.success(request, _('Product Saved.'))

    		if request.session.get('manage_product_redirect', False):
    			return redirect(reverse('admin_manage_product') + request.session['manage_product_redirect'])
    		else:
    			return redirect('admin_manage_product')

    		#return redirect(reverse('admin_edit_product', args=[prod_id]))

    info['form'] = form
    return render_to_response('admin/admin_edit_product.html',info,RequestContext(request))    

@csrf_exempt
def admin_upload_product_image(request):

	if request.method == "POST":

		uploaded = request.FILES['image']
		content_type = uploaded.content_type.split('/')[0]

		#print "The content type is: %s" % (uploaded.content_type)

		if content_type in settings.CONTENT_TYPES:
			if int(uploaded.size) > int(settings.MAX_UPLOAD_PRODUCT_IMAGE_SIZE):
				return HttpResponse(_('notok:Please keep filesize under %s. Current filesize %s').encode('utf-8') % (filesizeformat(settings.MAX_UPLOAD_PRODUCT_IMAGE_SIZE), filesizeformat(uploaded.size)))
			else:
				splittedName = getExtensionAndFileName(uploaded.name)
				newFileName = "%s-%s%s" % (splittedName[0],datetime.now().strftime('%b-%d-%I%M%s%p-%G'),splittedName[1])

				destination = open("%s%s%s" % (settings.MEDIA_ROOT, "products/temp/", newFileName), 'wb+')
				for chunk in uploaded.chunks():
					destination.write(chunk)

				destination.close()

				if uploaded.content_type == "image/tiff" or uploaded.content_type == "image/pjpeg" or uploaded.content_type == "image/jpeg":
					img = Image.open("%s%s%s" % (settings.MEDIA_ROOT, "products/temp/", newFileName))

					splittedName = getExtensionAndFileName(newFileName)
					try:
						os.unlink("%s%s%s" % (settings.MEDIA_ROOT, "products/temp/", newFileName))
					except:
						pass
					newFileName = "%s%s" % (splittedName[0], ".jpg")
					img.save("%s%s%s" % (settings.MEDIA_ROOT, "products/temp/", newFileName))

				return HttpResponse('ok:%s' % newFileName)
		else:
			return HttpResponse(_('notok:File type is not supported').encode('utf-8'))


@staff_member_required
def admin_manage_product(request, params = None):
    info = {}
    info['categories'] = Categories.objects.filter(parent__id=None,deleted=False).order_by('order')
    form = SearchProductForm()
    initial_form = {}

    idecorate_settings = IdecorateSettings.objects.get(pk=1)

    info['guests'] = idecorate_settings.global_default_quantity
    info['tables'] = idecorate_settings.global_table

    if 'gt_errors' in request.session:
    	info['gt_errors'] = request.session.get('gt_errors')
    	del request.session['gt_errors']

    order_by = request.GET.get('order_by','sku')
    sort_type = request.GET.get('sort_type','asc')
    s_type = order_by
    cat_link = ""

    if order_by == 'is_active':
    	if sort_type == 'asc':
    		s_type = "-%s" % order_by
    else:

	    if sort_type == 'desc':
	    	s_type = "-%s" % order_by

    products = Product.objects.filter(is_deleted=False).order_by(s_type)

    categories = Categories.objects.filter(deleted=False, parent=None).order_by('order')

    other_params_dict = {}

    catList = []
    for category in categories:
    	catList.append((str(category.id),category.name))

    form.fields['categories'].choices = tuple(catList)

    if request.method == "POST":

    	form = SearchProductForm(request.POST)
    	form.fields['categories'].choices = tuple(catList)


    	product_name = request.POST.get('product_name','')
    	product_sku = request.POST.get('product_sku','')
    	product_status = request.POST.get('product_status','')
    	product_categories = request.POST.getlist('categories', None)

    else:
    	product_name = request.GET.get('product_name','')
    	product_sku = request.GET.get('product_sku','')
    	product_status = request.GET.get('product_status','')
    	product_categories = request.GET.getlist('categories', None)

    	if product_name:
    		initial_form.update({'product_name':product_name})

    	if product_sku:
    		initial_form.update({'product_sku':product_sku})

    	if product_status:
    		initial_form.update({'product_status':product_status})

    	if product_categories:
    		initial_form.update({'product_categories':product_categories})

    	form = SearchProductForm(initial=initial_form)
    	form.fields['categories'].choices = tuple(catList)


    q = None
    if product_name:

    	other_params_dict.update({'product_name':product_name})

    	if q is not None:
    		q.add(Q(name__icontains=product_name), Q.AND)
    	else:
    		q = Q(name__icontains=product_name)

    if product_sku:

    	other_params_dict.update({'product_sku':product_sku})

    	if q is not None:
    		q.add(Q(sku__icontains=product_sku), Q.AND)
    	else:
    		q = Q(sku__icontains=product_sku)

    if product_status:
    	if product_status != "any":
    		other_params_dict.update({'product_status':product_status})
    		if q is not None:
    			q.add(Q(is_active=bool(int(product_status))), Q.AND)
    		else:
    			q = Q(is_active=bool(int(product_status)))

    if product_categories:
		
		catPostLists = product_categories
		catPostLists = [int(catPostList) for catPostList in catPostLists]
		request.listCats = product_categories

		#print "The get are: %s" % str(request.listCats)

		for product_category in product_categories:
			cat_link += "&categories=" + product_category
		#print catPostLists
		if q is not None:
			q.add(Q(categories__in=catPostLists), Q.AND)
		else:
			q = Q(categories__in=catPostLists)

    if q is not None:
    	products = products.filter(q).distinct().order_by(s_type)

    other_params_dict.update({'order_by':order_by, 'sort_type':sort_type})
    other_params = QueryDict(urllib.urlencode(other_params_dict) + cat_link)

    paginator = Paginator(products, 25)
    page = request.GET.get('page','')

    request.session['manage_product_redirect'] = "?page=%s&%s" % (page, urllib.urlencode(other_params_dict) + cat_link)

    #sku ascending link
    other_params_dict['order_by'] = 'sku'
    other_params_dict['sort_type'] = 'asc'
    info['sku_asc_link'] = "?page=%s&%s" % (page, urllib.urlencode(other_params_dict) + cat_link)

	#sku descending link
    other_params_dict['sort_type'] = 'desc'
    info['sku_desc_link'] = "?page=%s&%s" % (page, urllib.urlencode(other_params_dict) + cat_link)  

    #product name ascending link
    other_params_dict['order_by'] = 'name'
    other_params_dict['sort_type'] = 'asc'
    info['name_asc_link'] = "?page=%s&%s" % (page, urllib.urlencode(other_params_dict) + cat_link)

    #product name descending link
    other_params_dict['sort_type'] = 'desc'
    info['name_desc_link'] = "?page=%s&%s" % (page, urllib.urlencode(other_params_dict) + cat_link)

    #status ascending link
    other_params_dict['order_by'] = 'is_active'
    other_params_dict['sort_type'] = 'asc'
    info['status_asc_link'] = "?page=%s&%s" % (page, urllib.urlencode(other_params_dict) + cat_link)

    #status descending link
    other_params_dict['sort_type'] = 'desc'
    info['status_desc_link'] = "?page=%s&%s" % (page, urllib.urlencode(other_params_dict) + cat_link)

    #quantity ascending link
    other_params_dict['order_by'] = 'default_quantity'
    other_params_dict['sort_type'] = 'asc'
    info['quantity_asc_link'] = "?page=%s&%s" % (page, urllib.urlencode(other_params_dict) + cat_link)

    #quantity desc link
    other_params_dict['sort_type'] = 'desc'
    info['quantity_desc_link'] = "?page=%s&%s" % (page, urllib.urlencode(other_params_dict) + cat_link)

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    info['other_params'] = other_params
    info['form'] = form
    info['products'] = products
    return render_to_response('admin/admin_manage_product.html',info,RequestContext(request))

@staff_member_required
def edit_guests_tables(request):

	if request.method == "POST":
		form = EditGuestTableForm(request.POST)

		if form.is_valid():

			idecorate_settings = IdecorateSettings.objects.get(pk=1)
			idecorate_settings.global_default_quantity = form.cleaned_data['guests']
			idecorate_settings.global_table = form.cleaned_data['tables']
			idecorate_settings.save()
			messages.success(request, _('Data saved.'))
		else:
			request.session['gt_errors'] = form['guests'].errors + form['tables'].errors

	return redirect('admin_manage_product')

@staff_member_required
def admin_manage_checkout(request):
    info = {}

    idecorate_settings = IdecorateSettings.objects.get(pk=1)

    form = EditCheckoutPage()

    if request.method == "POST":
    	form = EditCheckoutPage(request.POST)

    	if form.is_valid():
    		idecorate_settings.delivery_date_note = form.cleaned_data['delivery_text']
    		idecorate_settings.any_question = form.cleaned_data['any_question_text']
    		idecorate_settings.t_and_c = form.cleaned_data['tc_text']
    		idecorate_settings.save()
    		messages.success(request, _('Data saved.'))
    		redirect('admin_manage_checkout')

    info['delivery_text'] = idecorate_settings.delivery_date_note
    info['any_question_text'] = idecorate_settings.any_question
    info['tc_text'] = idecorate_settings.t_and_c
    info['form'] = form
    return render_to_response('admin/admin_manage_checkout.html',info,RequestContext(request))

@staff_member_required
def admin_upload_embellishment(request):
    info = {}
    form = UploadEmbellishmentForm()

    if request.method == "POST":
    	form = UploadEmbellishmentForm(request.POST)

    	if form.is_valid():

    		directoryName = ''

    		if int(form.cleaned_data['embellishment_type']) == 1:
    			directoryName = 'images'
    		elif int(form.cleaned_data['embellishment_type']) == 2:
    			directoryName = 'textures'
    		elif int(form.cleaned_data['embellishment_type']) == 3:
    			directoryName = 'patterns'
    		elif int(form.cleaned_data['embellishment_type']) == 4:
    			directoryName = 'shapes'
    		elif int(form.cleaned_data['embellishment_type']) == 5:
    			directoryName = 'borders' 

    		imgSize = (settings.EMBELLISHMENT_THUMBNAIL_WIDTH, settings.EMBELLISHMENT_THUMBNAIL_HEIGHT)
    		
    		splittedName = getExtensionAndFileName(form.cleaned_data['embellishment_image'])
    		thumbName = "%s%s" % (splittedName[0], '_thumbnail.png')

    		#CREATE THUMBNAIL
    		img = Image.open("%s%s%s" % (settings.MEDIA_ROOT, "embellishments/temp/", form.cleaned_data['embellishment_image']))
    		img.thumbnail(imgSize,Image.ANTIALIAS)
    		bgImg = Image.new('RGBA', imgSize, (255, 255, 255, 0))
    		bgImg.paste(img,((imgSize[0] - img.size[0]) / 2, (imgSize[1] - img.size[1]) / 2))
    		bgImg.save("%s%s%s" % (settings.MEDIA_ROOT, "embellishments/%s/" % directoryName, thumbName))

    		img = Image.open("%s%s%s" % (settings.MEDIA_ROOT, "embellishments/temp/", form.cleaned_data['embellishment_image']))
	    	img.save("%s%s%s" % (settings.MEDIA_ROOT, "embellishments/%s/" % directoryName, form.cleaned_data['embellishment_image']))

	    	embellishmentType = EmbellishmentsType.objects.get(id=int(form.cleaned_data['embellishment_type']))
	    	embellishment = Embellishments()

	    	embellishment.is_active = bool(int(form.cleaned_data['embellishment_status']))
	    	embellishment.description = form.cleaned_data['embellishment_description']
	    	embellishment.e_type = embellishmentType
	    	embellishment.image = form.cleaned_data['embellishment_image']
	    	embellishment.image_thumb = thumbName
	    	embellishment.save()

	    	#REMOVE FILES
	    	try:
	    		os.unlink("%s%s%s" % (settings.MEDIA_ROOT, "embellishments/temp/", form.cleaned_data['embellishment_image']))
	    	except:
	    		pass

	    	messages.success(request, _('Embellishment Saved.'))
	    	return redirect('admin_upload_embellishment')

    info['form'] = form
    return render_to_response('admin/admin_upload_embellishment.html',info,RequestContext(request))

@csrf_exempt
def admin_upload_embellishment_image(request):

	if request.method == "POST":

		uploaded = request.FILES['image']
		content_type = uploaded.content_type.split('/')[0]

		if content_type in settings.CONTENT_TYPES:
			if int(uploaded.size) > int(settings.MAX_UPLOAD_EMBELLISHMENT_IMAGE_SIZE):
				return HttpResponse(_('notok:Please keep filesize under %s. Current filesize %s').encode('utf-8') % (filesizeformat(settings.MAX_UPLOAD_EMBELLISHMENT_IMAGE_SIZE), filesizeformat(uploaded.size)))
			else:
				splittedName = getExtensionAndFileName(uploaded.name)
				newFileName = "%s-%s%s" % (splittedName[0],datetime.now().strftime('%b-%d-%I%M%s%p-%G'),splittedName[1])

				destination = open("%s%s%s" % (settings.MEDIA_ROOT, "embellishments/temp/", newFileName), 'wb+')
				for chunk in uploaded.chunks():
					destination.write(chunk)

				destination.close()

				if uploaded.content_type == "image/tiff" or uploaded.content_type == "image/pjpeg" or uploaded.content_type == "image/jpeg":
					img = Image.open("%s%s%s" % (settings.MEDIA_ROOT, "embellishments/temp/", newFileName))

					splittedName = getExtensionAndFileName(newFileName)
					try:
						os.unlink("%s%s%s" % (settings.MEDIA_ROOT, "embellishments/temp/", newFileName))
					except:
						pass
					newFileName = "%s%s" % (splittedName[0], ".jpg")
					img.save("%s%s%s" % (settings.MEDIA_ROOT, "embellishments/temp/", newFileName))

				return HttpResponse('ok:%s' % newFileName)
		else:
			return HttpResponse(_('notok:File type is not supported').encode('utf-8'))


@staff_member_required
def admin_manage_text_font(request):
    info = {}

    form = UploadFontForm()

    if request.method == "POST":
    	form = UploadFontForm(request.POST)

    	if form.is_valid():
    		textFont = TextFonts()
    		textFont.is_active = bool(int(form.cleaned_data['font_status']))
    		textFont.description = form.cleaned_data['font_description']
    		textFont.font = form.cleaned_data['font_file']
    		textFont.save()

	    	#MOVE FONT
	    	shutil.move("%s%s%s" % (settings.MEDIA_ROOT, "fonts/temp/", form.cleaned_data['font_file']), "%s%s%s" % (settings.MEDIA_ROOT, "fonts/", form.cleaned_data['font_file']))

	    	messages.success(request, _('Font Saved.'))
	    	return redirect('admin_manage_text_font')

    info['form'] = form
    return render_to_response('admin/admin_manage_text_font.html',info,RequestContext(request))


@csrf_exempt
def admin_upload_font(request):

	if request.method == "POST":

		uploaded = request.FILES['font']
		content_type = uploaded.content_type

		print "The content type is: %s" % content_type

		if content_type in settings.FONT_TYPES:
			if int(uploaded.size) > int(settings.MAX_UPLOAD_FONT_SIZE):
				return HttpResponse(_('notok:Please keep filesize under %s. Current filesize %s').encode('utf-8') % (filesizeformat(settings.MAX_UPLOAD_FONT_SIZE), filesizeformat(uploaded.size)))
			else:
				splittedName = getExtensionAndFileName(uploaded.name)
				newFileName = "%s-%s%s" % (splittedName[0],datetime.now().strftime('%b-%d-%I%M%s%p-%G'),splittedName[1])

				destination = open("%s%s%s" % (settings.MEDIA_ROOT, "fonts/temp/", newFileName), 'wb+')
				for chunk in uploaded.chunks():
					destination.write(chunk)

				destination.close()

				return HttpResponse('ok:%s' % newFileName)
		else:
			return HttpResponse(_('notok:File type is not supported').encode('utf-8'))

def admin_generate_text_thumbnail(request):
	#parameters
	font_size = 100
	image_text = request.GET.get('font_text','')
	font_name = request.GET.get('font_name','')
	font_color = request.GET.get('font_color','')

	font_color = (int(font_color[0:3]), int(font_color[3:6]), int(font_color[6:9]))
	#load font with size
	font = ImageFont.truetype("%s%s%s" % (settings.MEDIA_ROOT, "fonts/temp/", font_name), font_size)
	
	#get the text size first
	textSize = font.getsize(image_text)

	#image with background transparent
	img = Image.new("RGBA", textSize, (255,255,255, 0))

	#create draw object	
	draw = ImageDraw.Draw(img)

	#draw text with black font color
	draw.text((0,0), image_text, font_color, font=font)

	#create thumbnail
	img.thumbnail((100,100),Image.ANTIALIAS)
	bgImg = Image.new('RGBA', (100,100), (255, 255, 255, 0))
	bgImg.paste(img,((100 - img.size[0]) / 2, (100 - img.size[1]) / 2))

	response = HttpResponse(mimetype="image/jpg")
	bgImg.save(response, "JPEG")
	return response

@staff_member_required
def admin_manage_embellishment(request):
    info = {}

    form = SearchEmbellishmentForm()
    initial_form = {}

    order_by = request.GET.get('order_by','description')
    sort_type = request.GET.get('sort_type','asc')
    s_type = order_by

    if order_by == 'is_active':
    	if sort_type == 'asc':
    		s_type = "-%s" % order_by
    else:

	    if sort_type == 'desc':
	    	s_type = "-%s" % order_by

    embellishments = Embellishments.objects.filter(is_deleted=False).order_by(s_type)

    other_params_dict = {}

    if request.method == "POST":

    	form = SearchEmbellishmentForm(request.POST)

    	embellishment_description = request.POST.get('embellishment_description','')
    	embellishment_status = request.POST.get('embellishment_status','')
    	embellishment_type = request.POST.get('embellishment_type','')

    else:
    	embellishment_description = request.GET.get('embellishment_description','')
    	embellishment_status = request.GET.get('embellishment_status','')
    	embellishment_type = request.GET.get('embellishment_type','')

    	if embellishment_description:
    		initial_form.update({'embellishment_description':embellishment_description})

    	if embellishment_status:
    		initial_form.update({'embellishment_status':embellishment_status})

    	if embellishment_type:
    		initial_form.update({'embellishment_type':embellishment_type})

    	form = SearchEmbellishmentForm(initial=initial_form)

    q = None
    if embellishment_description:

    	other_params_dict.update({'embellishment_description':embellishment_description})

    	if q is not None:
    		q.add(Q(description__icontains=embellishment_description), Q.AND)
    	else:
    		q = Q(description__icontains=embellishment_description)

    if embellishment_status:
    	if embellishment_status != "any":
    		other_params_dict.update({'embellishment_status':embellishment_status})
    		if q is not None:
    			q.add(Q(is_active=bool(int(embellishment_status))), Q.AND)
    		else:
    			q = Q(is_active=bool(int(embellishment_status)))

    if embellishment_type:
    	if embellishment_type != "any":
    		other_params_dict.update({'embellishment_type':embellishment_type})
    		if q is not None:
    			q.add(Q(e_type=int(embellishment_type)), Q.AND)
    		else:
    			q = Q(e_type=int(embellishment_type))

    if q is not None:
    	embellishments = embellishments.filter(q).order_by(s_type)

    other_params_dict.update({'order_by':order_by, 'sort_type':sort_type})
    other_params = QueryDict(urllib.urlencode(other_params_dict))

    paginator = Paginator(embellishments, 25)
    page = request.GET.get('page','')

    request.session['manage_embellishment_redirect'] = "?page=%s&%s" % (page, urllib.urlencode(other_params_dict))


    other_params_dict['order_by'] = 'description'
    other_params_dict['sort_type'] = 'asc'
    info['description_asc_link'] = "?page=%s&%s" % (page, urllib.urlencode(other_params_dict))

    other_params_dict['sort_type'] = 'desc'
    info['description_desc_link'] = "?page=%s&%s" % (page, urllib.urlencode(other_params_dict))  

    #status ascending link
    other_params_dict['order_by'] = 'is_active'
    other_params_dict['sort_type'] = 'asc'
    info['status_asc_link'] = "?page=%s&%s" % (page, urllib.urlencode(other_params_dict))

    #status descending link
    other_params_dict['sort_type'] = 'desc'
    info['status_desc_link'] = "?page=%s&%s" % (page, urllib.urlencode(other_params_dict))

    #status ascending type
    other_params_dict['order_by'] = 'e_type__name'
    other_params_dict['sort_type'] = 'asc'
    info['type_asc_link'] = "?page=%s&%s" % (page, urllib.urlencode(other_params_dict))

    #status descending link
    other_params_dict['sort_type'] = 'desc'
    info['type_desc_link'] = "?page=%s&%s" % (page, urllib.urlencode(other_params_dict))


    try:
        embellishments = paginator.page(page)
    except PageNotAnInteger:
        embellishments = paginator.page(1)
    except EmptyPage:
        embellishments = paginator.page(paginator.num_pages)

    info['other_params'] = other_params
    info['form'] = form
    info['embellishments'] = embellishments

    return render_to_response('admin/admin_manage_embellishment.html',info,RequestContext(request))


@staff_member_required
def admin_delete_embellishment(request,id_delete):
	
	embellishment = Embellishments.objects.get(id=int(id_delete))

	embellishment.is_deleted = True
	embellishment.is_active = False
	embellishment.save()

	messages.success(request, _('Embellishment deleted.'))

	if request.session.get('manage_embellishment_redirect', False):
		return redirect(reverse('admin_manage_embellishment') + request.session['manage_embellishment_redirect'])
	else:
		return redirect('admin_manage_embellishment')


@staff_member_required
def admin_edit_embellishment(request, e_id):
    info = {}

    embellishment = Embellishments.objects.get(id=int(e_id))
    info['embellishment'] = embellishment

    info['initial_form_data'] = {
    	'embellishment_status':str(int(embellishment.is_active)),
    	'embellishment_description':embellishment.description,
    	'embellishment_image': embellishment.image,
    	'embellishment_type':str(int(embellishment.e_type.id)),
    }

    form = EditEmbellishmentForm(initial=info['initial_form_data'])

    if request.method == "POST":

    	form = EditEmbellishmentForm(request.POST)

    	if form.is_valid():

    		directoryOld = ''

    		if embellishment.e_type.id == 1:
    			directoryOld = 'images'
    		elif embellishment.e_type.id == 2:
    			directoryOld = 'textures'
    		elif embellishment.e_type.id == 3:
    			directoryOld = 'patterns'
    		elif embellishment.e_type.id == 4:
    			directoryOld = 'shapes'
    		elif embellishment.e_type.id == 5:
    			directoryOld = 'borders'

    		directoryNew = ''

    		if int(form.cleaned_data['embellishment_type']) == 1:
    			directoryNew = 'images'
    		elif int(form.cleaned_data['embellishment_type']) == 2:
    			directoryNew = 'textures'
    		elif int(form.cleaned_data['embellishment_type']) == 3:
    			directoryNew = 'patterns'
    		elif int(form.cleaned_data['embellishment_type']) == 4:
    			directoryNew = 'shapes'
    		elif int(form.cleaned_data['embellishment_type']) == 5:
    			directoryNew = 'borders' 

	    	embellishment.is_active = bool(int(form.cleaned_data['embellishment_status']))
	    	embellishment.description = form.cleaned_data['embellishment_description']
	    	embellishment.e_type = EmbellishmentsType.objects.get(id=int(form.cleaned_data['embellishment_type']))

	    	#move the file first if the type is changed
	    	if directoryOld != directoryNew:
				shutil.move("%s%s%s" % (settings.MEDIA_ROOT, "embellishments/%s/" % directoryOld, embellishment.image), "%s%s%s" % (settings.MEDIA_ROOT, "embellishments/%s/" % directoryNew, embellishment.image))
				shutil.move("%s%s%s" % (settings.MEDIA_ROOT, "embellishments/%s/" % directoryOld, embellishment.image_thumb), "%s%s%s" % (settings.MEDIA_ROOT, "embellishments/%s/" % directoryNew, embellishment.image_thumb))	    	

    		if embellishment.image != form.cleaned_data['embellishment_image']:
    			#image changed
	    		imgSize = (settings.EMBELLISHMENT_THUMBNAIL_WIDTH, settings.EMBELLISHMENT_THUMBNAIL_HEIGHT)
	    		
	    		splittedName = getExtensionAndFileName(form.cleaned_data['embellishment_image'])
	    		thumbName = "%s%s" % (splittedName[0], '_thumbnail.png')

	    		#CREATE THUMBNAIL
	    		img = Image.open("%s%s%s" % (settings.MEDIA_ROOT, "embellishments/temp/", form.cleaned_data['embellishment_image']))
	    		img.thumbnail(imgSize,Image.ANTIALIAS)
	    		bgImg = Image.new('RGBA', imgSize, (255, 255, 255, 0))
	    		bgImg.paste(img,((imgSize[0] - img.size[0]) / 2, (imgSize[1] - img.size[1]) / 2))
	    		bgImg.save("%s%s%s" % (settings.MEDIA_ROOT, "embellishments/%s/" % directoryNew, thumbName))

	    		img = Image.open("%s%s%s" % (settings.MEDIA_ROOT, "embellishments/temp/", form.cleaned_data['embellishment_image']))
		    	img.save("%s%s%s" % (settings.MEDIA_ROOT, "embellishments/%s/" % directoryNew, form.cleaned_data['embellishment_image']))

		    	#REMOVE FILES
		    	try:
		    		os.unlink("%s%s%s" % (settings.MEDIA_ROOT, "embellishments/temp/", form.cleaned_data['embellishment_image']))
		    	except:
		    		pass
		    	try:
		    		os.unlink("%s%s%s" % (settings.MEDIA_ROOT, "embellishments/%s/" % directoryNew, embellishment.image))
		    	except:
		    		pass
		    	try:
		    		os.unlink("%s%s%s" % (settings.MEDIA_ROOT, "embellishments/%s/" % directoryNew, embellishment.image_thumb))
		    	except:
		    		pass

		    	embellishment.image = form.cleaned_data['embellishment_image']
		    	embellishment.image_thumb = thumbName

    		embellishment.save()

    		messages.success(request, _('Embellishment Saved.'))

    		if request.session.get('manage_embellishment_redirect', False):
    			return redirect(reverse('admin_manage_embellishment') + request.session['manage_embellishment_redirect'])
    		else:
    			return redirect('admin_manage_embellishment')

    info['current_directory'] = "%s%s" % (str(embellishment.e_type.name).lower(), "s")
    info['form'] = form
    return render_to_response('admin/admin_edit_embellishment.html',info,RequestContext(request))


@staff_member_required
def admin_manage_font(request):
    info = {}

    form = SearchFontForm()
    initial_form = {}

    order_by = request.GET.get('order_by','description')
    sort_type = request.GET.get('sort_type','asc')
    s_type = order_by

    if order_by == 'is_active':
    	if sort_type == 'asc':
    		s_type = "-%s" % order_by
    else:

	    if sort_type == 'desc':
	    	s_type = "-%s" % order_by

    fonts = TextFonts.objects.filter(is_deleted=False).order_by(s_type)

    other_params_dict = {}

    if request.method == "POST":

    	form = SearchFontForm(request.POST)

    	font_description = request.POST.get('font_description','')
    	font_status = request.POST.get('font_status','')

    else:
    	font_description = request.GET.get('font_description','')
    	font_status = request.GET.get('font_status','')

    	if font_description:
    		initial_form.update({'font_description':font_description})

    	if font_status:
    		initial_form.update({'font_status':font_status})

    	form = SearchFontForm(initial=initial_form)

    q = None
    if font_description:

    	other_params_dict.update({'font_description':font_description})

    	if q is not None:
    		q.add(Q(description__icontains=font_description), Q.AND)
    	else:
    		q = Q(description__icontains=font_description)

    if font_status:
    	if font_status != "any":
    		other_params_dict.update({'font_status':font_status})
    		if q is not None:
    			q.add(Q(is_active=bool(int(font_status))), Q.AND)
    		else:
    			q = Q(is_active=bool(int(font_status)))

    if q is not None:
    	fonts = fonts.filter(q).order_by(s_type)

    other_params_dict.update({'order_by':order_by, 'sort_type':sort_type})
    other_params = QueryDict(urllib.urlencode(other_params_dict))

    paginator = Paginator(fonts, 25)
    page = request.GET.get('page','')

    request.session['manage_font_redirect'] = "?page=%s&%s" % (page, urllib.urlencode(other_params_dict))


    other_params_dict['order_by'] = 'description'
    other_params_dict['sort_type'] = 'asc'
    info['description_asc_link'] = "?page=%s&%s" % (page, urllib.urlencode(other_params_dict))

    other_params_dict['sort_type'] = 'desc'
    info['description_desc_link'] = "?page=%s&%s" % (page, urllib.urlencode(other_params_dict))  

    #status ascending link
    other_params_dict['order_by'] = 'is_active'
    other_params_dict['sort_type'] = 'asc'
    info['status_asc_link'] = "?page=%s&%s" % (page, urllib.urlencode(other_params_dict))

    #status descending link
    other_params_dict['sort_type'] = 'desc'
    info['status_desc_link'] = "?page=%s&%s" % (page, urllib.urlencode(other_params_dict))


    try:
        fonts = paginator.page(page)
    except PageNotAnInteger:
        fonts = paginator.page(1)
    except EmptyPage:
        fonts = paginator.page(paginator.num_pages)

    info['other_params'] = other_params
    info['form'] = form
    info['fonts'] = fonts

    return render_to_response('admin/admin_manage_font.html',info,RequestContext(request))

@staff_member_required
def admin_delete_font(request,id_delete):
	
	font = TextFonts.objects.get(id=int(id_delete))

	font.is_deleted = True
	font.is_active = False
	font.save()

	messages.success(request, _('Font deleted.'))

	if request.session.get('manage_font_redirect', False):
		return redirect(reverse('admin_manage_font') + request.session['manage_font_redirect'])
	else:
		return redirect('admin_manage_font')


@staff_member_required
def admin_edit_font(request, t_id):
    info = {}

    font = TextFonts.objects.get(id=int(t_id))
    info['font'] = font

    info['initial_form_data'] = {
    	'font_status':str(int(font.is_active)),
    	'font_description':font.description,
    	'font_file': font.font
    }

    form = EditFontForm(initial=info['initial_form_data'])

    if request.method == "POST":

    	form = EditFontForm(request.POST)

    	if form.is_valid():

	    	font.is_active = bool(int(form.cleaned_data['font_status']))
	    	font.description = form.cleaned_data['font_description']  	

    		if font.font != form.cleaned_data['font_file']:
    			#font changed

	    		#MOVE FONT
	    		shutil.move("%s%s%s" % (settings.MEDIA_ROOT, "fonts/temp/", form.cleaned_data['font_file']), "%s%s%s" % (settings.MEDIA_ROOT, "fonts/", form.cleaned_data['font_file']))

		    	#REMOVE FILES
		    	try:
		    		os.unlink("%s%s%s" % (settings.MEDIA_ROOT, "fonts/", font.font))
		    	except:
		    		pass

		    	font.font = form.cleaned_data['font_file']

    		font.save()

    		messages.success(request, _('Font Saved.'))

    		if request.session.get('manage_font_redirect', False):
    			return redirect(reverse('admin_manage_font') + request.session['manage_font_redirect'])
    		else:
    			return redirect('admin_manage_font')

    info['form'] = form
    return render_to_response('admin/admin_edit_font.html',info,RequestContext(request))

@staff_member_required
def admin_manage_users(request):
	info = {}

	form = SearchUsersForm()
	edit_form = EditUsersForm()
	initial_form = {}

	order_by = request.GET.get('order_by','last_login')
	sort_type = request.GET.get('sort_type','desc')
	s_type = order_by


	if order_by == 'is_active':
		if sort_type == 'asc':
			s_type = "-%s" % order_by
	else:
		if sort_type == 'desc':
			s_type = "-%s" % order_by

	if 'mu_errors' in request.session:
		info['mu_errors'] = request.session.get('mu_errors')
		del request.session['mu_errors']

	users = User.objects.filter().order_by(s_type)
	other_params_dict = {}

	if request.method == "POST":
		form = SearchUsersForm(request.POST)
		nickname = request.POST.get('nickname','')
		email = request.POST.get('email','')
		u_type = request.POST.get('u_type','')
		status = request.POST.get('status','')

	else:
		nickname = request.GET.get('nickname','')
		email = request.GET.get('email','')
		u_type = request.GET.get('u_type','')
		status = request.GET.get('status','')

		if nickname:
			initial_form.update({'nickname':nickname})

		if email:
			initial_form.update({'email':email})

		if u_type:
			initial_form.update({'u_type':u_type})

		if status:
			initial_form.update({'status':status})

		form = SearchUsersForm(initial=initial_form)

	q = None

	if nickname:

		other_params_dict.update({'nickname':nickname})

		splittedNicks = nickname.split(' ')

		for splittedNick in splittedNicks:

			customerProfiles = CustomerProfile.objects.filter(nickname__icontains=splittedNick)
			cList = [int(customerProfile.user.id) for customerProfile in customerProfiles]

			if q is not None:
				q.add(Q(id__in=cList), Q.OR)
			else:
				q = Q(id__in=cList)

			if q is not None:
				q.add(Q(first_name__icontains=splittedNick), Q.OR)
			else:
				q = Q(first_name__icontains=splittedNick)

			if q is not None:
				q.add(Q(last_name__icontains=splittedNick), Q.OR)
			else:
				q = Q(last_name__icontains=splittedNick)

	if email:

		other_params_dict.update({'email':email})

		if q is not None:
			q.add(Q(username__icontains=email), Q.AND)

		else:
			q = Q(username__icontains=email)

	if u_type:
		if u_type != "any":
			other_params_dict.update({'u_type':u_type})
			if q is not None:
				q.add(Q(is_staff=bool(int(u_type))), Q.AND)
			else:
				q = Q(is_staff=bool(int(u_type)))

	if status:
		if status != "any":
			other_params_dict.update({'status':status})
			if q is not None:
				q.add(Q(is_active=bool(int(status))), Q.AND)
			else:
				q = Q(is_active=bool(int(status)))

	if q is not None:
		users = users.filter(q).order_by(s_type)

	other_params_dict.update({'order_by':order_by, 'sort_type':sort_type})
	other_params = QueryDict(urllib.urlencode(other_params_dict))

	paginator = Paginator(users, 25)
	page = request.GET.get('page','')

	request.session['manage_users_redirect'] = "?page=%s&%s" % (page, urllib.urlencode(other_params_dict))

	other_params_dict['order_by'] = 'username'
	other_params_dict['sort_type'] = 'asc'
	info['username_asc_link'] = "?page=%s&%s" % (page, urllib.urlencode(other_params_dict))

	other_params_dict['sort_type'] = 'desc'
	info['username_desc_link'] = "?page=%s&%s" % (page, urllib.urlencode(other_params_dict))

	other_params_dict['order_by'] = 'is_active'
	other_params_dict['sort_type'] = 'asc'
	info['status_asc_link'] = "?page=%s&%s" % (page, urllib.urlencode(other_params_dict))

	other_params_dict['sort_type'] = 'desc'
	info['status_desc_link'] = "?page=%s&%s" % (page, urllib.urlencode(other_params_dict))

	other_params_dict['order_by'] = 'is_staff'
	other_params_dict['sort_type'] = 'asc'
	info['type_asc_link'] = "?page=%s&%s" % (page, urllib.urlencode(other_params_dict))

	other_params_dict['sort_type'] = 'desc'
	info['type_desc_link'] = "?page=%s&%s" % (page, urllib.urlencode(other_params_dict))

	other_params_dict['order_by'] = 'last_login'
	other_params_dict['sort_type'] = 'asc'
	info['act_asc_link'] = "?page=%s&%s" % (page, urllib.urlencode(other_params_dict))

	other_params_dict['sort_type'] = 'desc'
	info['act_desc_link'] = "?page=%s&%s" % (page, urllib.urlencode(other_params_dict))

	try:
		users = paginator.page(page)
	except PageNotAnInteger:
		users = paginator.page(1)
	except EmptyPage:
		users = paginator.page(paginator.num_pages)

	info['other_params'] = other_params
	info['form'] = form
	info['users'] = users
	info['edit_form'] = edit_form

	return render_to_response('admin/admin_manage_users.html',info,RequestContext(request))

@staff_member_required
def admin_stat_user(request,id):
	
	user = User.objects.get(id=id)
	retStat = ""
	retStat2 = ""

	if user.is_active:
		user.is_active = False
		retStat = "Deactivated"
		retStat2 = " Deactivated users will no longer be able to login."
	else:
		user.is_active = True
		retStat = "Activated"
		retStat2 = ""

	user.save()

	messages.success(request, _('User %s.%s' % (retStat,retStat2)))

	if request.session.get('manage_users_redirect', False):
		return redirect(reverse('admin_manage_users') + request.session['manage_users_redirect'])
	else:
		return redirect('admin_manage_users')

@staff_member_required
def admin_delete_user(request,id):

	try:
		customerStyleBoard = CustomerStyleBoard.objects.get(user__id=int(id))
	except:
		customerStyleBoard = None

	if customerStyleBoard:
		request.session['mu_errors'] = [_('You cannot delete an active user.')]
	else:

		usr = User.objects.get(id=id)

		uOrder = Order.objects.filter(user=usr)

		if uOrder.count() == 0:
			usr.delete()
			messages.success(request, _('User deleted.'))
		else:
			request.session['mu_errors'] = [_('You cannot delete user with order.')]	

	if request.session.get('manage_users_redirect', False):
		return redirect(reverse('admin_manage_users') + request.session['manage_users_redirect'])
	else:
		return redirect('admin_manage_users')


@staff_member_required
def admin_edit_user(request):
	
	#user = User.objects.get(id=id)

	if request.method == "POST":
		form = EditUsersForm(request.POST, user_id=request.POST.get('u_id'))

		if form.is_valid():

			user = User.objects.get(id=int(form.cleaned_data['u_id']))
			user.username = form.cleaned_data['email']
			user.is_staff = bool(int(form.cleaned_data['u_type']))
			user.is_active = bool(int(form.cleaned_data['status']))
			user.first_name = form.cleaned_data['first_name']
			user.last_name = form.cleaned_data['last_name']

			passwd = form.cleaned_data['password']

			if passwd:
				user.set_password(passwd)

			user.save()

			try:
				prof = CustomerProfile.objects.get(user=user)
				prof.nickname = form.cleaned_data['nickname']
				prof.save()
			except:
				prof = CustomerProfile()
				prof.nickname = form.cleaned_data['nickname']
				prof.user = user
				prof.save()

			messages.success(request, _('Changes Saved.'))
		else:
			request.session['mu_errors'] = form['u_id'].errors + form['nickname'].errors + form['email'].errors + form['u_type'].errors + form['status'].errors + form['password'].errors + form['confirm_password'].errors

	if request.session.get('manage_users_redirect', False):
		return redirect(reverse('admin_manage_users') + request.session['manage_users_redirect'])
	else:
		return redirect('admin_manage_users')

@staff_member_required
def manage_template(request):
    info = {}
    info['max_emb_size'] = settings.MAX_UPLOAD_EMBELLISHMENT_IMAGE_SIZE
    info['text_items'] = TextFonts.objects.filter(is_active=True, is_deleted=False)

    template_positions = request.session.get('template_positions', None)

    if template_positions:
    	info['template_positions'] = mark_safe(str(template_positions))
    else:
    	info['template_positions'] = mark_safe("''")

    return render_to_response('admin/manage_template.html',info,RequestContext(request))

@staff_member_required
def manage_homepage(request):
    info = {}
    info['home_banners'] = get_home_banners()
    return render_to_response('admin/manage_homepage.html',info,RequestContext(request))

@staff_member_required
def homepage_upload_banner(request):
    info = {}
    form = HomeBannerForm()
    info['mode'] = 'new'
    if request.method=="POST":
    	form = HomeBannerForm(request.POST)
    	if form.is_valid():
    		validated = validate_home_banner_form(form.cleaned_data)
    		if not validated:
	    		save_response = save_home_banner(form.cleaned_data)
	    		if save_response:
	    			messages.success(request, _('Successfully added.'))
	    		else:
	    			messages.error(request, _('Could not save. Please contact administrator.'))
	    		return redirect('homepage_upload_banner')
	    	else:
	    		info['validated'] = validated
    info['form'] = form
    return render_to_response('admin/upload_home_banner.html',info,RequestContext(request))

@staff_member_required
def homepage_edit_banner(request,hbid=None):
	if not hbid:
		return redirect('manage_homepage')

	home_banner_item = get_home_banner(hbid)

	if not home_banner_item:
		return redirect('manage_homepage')

	hb_images = get_home_banner_images(home_banner_item.id)
	hb_images = hb_images.order_by('id')
	info = {}

	image11 = ''
	wholelink = ''
	image21 = ''
	image22 = ''
	half1link = ''
	half2link = ''
	image31 = ''
	image32 = ''
	image33 = ''
	third1link = ''
	third2link = ''
	third3link = ''

	count = hb_images.count()
	if count==1:
		image11 = hb_images[0].image		
		wholelink = hb_images[0].link

		info['image11'] = image11
	if count==2:
		image21 = hb_images[0].image
		image22 = hb_images[1].image
		half1link = hb_images[0].link
		half2link = hb_images[1].link

		info['image21'] = image21
		info['image22'] = image22
	if count==3:
		image31 = hb_images[0].image
		image32 = hb_images[1].image
		image33 = hb_images[2].image
		third1link = hb_images[0].link
		third2link = hb_images[1].link
		third3link = hb_images[2].link

		image31 = hb_images[0].image
		image32 = hb_images[1].image
		image33 = hb_images[2].image

		info['image31'] = image31
		info['image32'] = image32
		info['image33'] = image33

	if request.method=="POST":
		form = HomeBannerForm(request.POST)
		if form.is_valid():
			validated = validate_home_banner_form(form.cleaned_data)
			if not validated:
				data = form.cleaned_data				
				data['id'] = hbid
				save_response = save_home_banner(data)
				if save_response:
					messages.success(request, _('Saved.'))
				else:
					messages.error(request, _('Could not save. Please contact administrator.'))
				return redirect('/admin/edit_banner/%s' % hbid)
			else:
				info['validated'] = validated
	else:
		form = HomeBannerForm(initial={ 
			'sizes': home_banner_item.size, 
			'image11':image11, 
			'wholelink':wholelink,
			'image21':image21,
			'image22':image22,
			'half1link':half1link,
			'half2link':half2link,
			'image31':image31,
			'image32':image32,
			'image33':image33,
			'third1link':third1link,
			'third2link':third2link,
			'third3link':third3link
			})
	info['form'] = form
	info['mode'] = 'edit'
	return render_to_response('admin/upload_home_banner.html',info,RequestContext(request))

@csrf_exempt
def upload_temp_banner(request):
	if request.method == 'POST':
		size = int(request.POST['size'])
		uploaded = request.FILES['image']
		validated = validate_banner(uploaded)

		if validated['error']:
			return_response = 'fail|%s' % validated['msg']			
		else:
			max_width = 0
			max_height = settings.HOME_BANNER_HEIGHT
			if size == 11:
				max_width = settings.HOME_BANNER_WHOLE_WIDTH
			elif size==21 or size==22:
				max_width = settings.HOME_BANNER_HALF_WIDTH
			else:
				max_width = settings.HOME_BANNER_THIRD_WIDTH			

			ret = home_banner(uploaded, max_width, max_height)
			if ret:
				return_response = 'good|%s' % ret
			else:
				return_response = 'fail|Server error. Please contact administrator.'
		return HttpResponse(return_response)
	else:
		return HttpResponseNotFound()

def generate_home_banner_thumb(request,hbiid,width,height):
	try:
		home_banner_image = HomeBannerImages.objects.get(id=hbiid)
		path = '%s%s%s' % (settings.MEDIA_ROOT, "banners/", home_banner_image.image)
		img = pil.open(path)
		img.thumbnail((width, height), pil.ANTIALIAS)
		splittedName = getExtensionAndFileName(home_banner_image.image)
		fname = '%s%s' % (home_banner_image.id,splittedName[1])
		thumb_path = '%s%s%s' % (settings.MEDIA_ROOT, "banners/thumb/", fname)

		background = Image.new('RGBA', size, (255, 255, 255, 0))
		background.paste(im,((size[0] - im.size[0]) / 2, (size[1] - im.size[1]) / 2))

		background.save(path)
	except:
		return HttpResponseNotFound()

@staff_member_required
def manage_home_info_graphic(request):
	info = {}
	info['infographics'] = get_HomeInfographics()
	return render_to_response('admin/manage_home_info_graphic.html',info,RequestContext(request))

@staff_member_required
def upload_info_graphic(request):
	info = {}
	form = HomeInfoGraphicForm()
	info['width'] = settings.HOME_INFO_GRAPHICS_WIDTH
	info['height'] = settings.HOME_INFO_GRAPHICS_HEIGHT

	if request.method == 'POST':
		form = HomeInfoGraphicForm(request.POST)
		if form.is_valid():
			data = form.cleaned_data
			save_response = save_Infographics(data)
			if save_response:
				messages.success(request, _('Successfully added.'))
			else:
				messages.error(request, _('Could not save. Please contact administrator.'))
			return redirect('upload_info_graphic')
	info['form'] = form
	return render_to_response('admin/upload_info_graphic.html',info,RequestContext(request))

@csrf_exempt
def upload_temp_infographic(request):
	if request.method == 'POST':
		uploaded = request.FILES['image']
		validated = validate_Infographic(uploaded)

		if validated['error']:
			return_response = 'fail|%s' % validated['msg']			
		else:
			max_width = 0
			max_height = settings.HOME_INFO_GRAPHICS_HEIGHT
			max_width = settings.HOME_INFO_GRAPHICS_WIDTH		

			ret = manage_infographic(uploaded, max_width, max_height)
			if ret:
				return_response = 'good|%s' % ret
			else:
				return_response = 'fail|Server error. Please contact administrator.'			
		return HttpResponse(return_response)
	else:
		return HttpResponseNotFound()

@csrf_exempt
def set_infographic_status(request):
	if request.method == 'POST':
		id = request.POST['id']
		ret = set_HomeInfographicStatus(id)
		if ret:
			return_response = 'good'
		else:
			return_response = 'fail'
			
		return HttpResponse(return_response)
	else:
		return HttpResponseNotFound()

@csrf_exempt
def set_template_positions(request):
	ret = ""

	if request.method == 'POST':
		obj_counter = request.POST.get('obj_counter','')
		unique_identifier = request.POST.get('unique_identifier','')
		changes_counter = request.POST.get('changes_counter','')
		product_objects = request.POST.get('product_objects','')
		embellishment_objects = request.POST.get('embellishment_objects','')
		box_objects = request.POST.get('box_objects','')

		request.session['template_positions'] = {
			'obj_counter':str(obj_counter),
			'unique_identifier': str(unique_identifier),
			'changes_counter': str(changes_counter),
			'product_objects':str(product_objects),
			'embellishment_objects': str(embellishment_objects),
			'box_objects': str(box_objects)
		}

		ret = obj_counter

	return HttpResponse(ret)

def clear_template_session(request):

	try:
		del request.session['template_positions']
	except:
		pass

def new_template(request):
	clear_template_session(request)
	return redirect('manage_template')

def management_reports(request):
	info = {}
	product_list = Product.objects.all().order_by('sku')
	offset = 25
	paginator = Paginator(product_list, offset)
	page = request.GET.get('page')
	try:
		products = paginator.page(page)
	except PageNotAnInteger:
		products = paginator.page(1)
	except EmptyPage:
		products = paginator.page(paginator.num_pages)

	info['products'] = product_list
	return render_to_response('admin/management_reports.html',info,RequestContext(request))

@csrf_exempt
def update_qty_sold(request):
	if request.method == "POST":
		id = request.POST['id']
		qty_sold = request.POST['qty_sold']
		try:
			p = Product.objects.get(id=id)
			try:
				pd = ProductDetails.objects.get(product=p)
			except:
				pd = ProductDetails()
				pd.product = p
			pd.qty_sold = qty_sold
			pd.save()
			return HttpResponse(1)
		except Exception as e:
			return HttpResponse(0)
	else:
		return HttpResponseNotFound()

import csv

@csrf_exempt
def export_inventory_finance_report(request):
	if request.method == "POST":
		data = request.POST['data']
		request.session['EXPORT_REPORT_DATA'] = data
		# jdata = simplejson.loads(data)		
		# for dd in jdata:
		# 	print dd[0]
		#print jdata
		return HttpResponse(1)
	else:
		return HttpResponseNotFound()

def csv_export_report(request):
	response = HttpResponse(mimetype='text/csv')
	now = datetime.now()
	cvname = '%s%s%s_%s%s%s.csv' % (now.year,now.month,now.day,now.hour,now.minute,now.second)
	print now.hour
	response['Content-Disposition'] = 'attachment; filename="%s"' % cvname
	writer = csv.writer(response)
	reports = request.session['EXPORT_REPORT_DATA']
	jdata = simplejson.loads(reports)

	l = [dd[0].encode('utf-8') for dd in jdata]
	i=0
	for dd in jdata:
		if i > 0:
			
			dd[2] = "'%s" % dd[2]
			# dd[0] = "'%s" % dd[0]
			# dd[3] = "'%s" % dd[3]
			# dd[4] = "'%s" % dd[4]
			# dd[5] = "'%s" % dd[5]
			# dd[6] = "'%s" % dd[6]
			# dd[12] = "'%s" % dd[12]

			# if dd[7] == '0.00' or dd[7] == 0.00:
			# 	dd[7] = ''
			# if dd[11] == '0.00' or dd[11] == 0.00:
			# 	dd[11] = ''
			# if dd[13] == '0.00' or dd[13] == 0.00:
			# 	dd[13] = ''
			# if dd[14] == '0.00' or dd[14] == 0.00:
			# 	dd[14] = ''
			# else:
			# 	try:
			# 		if str(dd[14]).index(',') >= 0 or str(dd[14]).index('.') >= 0:
			# 			pass
			# 	except Exception as e:					
			# 		dd[14] = "'%s" % dd[14]

			# if dd[15] == '0.00' or dd[15] == 0.00:
			# 	dd[15] = ''
			# else:
			# 	try:
			# 		if str(dd[15]).index(',') >= 0 or str(dd[15]).index('.') >= 0:
			# 			pass
			# 	except:
			# 		dd[15] = "'%s" % dd[15]

		l = [unicode_convert(d) for d in dd]
		writer.writerow(l)
		i = i+1
	return response

def unicode_convert(strString):
	strString = '%s' % strString.replace("\\n","\r\n")		
	return strString.encode('utf-8')