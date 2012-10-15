from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import HttpResponse, redirect, render_to_response
from django.contrib.auth import authenticate, login, logout
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from admin.models import LoginLog
from datetime import datetime, timedelta
from django.template import RequestContext
from admin.forms import MenuAddForm, FooterCopyRightForm, AddProductForm, SearchProductForm
from menu.services import addMenu
from menu.models import InfoMenu, SiteMenu, FooterMenu, FooterCopyright
from django.contrib.sites.models import Site
from django.views.decorators.csrf import csrf_exempt
from django.template.defaultfilters import filesizeformat
from django.conf import settings
from services import getExtensionAndFileName
from cart.models import Product, ProductPrice
from plata.shop.models import TaxClass
import shutil
from PIL import Image
import os
from category.models import Categories

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

def admin_login(request):

	if request.method == 'POST':

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

			if user.is_active:
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

    		#CREATE THUMBNAIL
    		imgSize = (settings.PRODUCT_THUMBNAIL_WIDTH, settings.PRODUCT_THUMBNAIL_HEIGHT)
    		splittedName = getExtensionAndFileName(form.cleaned_data['original_image'])
    		thumbName = "%s%s" % (splittedName[0], '_thumbnail.jpg')

    		img = Image.open("%s%s%s" % (settings.MEDIA_ROOT, "products/temp/", form.cleaned_data['original_image']))
    		img.thumbnail(imgSize,Image.ANTIALIAS)
    		bgImg = Image.new('RGBA', imgSize, (255, 255, 255, 0))
    		bgImg.paste(img,((imgSize[0] - img.size[0]) / 2, (imgSize[1] - img.size[1]) / 2))
    		bgImg.save("%s%s%s" % (settings.MEDIA_ROOT, "products/", thumbName))

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
    		product.original_image = form.cleaned_data['original_image']
    		product.no_background = form.cleaned_data['no_background']
    		product.original_image_thumbnail = thumbName
    		product.sku = form.cleaned_data['product_sku']
    		product.save()

    		#add category
    		catPostLists = request.POST.getlist('categories')
    		for catPostList in catPostLists:
    			cat = Categories.objects.get(id=int(catPostList))

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

    		productPrice = ProductPrice()
    		productPrice.product = product
    		productPrice._unit_price = form.cleaned_data['price']
    		productPrice.currency = settings.CURRENCIES[0] #USD
    		productPrice.tax_included = False
    		productPrice.tax_class = TaxClass.objects.get(pk=1)
    		productPrice.save()

    		#MOVE FILES
    		shutil.move("%s%s%s" % (settings.MEDIA_ROOT, "products/temp/", form.cleaned_data['original_image']), "%s%s%s" % (settings.MEDIA_ROOT, "products/", form.cleaned_data['original_image']))
    		shutil.move("%s%s%s" % (settings.MEDIA_ROOT, "products/temp/", form.cleaned_data['no_background']), "%s%s%s" % (settings.MEDIA_ROOT, "products/", form.cleaned_data['no_background']))
    		
    		messages.success(request, _('Product Saved.'))
    		return redirect('admin_create_product')

    info['form'] = form
    return render_to_response('admin/admin_create_product.html',info,RequestContext(request))

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
					os.unlink("%s%s%s" % (settings.MEDIA_ROOT, "products/temp/", newFileName))
					newFileName = "%s%s" % (splittedName[0], ".jpg")
					img.save("%s%s%s" % (settings.MEDIA_ROOT, "products/temp/", newFileName))

				return HttpResponse('ok:%s' % newFileName)
		else:
			return HttpResponse(_('notok:File type is not supported').encode('utf-8'))


@staff_member_required
def admin_manage_product(request):
    info = {}
    info['categories'] = Categories.objects.filter(parent__id=None,deleted=False).order_by('order')
    form = SearchProductForm()
    products = Product.objects.filter().order_by('sku')

    categories = Categories.objects.filter(deleted=False).order_by('order')    

    catList = []
    for category in categories:
    	catList.append((str(category.id),category.name))

    form.fields['categories'].choices = tuple(catList)

    if request.method == "POST":

    	form = SearchProductForm(request.POST)
    	form.fields['categories'].choices = tuple(catList)

    	if form.is_valid():
    		pass

    info['form'] = form
    info['products'] = products
    return render_to_response('admin/admin_manage_product.html',info,RequestContext(request))