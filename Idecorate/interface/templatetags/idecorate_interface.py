from django import template
from django.utils.safestring import mark_safe
from menu.models import FooterCopyright
from category.services import get_sub_categories

register = template.Library()

@register.filter
def get_interface_info(infoType):

	if infoType == "footer":


		copyright = FooterCopyright.objects.get(id=1)

		return mark_safe(copyright.copyright)

@register.filter
def get_parent_category(value):
	parent_category = get_sub_categories(None)

	parent_category = parent_category.order_by('order')
	print parent_category.count()
	tags = """
		<ul>		
	"""
	for cat in parent_category:
		tags += """
			<li><a href="#">%s</a></li>
		""" % cat.name
		
	tags += """
		</ul>
	"""

	return mark_safe(tags)