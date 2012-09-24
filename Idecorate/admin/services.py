from category.models import Categories

def save_category(data):
	print data
	category_name = data['name']

	try:
		category = Categories()

		try:
			cat = Categories.objects.get(id=data['parent'])
			category.parent = cat
		except:
			pass
		
		category.name = category_name
		category.save()
		return True
	except:
		return False

