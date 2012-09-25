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
		category.thumbnail = data['thumbnail']
		category.save()
		return True
	except Exception as e:
		print e
		return False

def get_sub_categories(parent_id):
	return Categories.objects.filter(parent__id=parent_id)
