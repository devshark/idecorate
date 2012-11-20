from django import template
from django.utils.safestring import mark_safe
from category.models import Categories
from menu.models import InfoMenu, SiteMenu, FooterMenu
from category.services import get_categories
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from cart.models import ProductPrice
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
def getMenus(menus, id):

	return menuRecursion(menus, id)

def menuRecursion(menus, id):

	element = ""
	needToOpen = True
	menuType = 0

	for menu in menus:
		if menu.parent is None:
			if needToOpen:
				element += '<ol class="sortable" id="%s">' % id
				needToOpen = False

		else:
			if needToOpen:
				element += '<ol>'
				needToOpen = False

		if menus.model == type(InfoMenu()):
			menuType = 1
		elif menus.model == type(SiteMenu()):
			menuType = 2
		else:
			menuType = 3

		element += '<li class="ui-state-default"><div><span style="display:inline-block;float:right;"><a data-toggle="modal" href="#myModal" onclick="setEdit(\'%s\',\'%s\',\'%s\',\'%s\')">Edit</a> | <a data-toggle="modal" href="#myModal2" onclick="setGlobalURL(\'%s\')">Delete</a></span><span class="menu_id" style="display:none;">%s</span><span class="ui-icon ui-icon-arrowthick-2-n-s"></span>%s</div>' % (menu.id,menu.name,menu.link,menuType,reverse('admin_delete_menu', args=[menu.id,menuType]),menu.id,menu.name)

		if menus.model == type(InfoMenu()):

			sub_menus = InfoMenu.objects.filter(parent__id=menu.id,deleted=False).order_by('order')
			element += menuRecursion(sub_menus, "")

		elif menus.model == type(SiteMenu()):
			sub_menus = SiteMenu.objects.filter(parent__id=menu.id,deleted=False).order_by('order')
			element += menuRecursion(sub_menus, "")
		else:
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