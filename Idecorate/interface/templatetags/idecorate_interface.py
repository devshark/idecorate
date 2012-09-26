from django import template
from django.utils.safestring import mark_safe
from menu.models import FooterCopyright

register = template.Library()

@register.filter
def get_interface_info(infoType):

	if infoType == "footer":


		copyright = FooterCopyright.objects.get(id=1)

		return mark_safe(copyright.copyright)
