from django import template
from django.utils.safestring import mark_safe
from category.models import Categories
from category.services import get_sub_categories
from django.core.urlresolvers import reverse
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
def getSubCategories(categories):
	tags = ""
	for cat in categories:
		subcats = get_sub_categories(cat.id)

		cls = ''
		if subcats.count() > 0:
			cls = 'class="sub-menu"'

		tags += '''
			<li %s><a href="#" rel="%s" class="cat"><span>%s</span></a>
		''' % (cls, cat.id, cat.name)

		if subcats.count() > 0:
			tags += recursiveSubCat(cat.id)
		tags += "</li>"

	return mark_safe(tags)

def recursiveSubCat(parent_id):

	cats = get_sub_categories(parent_id)
	tags = '<ul class="dropdown-submenu">'
	for cat in cats:
		subcats = get_sub_categories(cat.id)

		tags += '''
			<li><a href="#" rel="%s" class="cat"> - <span>%s</span></a>
		''' % (cat.id, cat.name)

		if subcats.count() > 0:
			tags += recursiveSubCat(cat.id)

		tags += '</li>'
	tags += '</ul>'
	return tags

@register.filter
def generateProductCategories(categories):
	tags = ''
	for cat in categories:
		subcats = get_sub_categories(cat.id)		
		cat_name = cat.name
		if subcats.count() > 0:
			cat_name = '<span class="togglePlus">+</span> %s' % cat_name

		tags += '''
			<div class="tab-pane active" id="info_manage_menu_%s">			
				<ol class="sortable" id="sortable_parent_%s">
				    <li id="list_%s" class="ui-state-default">
				    	<div class="title-holder"><span class="ui-icon ui-icon-arrowthick-2-n-s pull-left"></span><span class="pull-left">%s</span><span class="pull-right"><a href="%s">Edit</a> | <a href="#" rel="%s" class="btn-delete">Delete</a></span></div>
				''' % (cat.id, cat.id, cat.id, cat_name, reverse('edit_category', args=[cat.id]), cat.id)
		if subcats.count() > 0:
			tags += generateProductSubCategories(cat.id)

		tags += '''</li></ol>
		  	</div>'''

	return mark_safe(tags)

def generateProductSubCategories(parent_id):
	cats = get_sub_categories(parent_id)
	tags = '<ol id="parent_id_%s">' % parent_id
	for cat in cats:
		subcats = get_sub_categories(cat.id)

		cat_name = cat.name
		if subcats.count() > 0:
			cat_name = '<span class="togglePlus">+</span> %s %s' % (cat_name, subcats.count())

		tags += '''
			<li id="list_%s" class="ui-state-default"><div class="title-holder"><span class="ui-icon ui-icon-arrowthick-2-n-s pull-left"></span> <span class="pull-left">%s</span> <span class="pull-right"><a href="%s">Edit</a> | <a href="#" rel="%s" class="btn-delete">Delete</a></span></div>
		''' % (cat.id, cat_name, reverse('edit_category', args=[cat.id]), cat.id)

		if subcats.count() > 0:
			tags += generateProductSubCategories(cat.id)

		tags += '</li>'
	tags += '</ol>'
	return tags
