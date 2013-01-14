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
	pass
	# for i in arrangement:
	# 	itemMenus 		= ItemMenu.objects.get(id = i)

	# 	if a != "":
	# 		splitValues = a.split(':')
	# 		arrange_footer = FooterMenu.objects.get(id=int(splitValues[0]))
	# 		arrange_footer.order = int(splitValues[1])

	# 		if splitValues[2].strip() == "None":
	# 			arrange_footer.parent = None
	# 		else:
	# 			arrange_footer.parent = FooterMenu.objects.get(id=int(splitValues[2]))

	# 		arrange_footer.save()
	# info['footer_message'] = True
	# messages.success(request, _('Arrangement saved.'))