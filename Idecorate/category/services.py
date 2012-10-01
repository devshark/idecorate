import os
from django.db.models import Max
from category.models import Categories
from django.utils.safestring import mark_safe
from PIL import Image
import magic
from django.conf import settings

def new_category(data):
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
		convert_to_jpeg(category.id)
		return True
	except Exception as e:
		return False

def parent_is_my_sub(cat_id,parent_id):
	is_sub = False
	try:
		categories = Categories.objects.filter(parent__id=cat_id)
		if categories.count() > 0:
			for cat in categories:
				subcats = Categories.objects.filter(parent__id=cat.id)

				if subcats.count() > 0:
					is_sub = parent_is_my_sub(cat.id, parent_id)
				if int(cat.id) == int(parent_id):
					is_sub = True
					break
	except:
		pass
	return is_sub

def category_edit(data):
	try:
		category = Categories.objects.get(id=data['id'])
		try:
			cat = Categories.objects.get(id=data['parent'])
			category.parent = cat
			category.order = get_next_order(data['parent'])
		except:
			category.parent = None
			category.order = get_next_order(None)

		if data['thumbnail']:
			category.thumbnail = data['thumbnail']
		category.name = data['name']
		category.save()
		convert_to_jpeg(category.id)
		return True
	except Exception as e:
		print e
		return False

def convert_to_jpeg(cat_id):	
	try:
		cat = Categories.objects.get(id=cat_id)
		thumb = cat.thumbnail.path
		s = thumb.split('/')
		l = len(s)
		fn = s[l-1].split('.')
		nfn = fn[0]

		path = '%s%s.%s' % (settings.MEDIA_ROOT,nfn,'jpeg')

		im = Image.open(cat.thumbnail.path)

		size = (settings.CATEGORY_THUMBNAIL_WIDTH, settings.CATEGORY_THUMBNAIL_HEIGHT)

		im.thumbnail(size, Image.ANTIALIAS)

		if im.mode != 'RGB':
			im = im.convert("RGB")
		im.save(path)
		cat.thumbnail = path
		cat.save()

		if fn[1] != 'jpeg' and fn[1] != 'jpg':
			os.unlink(thumb)

	except Exception as e:
		print 'Exception : %s' % e


def get_categories(parent_id):
	return Categories.objects.filter(parent__id=parent_id,deleted=0)

def delete_category(category_id):
	try:
		category = Categories.objects.get(id=category_id)
		sub_categories_count = Categories.objects.filter(parent__id=category.id).count()
		if sub_categories_count > 0:
			delete_sub_category(category.id)
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
	parent = None
	if parent_id:
		parent = parent_id

	cat = Categories.objects.filter(parent__id=parent)
	order = 1
	if cat.count() > 0:
		max_order = cat.aggregate(Max('order'))['order__max']
		if max_order:
			order = max_order + 1

	return int(order)

def generate_admin_dropdown_category():	
	categories = get_sub_categories(None)
	tags = """
		<li><a href="#" rel="" class="cat">---- Parent ----</a></li>
	"""
	for cat in categories:
		subcats = get_sub_categories(cat.id)

		cls = ''
		if subcats.count() > 0:
			cls = 'class="sub-menu"'

		tags += '''
			<li %s><a href="#" rel="%s" class="cat" id="ddl-cat-%s"><span>%s</span></a>
		''' % (cls, cat.id, cat.id, cat.name)

		if subcats.count() > 0:
			tags += generate_admin_dropdown_sub_category(cat.id)
		tags += "</li>"

	return mark_safe(tags)

def generate_admin_dropdown_sub_category(parent_id, level=''):
	cats = get_sub_categories(parent_id)
	tags = ''
	for cat in cats:
		subcats = get_sub_categories(cat.id)
		arrow = '&rsaquo;'
		tags += '''
			<li><a href="#" rel="%s" class="cat" id="ddl-cat-%s"> %s <span>%s</span></a>
		''' % (cat.id, cat.id, arrow + level , cat.name)

		if subcats.count() > 0:
			tags += generate_admin_dropdown_sub_category(cat.id, arrow + level)

		tags += '</li>'
	tags += ''
	return tags