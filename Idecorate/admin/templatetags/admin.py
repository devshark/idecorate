from django import template
from django.utils.safestring import mark_safe
from category.models import Categories
from menu.models import InfoMenu, SiteMenu, FooterMenu, FatFooterMenu, ItemMenu
from category.services import get_categories
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from cart.models import ProductPrice, ProductDetails, Contact, OrderData
from customer.models import CustomerProfile
from customer.services import customer_profile
from django.contrib.humanize.templatetags.humanize import naturaltime, intcomma
from interface.views import admin as admin2
from django.contrib.auth.models import User
import decimal
from plata.shop.models import OrderPayment
from urllib import quote, quote_plus
from django.utils import simplejson
#from django.utils.translation import ugettext_lazy as _

register = template.Library()

@register.filter
def deleteSession(request, key):
    
    try:
    	del request.session[key]
    except KeyError:
    	pass

    return ""

@register.filter
def checkEmailError(request, isControlGroup):

	if isControlGroup:
		if "admin_login_post" in request.session:
			if str(request.session['admin_username']).strip() == "":
				return "error" 
	else:
		if "admin_login_post" in request.session:
			if str(request.session['admin_username']).strip() == "":
				return mark_safe('<span class="help-inline"><ul class="errorlist"><li>This field is required.</li></ul></span>') 

	return ""

@register.filter
def checkPasswordError(request, isControlGroup):

	if isControlGroup:
		if "admin_login_post" in request.session:
			if str(request.session['admin_password']).strip() == "":
				return "error" 
	else:
		if "admin_login_post" in request.session:
			if str(request.session['admin_password']).strip() == "":
				return mark_safe('<span class="help-inline"><ul class="errorlist"><li>This field is required.</li></ul></span>') 

	return ""

@register.filter
def getItemMenu(menus,is_sub=False):
	menuStr = ""
	if is_sub:
		menuStr += '<ol>'
	else:
		menuStr += '<ol class="sortable">'

	for menu in menus: 
		#LI
		menuStr += """
			<li class="ui-state-default" id="%s">
				<div class="menuDataWrap clearfix">
					<div class="menuData">
						<span class="ui-icon ui-icon-arrowthick-2-n-s"></span>
						<span class="menuName">%s</span>
					</div>
					<div class="menuAction">
						<a data-toggle="modal" href="#myModal" class="editItemMenu" data-item="%s|%s|%s" id="edit_">Edit</a> | 
						<a data-toggle="modal" href="#myModal2" class="delItemMenu" id="%s">Delete</a>
					</div>
				</div>
			""" % (menu.id, menu.name, menu.id, menu.name, menu.link, menu.id)
		#</li> 
			
		sub_menus = ItemMenu.objects.filter(parent=menu.id,deleted=0).order_by('order')
		if sub_menus.count() > 0:
			menuStr += getItemMenu(sub_menus,True)

		menuStr += "</li>"

	menuStr += "</ol>"

	return mark_safe(menuStr)

@register.filter
def getMenus(menus, id):

	return menuRecursion(menus, id)

def menuRecursion(menus, id):

	element = ""
	needToOpen = True
	menuType = 0

	for menu in menus:
		try:
			if menu.parent is None:
				if needToOpen:
					element += '<ol class="sortable" id="%s">' % id
					needToOpen = False

			else:
				if needToOpen:
					element += '<ol>'
					needToOpen = False
		except:
			if needToOpen:
				element += '<ol class="sortable" id="%s">' % id
				needToOpen = False

		if menus.model == type(InfoMenu()):
			menuType = 1
		elif menus.model == type(SiteMenu()):
			menuType = 2
		elif menus.model == type(FatFooterMenu()):
			menuType = 4
		else:
			menuType = 3

		element += '<li class="ui-state-default"><div><span style="display:inline-block;float:right;"><a data-toggle="modal" href="#myModal" onclick="setEdit(\'%s\',\'%s\',\'%s\',\'%s\')">Edit</a> | <a data-toggle="modal" href="#myModal2" onclick="setGlobalURL(\'%s\')">Delete</a></span><span class="menu_id" style="display:none;">%s</span><span class="ui-icon ui-icon-arrowthick-2-n-s"></span>%s</div>' % (menu.id,menu.name,menu.link,menuType,reverse('admin_delete_menu', args=[menu.id,menuType]),menu.id,menu.name)

		if menus.model == type(InfoMenu()):

			sub_menus = InfoMenu.objects.filter(parent__id=menu.id,deleted=False).order_by('order')
			element += menuRecursion(sub_menus, "")

		elif menus.model == type(SiteMenu()):
			sub_menus = SiteMenu.objects.filter(parent__id=menu.id,deleted=False).order_by('order')
			element += menuRecursion(sub_menus, "")
		elif menus.model == type(FooterMenu()):
			sub_menus = FooterMenu.objects.filter(parent__id=menu.id,deleted=False).order_by('order')
			element += menuRecursion(sub_menus, "")

		element +='</li>'

	if needToOpen == False:
		element += '</ol>'

	return mark_safe(element)

@register.filter
def getSubCategories(categories):
	tags = ""
	for cat in categories:
		subcats = get_categories(cat.id)

		cls = ''
		if subcats.count() > 0:
			cls = 'class="sub-menu"'

		tags += '''
			<li %s><a href="#" rel="%s" class="cat" id="ddl-cat-%s"><span>%s</span></a>
		''' % (cls, cat.id, cat.id, cat.name)

		if subcats.count() > 0:
			tags += recursiveSubCat(cat.id)
		tags += "</li>"

	return mark_safe(tags)

def recursiveSubCat(parent_id, level = ""):

	cats = get_categories(parent_id)
	tags = ''

	for cat in cats:
		subcats = get_categories(cat.id)
		arrow = '&rsaquo;'			

		tags += '''
			<li><a href="#" rel="%s" class="cat" id="ddl-cat-%s"> %s <span>%s</span></a>
		''' % (cat.id, cat.id, arrow + level , cat.name)

		if subcats.count() > 0:
			tags += recursiveSubCat(cat.id, arrow + level)

		tags += '</li>'
	tags += ''
	return tags

@register.filter
def generateProductCategories(categories):
	tags = """
		<div class="tab-pane active" id="info_manage_cat">
			<ol class="sortable">
		"""
	for cat in categories:
		subcats = get_categories(cat.id)		
		cat_name = cat.name

		plus_sign = '&nbsp;'

		tags += '''
			<li id="list_%s" class="ui-state-default parent">
				    	<div class="title-holder">
				    		<span class="pull-left plus">%s</span>
				    		<span class="pull-left">%s</span>
				    		<span class="pull-right"><a href="%s">Edit</a> 
				    		| 
				    		<a href="#myModal" rel="%s" role="button" class="btn-delete" data-toggle="modal">Delete</a></span>
				    	</div>
				''' % (cat.id, plus_sign, cat_name, reverse('edit_category', args=[cat.id]), cat.id)
		if subcats.count() > 0:
			tags += generateProductSubCategories(cat.id)

		tags += '''
			</li>
			'''

	tags += """</ol>
		  	</div>
		  """

	return mark_safe(tags)

def generateProductSubCategories(parent_id):
	cats = get_categories(parent_id)
	tags = '<ol id="parent_id_%s">' % parent_id
	for cat in cats:
		subcats = get_categories(cat.id)

		cat_name = cat.name
		plus_sign = '&nbsp;'

		tags += '''
			<li id="list_%s" class="ui-state-default">
				<div class="title-holder">
					<span class="pull-left plus">%s</span>
					<span class="pull-left">%s</span> 
					<span class="pull-right"><a href="%s">Edit</a> | 
					<a href="#myModal" rel="%s" role="button" class="btn-delete" data-toggle="modal">Delete</a></span>
				</div>
		''' % (cat.id, plus_sign, cat_name, reverse('edit_category', args=[cat.id]), cat.id)

		if subcats.count() > 0:
			tags += generateProductSubCategories(cat.id)

		tags += '</li>'
	tags += '</ol>'
	return tags

@register.filter
def generateThumbnailUrl(value):
	tags = ''
	if value:
		tags = '%s' % reverse('category_thumbnail_view', args=[value])
	else:
		tags = '%s' % reverse('category_thumbnail')
	return mark_safe(tags)


@register.filter
def getCategoryTree(categories, req):

	return treeRecursion(categories, req)

def treeRecursion(categories, req):

	element = ""
	needToOpen = True
	attrParent = ""

	for category in categories:
		if category.parent is None:
			attrParent = 'isparent="isparent" '
			if needToOpen:
				element += '<ul id="tree1">'
				needToOpen = False

		else:
			if needToOpen:
				element += '<ul>'
				needToOpen = False

		chk = ""

		if req.method == "POST":

			if str(category.id) in req.POST.getlist('categories'):
				chk = ' checked="checked"'
			else:
				chk = ''
		else:
			try:
				listCats = req.listCats
				#print listCats
				if str(category.id) in listCats:
					chk = ' checked="checked"'
				else:
					chk = ''

			except AttributeError:
				pass

		sub_menus = Categories.objects.filter(parent__id=category.id,deleted=False).order_by('order')

		hidden = ""
		if sub_menus.count() > 0:
			#parent
			#hidden = ' style="display:none" disabled="disabled"'
			hidden = ' style="display:none"'
		else:
			#not parent
			hidden = ''

		element += '<li><input %sclass="treeinput" type="checkbox" name="categories" value="%s"%s%s/><label class="treelabel">%s</label>' % (attrParent, category.id, chk, hidden, category.name)
		attrParent = ""

		element += treeRecursion(sub_menus, req)

		element +='</li>'

	if needToOpen == False:
		element += '</ul>'

	return mark_safe(element)

@register.filter
def getProductCategories(product):

	categories = product.categories.all().order_by('name')
	catList = [cat.name for cat in categories if cat.parent == None]

	return ", ".join(catList)

@register.filter
def getProductPrice(product):
	price = ProductPrice.objects.get(product=product)

	return price._unit_price

@register.filter
def getProductStatus(product):

	return 'Active' if product.is_active else 'Inactive'

@register.filter
def getProductThumbnail(product):

	return mark_safe('<img src="/media/products/%s" alt="" />' % product.original_image_thumbnail)


@register.filter
def getCategoryTreeParentOnly(categories, req):

	element = ""
	needToOpen = True

	for category in categories:
		if category.parent is None:
			if needToOpen:
				element += '<ul id="tree1">'
				needToOpen = False

		else:
			if needToOpen:
				element += '<ul>'
				needToOpen = False

		chk = ""

		if req.method == "POST":

			if str(category.id) in req.POST.getlist('categories'):
				chk = ' checked="checked"'
			else:
				chk = ''
		else:
			try:
				listCats = req.listCats
				if str(category.id) in listCats:
					chk = ' checked="checked"'
				else:
					chk = ''

			except AttributeError:
				pass

		hidden = ""

		element += '<li><input class="treeinput" type="checkbox" name="categories" value="%s"%s%s/><label class="treelabel">%s</label>' % (category.id, chk, hidden, category.name)

		element +='</li>'

	if needToOpen == False:
		element += '</ul>'

	return mark_safe(element)

@register.filter
def getEmbellishmentThumbnail(embellishment):

	eDirectory = ""

	if embellishment.e_type.id == 1:
		eDirectory = "images"
	elif embellishment.e_type.id == 2:
		eDirectory = "textures"
	elif embellishment.e_type.id == 3:
		eDirectory = "patterns"
	elif embellishment.e_type.id == 4:
		eDirectory = "shapes"
	elif embellishment.e_type.id == 5:
		eDirectory = "borders"


	return mark_safe('<img src="/media/embellishments/%s/%s" alt="" />' % (eDirectory,embellishment.image_thumb))

@register.filter
def getEmbellishmentStatus(embellishment):

	return 'Active' if embellishment.is_active else 'Inactive'

@register.filter
def getFontPreview(font):

	return mark_safe('<img src="%s?font_size=100&font_text=Abc&font_color=000000000&font_id=%s&font_thumbnail=1" alt="" />' % (reverse('generate_text'),font.id))

@register.filter
def getFontStatus(font):

	return 'Active' if font.is_active else 'Inactive'

@register.filter
def getUserStatus(user):

	return 'Active' if user.is_active else 'Inactive'

@register.filter
def getUserNickname(user):

	ret = ""

	if user.first_name != "" and user.last_name != "":
		ret = "%s %s" % (user.first_name, user.last_name)
	else:

		try:
			profile = CustomerProfile.objects.get(user=user)
			ret = profile.nickname
		except:
			pass

	return mark_safe(ret)

@register.filter
def getUserNicknameOnly(user):

	ret = ""

	try:
		profile = CustomerProfile.objects.get(user=user)
		ret = profile.nickname
	except:
		pass

	return mark_safe(ret)

@register.filter
def getUserType(user):

	if user.is_staff and user.is_superuser:
		return 'Admin'
	elif user.is_staff and not user.is_superuser:
		return 'Store Manager'
	else:
		return 'Member'

	#return 'Admin' if user.is_staff else 'Member'

@register.filter
def getUserActivity(user):

	ret = ""

	if user.date_joined.year == user.last_login.year and user.date_joined.month == user.last_login.month and user.date_joined.day == user.last_login.day and user.date_joined.hour == user.last_login.hour and user.date_joined.minute == user.last_login.minute:
		ret = "%s%s" % ("Registered ", naturaltime(user.date_joined))
	else:
		ret = "%s%s" % ("Logged in ", naturaltime(user.last_login))

	return mark_safe(ret)

@register.filter
def user_enable_disable(user):

	ret = ''
	retStat = ""

	if user.is_active:
		retStat = "Deactivate"
	else:
		retStat = "Activate"

	ret = '<a data-toggle="modal" class="mod_btn" href="#myModal1" onclick="setGlobalURL(\'%s\')">%s</a>' % (reverse('admin_stat_user', args=[user.id]), retStat)

	return mark_safe(ret)

@register.filter
def get_images(home_banner_id):
	images = admin2.models.HomeBannerImages.objects.filter(home_banner__id=home_banner_id).order_by('id')
	ret = ''
	i=1
	for image in images:
		ret += '<a href="#" rel="%s">Image %s</a><br />' % (image.image, i);
		++i
	
	return images

@register.filter
def getProductCategoryName(product):
	res = ''
	for p in product.categories.all():
		res += '%s<br>' % p.name
	return mark_safe(res)

def getProductDetails(product):
	try:
		return ProductDetails.objects.get(product=product)
	except:
		return False

@register.filter
def getProductDetail(product,what):
	prod = getProductDetails(product)
	if not prod:
		return ''
	else:
		r = ''
		if what=='comment':
			if prod.comment:
				r = mark_safe(prod.comment)				
		elif what=='size':
			r = prod.size
		elif what=='colour':
			r = prod.color
		elif what=='unitprice':
			r = prod.unit_price
		elif what=='pcsctn':
			r = prod.pieces_carton
		elif what=='moqctns':
			r = prod.min_order_qty_carton
		elif what=='moqunits':
			r = prod.min_order_qty_pieces
		elif what=='costofmoq':
			r = prod.cost_min_order_qty
		elif what=='qtysold':
			r = prod.qty_sold
		elif what=='cogs':
			up = prod.unit_price
			if not up:
				up = 0
			qs = prod.qty_sold
			if not qs:
				qs = 0 
			r = decimal.Decimal(up)*decimal.Decimal(qs)
		elif what=='rev':
			qs = prod.qty_sold
			if not qs:
				qs = 0 


		if not r:
			r = ''

		return r

@register.filter
def currency(dollars):
	if dollars != '':
		dollars = round(float(dollars), 2)
		return "%s%s" % (intcomma(int(dollars)), ("%0.2f" % dollars)[-3:])
	else:
		return '0.00'


def getRevenueRaw(product):
	retail_price = getProductPrice(product)
	qty_sold = getProductDetail(product,'qtysold')
	qs = qty_sold
	if not qs:
		qs = 0
	else:
		qs = decimal.Decimal(qty_sold)

	rev = qs*decimal.Decimal(retail_price)
	return rev

@register.filter
def getRevenue(product):
	rev = getRevenueRaw(product)
	if rev <= 0:
		rev = ''
	else:
		rev = currency(rev)

	return rev

@register.filter
def getNetProfit(product):
	rev = getRevenueRaw(product)	
	cogs = getProductDetail(product,'cogs')	
	if not rev:
		rev = 0
	else:
		rev = decimal.Decimal(rev)

	if not cogs:
		cogs = 0
	else:
		cogs = decimal.Decimal(cogs)
	net_profit = rev-cogs
	if not net_profit:
		net_profit = '0.00'
	else:
		net_profit = currency(net_profit)
	return net_profit

@register.filter
def getExcessStock(product):
	moqunits = getProductDetail(product, 'moqunits')
	qtysold = getProductDetail(product, 'qtysold')

	if not moqunits:
		moqunits = 0
	if not qtysold:
		qtysold = 0

	excessstock = moqunits-qtysold
	return excessstock

@register.filter
def getOppCostExcess(product):
	retail_price = getProductPrice(product)
	excess = getExcessStock(product)

	if not retail_price:
		retail_price = 0
	else:
		retail_price = decimal.Decimal(retail_price)
	if not excess:
		excess = 0
	else:
		excess = decimal.Decimal(excess)

	opp_cost = retail_price*excess

	return currency(opp_cost)

@register.filter
def getProductCategories2(product):

	categories = product.categories.all().order_by('name')
	catList = [cat.name for cat in categories if cat.parent == None]

	return mark_safe("<br>".join(catList))

@register.filter
def form_field(value, classes=""):
	field = """
		<div class="row-fluid">
			<div class="span12">
				<div class="control-group">
					<label class="control-label">%s *</label>
					<div class="controls">
						%s
						<span class="help-block">%s</span>
					</div>
				</div>
			</div>
		</div>
	""" % (unicode(value.name), unicode(value.label), required_marker, value, value.help_text)
	return mark_safe(field)

@register.filter
def get_userprofile(user_id):
	user 	= User.objects.get(id=user_id)
	profile = customer_profile(user=user)

	if user.first_name != "":
		profile['nickname'] = user.first_name
	else:
		profile['nickname'] = user.username

	if profile['picture']:
		p_user = """<img src="%s" style="width:23px;height:23px;" alt="" />""" % (profile['picture'])
	else:
		p_user = """<img src="/media/images/man.png" alt="" />"""
	
	p_user += """<span class="member" style="margin-left:10px;">by %s</span>""" % (profile['nickname'])
		
	return mark_safe(p_user)

@register.filter
def readable_status(value):
	#: Order object is a cart.
    #CART = 10
    #: Checkout process has started.
    #CHECKOUT = 20
    #: Order has been confirmed, but it not (completely) paid for yet.
    #CONFIRMED = 30
    #: Order has been completely paid for.
    #PAID = 40
    #: Order has been completed. Plata itself never sets this state,
    #: it is only mean
    data = {
		'5':'Failed',
		'20':'Checkout',
		'30':'Pending',
		'40':'Paid',
		'45':'Payment Received',
		'46':'Pending Delivery',
		'50':'Completed'
	}
	
    return data[str(value)]

@register.filter
def readable_status_payment(value):

	try:
		data = {
			'PayPal':'PayPal',
			'Visa':'Visa',
			'Mastercard':'Mastercard',
			'American_Express': 'American Express'
		}

		return data[str(value)]
	except Exception as e:
		return 'N/A'

@register.filter
def get_order_detail(order,what):

	result = ""

	# try: 

	result = get_order(order).get(what, None)

	# except :

		# pass

	# if not result:

	# 	if what == 'payment_method' or what == 'delivery_date' or what == 'contact_number':

	# 		try:
	# 			orderDatum = OrderData.objects.get(order=order)

	# 			data = simplejson.loads(orderDatum.data)

	# 			needed = {
	# 				'payment_method': data.get('order-payment_method', None),
	# 				'delivery_date': data.get('delivery_date', None),
	# 				'contact_number': data.get('contact_number', None)
	# 			}
				
	# 			result = needed[what]

	# 		except Exception as e:

	# 			print e
	# 			pass

	return result

@register.filter
def get_order(order):

	try:
		oPayment = OrderPayment.objects.get(order=order)
	except:
		oPayment = None

	#contact = Contact.objects.get(user=order.user)
	o = {}
	o['id'] 				= str(order.id)
	o['status'] 			= str(order.status)

	if oPayment:
		o['payment_method'] = str(oPayment.payment_method)
		o['delivery_date'] 	= str(oPayment.data.get('delivery_date',''))
		o['contact_number']	= str(oPayment.data.get('contact_number',''))
	else:
		o['payment_method'] = ''
		o['delivery_date']	= ''

	o['first_name'] 		= str(order.billing_first_name)
	o['last_name'] 			= str(order.billing_last_name)
	o['email'] 				= str(order.email)
	o['delivery_address'] 	= str(order.shipping_address)

	if 'delivery_address2' in order.data:
		o['delivery_address2'] = str(order.data['delivery_address2'])
	else:
		o['delivery_address2'] = ''

	o['delivery_city'] = str(order.shipping_city)

	if 'delivery_state' in order.data:
		o['delivery_state'] = str(order.data['delivery_state'])
	else:
		o['delivery_state'] = ''

	o['delivery_zip_code']	= str(order.shipping_zip_code)

	if 'delivery_country' in order.data:
		o['delivery_country'] = str(order.data['delivery_country'])
	else:
		o['delivery_country'] = ''

	o['billing_address'] 	= str(order.billing_address)

	if 'billing_address2' in order.data:
		o['billing_address2'] = str(order.data['billing_address2'])
	else:
		o['billing_address2'] = ''

	o['billing_city'] = str(order.billing_city)


	if 'billing_state' in order.data:
		o['billing_state'] = str(order.data['billing_state'])
	else:
		o['billing_state'] = ''

	o['billing_zip_code']	= str(order.billing_zip_code)

	if 'billing_country' in order.data:
		o['billing_country'] = str(order.data['billing_country'])
	else:
		o['billing_country'] = ''
	
	o['note'] 				= order.notes

	
	return o

@register.filter
def multiply(val1, val2):
	return val1*val2

@register.filter
def get_order_safe(order):

	return mark_safe(get_order(order))

@register.filter
def get_order_json(order):

	return simplejson.dumps(get_order(order))
	
@register.filter
def py_boolean_js(boolean):

	return simplejson.dumps(boolean)