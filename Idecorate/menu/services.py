from models import InfoMenu, SiteMenu, FooterMenu, FatFooterMenu, ItemMenu
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
		if FatFooterMenu.objects.all().count() > 0:
			max_order = FatFooterMenu.objects.all().aggregate(Max('order'))
		else:
			max_order = {}
			max_order['order__max'] = 0


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
	for i,val in enumerate(arrangement):
		val = val.split(':')
		itemMenus 		= ItemMenu.objects.get(id = val[0])
		itemMenus.order = int(val[1])
		itemMenus.parent_id = None if  val[2] == 'None'  else int(val[2])
		itemMenus.save()

def updateItemMenu(data):
	item_menu_id 	= data['id']
	item_menu_name 	= data['name']
	item_menu_link 	= data['link']

	if item_menu_name.strip() == "":
		info['error_edit'] = True
	else:
		item_menu = ItemMenu.objects.get(id=int(item_menu_id))
		item_menu.name = item_menu_name
		item_menu.link = item_menu_link
		item_menu.save()