from models import InfoMenu, SiteMenu, FooterMenu


def addMenu(name, link, menuType):

	if menuType == "1":
		menu = InfoMenu()
	elif menuType == "2":
		menu = SiteMenu()

	else:
		menu = FooterMenu()


	menu.name = name
	menu.link = link
	menu.order = 1
	menu.save()
