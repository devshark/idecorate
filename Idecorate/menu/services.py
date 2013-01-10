from models import InfoMenu, SiteMenu, FooterMenu, ItemMenu
from django.db.models import Max

def addMenu(name, link, menuType):

	if menuType == "1":
		menu = InfoMenu()
		max_order = InfoMenu.objects.filter(parent__id=None).aggregate(Max('order'))
	elif menuType == "2":
		menu = SiteMenu()
		max_order = SiteMenu.objects.filter(parent__id=None).aggregate(Max('order'))
	else:
		menu = FooterMenu()
		max_order = FooterMenu.objects.filter(parent__id=None).aggregate(Max('order'))


	menu.name = name
	menu.link = link
	menu.order = max_order['order__max'] + 1
	menu.save()


def saveItemMenu(data):
	itemMenus 		= ItemMenu.objects.all()
	if itemMenus.count() > 0: 
		max_order = itemMenus.aggregate(Max('order'))
		order = max_order['order__max'] + 1
	else:
		order = 1
	newItem 		= ItemMenu()
	newItem.name 	= data['name']
	newItem.link 	= data['link']
	newItem.order 	= order
	newItem.save()

def arrangeItemMenu(arrangement):
	for i in arrangement:
		itemMenus 		= ItemMenu.objects.get(id = i)