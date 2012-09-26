import os
from django.db.models import Max
from category.models import Categories
from django.utils.safestring import mark_safe

def save_category(data):
	category_name = data['name']

	try:
		try:
			category = Categories.objects.get(id=data['id'])
			os.unlink(category.thumbnail.path)
		except:
			category = Categories()
			category.order = get_next_order(data['parent'])

		try:
			cat = Categories.objects.get(id=data['parent'])
			category.parent = cat
		except:
			pass
		
		if data['thumbnail']:
			category.thumbnail = data['thumbnail']

		category.name = category_name
		
		category.save()
		return True
	except Exception as e:
		return False

def get_sub_categories(parent_id):
	return Categories.objects.filter(parent__id=parent_id,deleted=0)

def delete_category(category_id):
	try:
		category = Categories.objects.get(id=category_id)
		sub_categories_count = Categories.objects.filter(parent__id=category.id).count()
		if sub_categories_count > 0:
			delete_sub_category(cat.id)
		category.deleted = 1
		category.save()
		return True
	except Exception as e:
		return False

def delete_sub_category(parent_id):
	try:
		sub_categories = Categories.objects.get(parent__id=parent_id)
		for cat in sub_categories:
			has_sub_cat = Categories.objects.filter(parent__id=cat.id).count()
			if has_sub_cat > 0:
				delete_sub_category(cat.id)

		sub_categories.deleted = 1
		sub_categories.save()

	except Exception as e:
		pass

def update_order(data):
	cid = data['id']
	order = data['order']
	parent = data['parent']
	try:
		category = Categories.objects.get(id=cid)
		category.order = order

		try:
			category.parent = Categories.objects.get(id=parent)
		except:
			category.parent = None
		
		category.save()
	except:
		pass

def get_next_order(parent_id):	
	try:
		max_order = Categories.objects.filter(parent__id=parent_id).aggregate(Max('order'))['order__max']
		cat = Categories.objects.get(order=max_order, parent__id=parent_id)
		order = int(cat.order)
		if order <= 0:
			order = 1
		else:
			order = order + 1
	except:
		order = 1

	return order

def generate_admin_dropdown_category():	
	categories = get_sub_categories(None)
	tags = """
		<li><a href="#" rel="" class="cat">--- Parent ----</a></li>
	"""
	for cat in categories:
		subcats = get_sub_categories(cat.id)

		cls = ''
		if subcats.count() > 0:
			cls = 'class="sub-menu"'

		tags += '''
			<li %s><a href="#" rel="%s" class="cat"><span>%s</span></a>
		''' % (cls, cat.id, cat.name)

		if subcats.count() > 0:
			tags += generate_admin_dropdown_sub_category(cat.id)
		tags += "</li>"

	return mark_safe(tags)

def generate_admin_dropdown_sub_category(parent_id):
	cats = get_sub_categories(parent_id)
	tags = '<ul class="dropdown-submenu">'
	for cat in cats:
		subcats = get_sub_categories(cat.id)

		tags += '''
			<li><a href="#" rel="%s" class="cat"> - <span>%s</span></a>
		''' % (cat.id, cat.name)

		if subcats.count() > 0:
			tags += generate_admin_dropdown_sub_category(cat.id)

		tags += '</li>'
	tags += '</ul>'
	return tags