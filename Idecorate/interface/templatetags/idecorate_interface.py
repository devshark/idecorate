from django import template
from django.utils.safestring import mark_safe
from menu.models import FooterCopyright, InfoMenu, SiteMenu, FooterMenu
from category.services import get_categories, category_tree_crumb, get_cat
from django.core.urlresolvers import reverse
from idecorate_settings.models import IdecorateSettings

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
def get_parent_category(value):
	parent_category = get_categories(None)

	parent_category = parent_category.order_by('order')
	tags = """
		<ul>		
	"""
	for cat in parent_category:
		tags += """
			<li><a href="%s">%s</a></li>
		""" % (reverse('styleboard_cat', args=[cat.id]), cat.name)
		
	tags += """
		</ul>
	"""

	return mark_safe(tags)

def menuInterfaceRecursion(menus):

	element = ""
	needToOpen = True
	css_class = ""
	link = ""
	spanOpen = ""
	spanClose = ""

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
			spanOpen = '<span>'
			spanClose = '</span>'
		else:
			css_class = ''
			link = '<a href="%s">%s</a>' % (menu.link, menu.name)
			spanOpen = ''
			spanClose = ''

		element += '<li%s>%s%s' % (css_class, spanOpen, link)

		if menus.model == type(InfoMenu()):

			sub_menus = InfoMenu.objects.filter(parent__id=menu.id,deleted=False).order_by('order')
			element += menuInterfaceRecursion(sub_menus)

		else:
			sub_menus = SiteMenu.objects.filter(parent__id=menu.id,deleted=False).order_by('order')
			element += menuInterfaceRecursion(sub_menus)

		element += '%s</li>' % spanClose

	if needToOpen == False:
		element += '</ul>'

	return mark_safe(element)

@register.filter
def getInterfaceMenus(menuType):

	if menuType == "info":
		menus = InfoMenu.objects.filter(parent=None,deleted=False).order_by('order')
	else:
		menus = SiteMenu.objects.filter(parent=None,deleted=False).order_by('order')

	return menuInterfaceRecursion(menus)

@register.filter
def get_breadcrumb(parent_id):
	if parent_id:
		cat_tree = category_tree_crumb(parent_id)
		tags = '<ul class="breadcrumb">'
		tags += '<li><a href="#">All</a></li>'
		arr = cat_tree.split('|')
		i = len(arr)

		while i != 0:
			cc = arr[i-1].split(':')
			if i==1:
				tags += '<li> > </li><li class="active">%s</li>' % (cc[1])
			else:
				tags += '<li> > </li><li><a rel="%s" href="#">%s</a></li>' % (cc[0], cc[1])
			i = i-1

		tags += '</ul>'
		return mark_safe(tags)

	return ''

@register.filter
def generate_product_order_list(obj,objMain):
	products = obj.filter()
	ret = ""

	for product in products:

		ret += """
						<tr>
							<td>
								<img src="/media/products/%s" align="left" />
								<span>%s</span>
							</td>
							<td valign="middle" class="productPricing">
								%s %s
							</td>
							<td valign="middle" class="productPricing">
								%s
							</td>
							<td valign="middle" class="productPricing">
								%s %s
							</td>
						</tr>
		""" % (product.product.original_image_thumbnail, product.product.name, objMain.currency, "%.2f" % product.unit_price, product.quantity, objMain.currency, "%.2f" % product.discounted_subtotal)

	return mark_safe(ret)

@register.filter
def get_checkout_page_info(inf):

	idecorate_settings = IdecorateSettings.objects.get(pk=1)

	if inf == "delivery_date_note":
		return idecorate_settings.delivery_date_note
	elif inf == "any_question":
		return idecorate_settings.any_question
	elif inf == "t_and_c":
		return idecorate_settings.t_and_c
	else:
		return ""