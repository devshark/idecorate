from django import template
from django.utils.safestring import mark_safe
from category.models import Categories
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



def test_recursion():

	cat = Categories.objects.filter(parent__id=None)

	recursion_function(cat)


def recursion_function(obj):

	print obj.count()

	for o in obj:

		cat = Categories.objects.filter(parent__id=o.id)

		recursion_function(cat)

