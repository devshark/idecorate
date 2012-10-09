from django import template
from django.utils.safestring import mark_safe
from category.models import Categories
from menu.models import InfoMenu, SiteMenu, FooterMenu
from category.services import get_categories
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
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

		sub_menus = Categories.objects.filter(parent__id=category.id,deleted=False).order_by('order')

		hidden = ""
		if sub_menus.count() > 0:
			#parent
			hidden = ' style="display:none" disabled="disabled"'
		else:
			#not parent
			hidden = ''

		element += '<li><input class="treeinput" type="checkbox" name="categories" value="%s"%s%s/><label class="treelabel">%s</label>' % (category.id, chk, hidden, category.name)

		element += treeRecursion(sub_menus, req)

		element +='</li>'

	if needToOpen == False:
		element += '</ul>'

	return mark_safe(element)