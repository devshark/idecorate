from django import template
from django.utils.safestring import mark_safe
from menu.models import FooterCopyright, InfoMenu, SiteMenu, FooterMenu

register = template.Library()

@register.filter
def get_interface_info(infoType):

	if infoType == "footer":


		copyright = FooterCopyright.objects.get(id=1)

		return mark_safe(copyright.copyright)

	elif infoType == "footer_menu":
		element = '<ul>'

		footer_menus = FooterMenu.objects.filter(parent=None,deleted=False).order_by('order')
		link = ""

		for menu in footer_menus:

			if menu.link == "":
				link = menu.name
			else:
				link = '<a href="%s">%s</a>' % (menu.link, menu.name)

			element += '<li>%s</li>' % link

		element += '</ul>'

		return mark_safe(element)

@register.filter
def getInterfaceMenus(menuType):

	if menuType == "info":
		menus = InfoMenu.objects.filter(parent=None,deleted=False).order_by('order')
	else:
		menus = SiteMenu.objects.filter(parent=None,deleted=False).order_by('order')

	return menuInterfaceRecursion(menus)

def menuInterfaceRecursion(menus):

	element = ""
	needToOpen = True
	css_class = ""
	link = ""

	for menu in menus:
		if menu.parent is None:
			if needToOpen:
				element += '<ul class="dropdown clearfix">'
				needToOpen = False

		else:
			if needToOpen:
				element += '<ul>'
				needToOpen = False

		if menu.link == "":
			css_class = ' class="nonLink"'
			link = menu.name
		else:
			css_class = ''
			link = '<a href="%s">%s</a>' % (menu.link, menu.name)

		element += '<li%s>%s' % (css_class, link)

		if menus.model == type(InfoMenu()):

			sub_menus = InfoMenu.objects.filter(parent__id=menu.id,deleted=False).order_by('order')
			element += menuInterfaceRecursion(sub_menus)

		else:
			sub_menus = SiteMenu.objects.filter(parent__id=menu.id,deleted=False).order_by('order')
			element += menuInterfaceRecursion(sub_menus)

		element +='</li>'

	if needToOpen == False:
		element += '</ul>'

	return mark_safe(element)