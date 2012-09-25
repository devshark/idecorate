from django import template
from django.utils.safestring import mark_safe
from category.models import Categories
from menu.models import InfoMenu, SiteMenu, FooterMenu
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

def recursiveSubCat(parent_id, tags):

	cats = Categories.objects.filter(parent__id=parent_id)
	tags += '<ul class="dropdown-submenu">'
	for cat in cats:
		subcats = Categories.objects.filter(parent__id=cat.id)

		tags += '''
			<li><a href="#" rel="%s" class="cat"> - <span>%s</span></a>
		''' % (cat.id, cat.name)

		if subcats.count() > 0:
			tags += recursiveSubCat(cat.id, "")

		tags += '</li>'
	tags += '</ul>'
	return tags

@register.filter
def getSubCategories(categories):
	tags = ""
	for cat in categories:
		subcats = Categories.objects.filter(parent__id=cat.id)

		cls = ''
		if subcats.count() > 0:
			cls = 'class="sub-menu"'

		tags += '''
			<li %s><a href="#" rel="%s" class="cat"><span>%s</span></a>
		''' % (cls, cat.id, cat.name)

		if subcats.count() > 0:
			tags += recursiveSubCat(cat.id, "")
		tags += "</li>"

	return mark_safe(tags)

@register.filter
def getMenus(menus, id):

	return menuRecursion(menus, id)

def menuRecursion(menus, id):

	element = ""
	needToOpen = True

	for menu in menus:
		if menu.parent is None:
			if needToOpen:
				element += '<ol class="sortable" id="%s">' % id
				needToOpen = False

		else:
			if needToOpen:
				element += '<ol>'
				needToOpen = False

		element += '<li class="ui-state-default"><div><span style="display:inline-block;float:right;"><a href="#">DELETE</a></span><span class="menu_id" style="display:none;">%s</span><span class="ui-icon ui-icon-arrowthick-2-n-s"></span>%s</div>' % (menu.id,menu.name)

		if menus.model == type(InfoMenu()):

			sub_menus = InfoMenu.objects.filter(parent__id=menu.id).order_by('order')
			element += menuRecursion(sub_menus, "")

		elif menus.model == type(SiteMenu()):
			sub_menus = SiteMenu.objects.filter(parent__id=menu.id).order_by('order')
			element += menuRecursion(sub_menus, "")
		else:
			sub_menus = FooterMenu.objects.filter(parent__id=menu.id).order_by('order')
			element += menuRecursion(sub_menus, "")

		element +='</li>'

	if needToOpen == False:
		element += '</ol>'

	return mark_safe(element)



def test_recursion():

	cat = Categories.objects.filter(parent__id=None)

	recursion_function(cat)


def recursion_function(obj):

	print obj.count()

	for o in obj:

		cat = Categories.objects.filter(parent__id=o.id)

		recursion_function(cat)

