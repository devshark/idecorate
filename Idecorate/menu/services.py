from models import InfoMenu, SiteMenu, FooterMenu, FatFooterMenu
from django.db.models import Max

def addMenu(name, link, menuType):

	if menuType == "1":
		menu = InfoMenu()
		max_order = InfoMenu.objects.filter(parent__id=None).aggregate(Max('order'))
	elif menuType == "2":
		menu = SiteMenu()
		max_order = SiteMenu.objects.filter(parent__id=None).aggregate(Max('order'))
	elif menuType == "3":
		menu = FooterMenu()
		max_order = FooterMenu.objects.filter(parent__id=None).aggregate(Max('order'))
	else:
		menu = FatFooterMenu()
		max_order = FatFooterMenu.objects.all().aggregate(Max('order'))


	menu.name = name
	menu.link = link
	menu.order = max_order['order__max'] + 1
	menu.save()
