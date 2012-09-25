from category.models import Categories
import os

def save_category(data):
	category_name = data['name']

	try:
		try:
			category = Categories.objects.get(id=data['id'])
			os.unlink(category.thumbnail.path)
		except:
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

def delete_category(category_id):
	try:
		category = Categories.objects.get(id=category_id)
		sub_categories_count = Categories.objects.get(parent__id=category.id).count()
		if sub_categories_count > 0:
			delete_sub_category(cat.id)

		category.delete()
		return True
	except:
		return False

def delete_sub_category(parent_id):
	try:
		sub_categories = Categories.objects.get(parent__id=parent_id)
		for cat in sub_categories:
			has_sub_cat = Categories.objects.filter(parent__id=cat.id).count()
			if has_sub_cat > 0:
				delete_sub_category(cat.id)

		sub_categories.delete()

	except:
		pass