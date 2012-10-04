import os
from django.db.models import Max
from models import Categories, CategoryThumbnail, CategoryThumbnailTemp
from django.utils.safestring import mark_safe
from PIL import Image
import magic
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
import time

def new_category(data):
	category_name = data['name']

	try:
		category = Categories()
		category.order = get_next_order(data['parent'])

		try:
			cat = Categories.objects.get(id=data['parent'])
			category.parent = cat
		except:
			pass

		category.name = category_name		
		category.save()

		set_category_thumbnail(category,data['thumbnail'])
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

def is_parent_change(cat_parent,parent_id):
	cat_parent = 0 if not cat_parent else cat_parent
	parent = 0 if not parent_id else parent_id
	is_change = False
	if int(cat_parent) != int(parent):
		is_change = True

	return is_change

def category_edit(data):
	try:
		category = Categories.objects.get(id=data['id'])
		try:
			cat_parent = category.parent.id
		except:
			cat_parent = None
		try:
			cat = Categories.objects.get(id=data['parent'])
			category.parent = cat
			if is_parent_change(cat_parent, data['parent']):
				category.order = get_next_order(data['parent'])
		except:
			category.parent = None
			if is_parent_change(cat_parent,None):
				category.order = get_next_order(None)

		category.name = data['name']
		category.save()

		set_category_thumbnail(category, data['thumbnail'])

		return True
	except Exception as e:
		print e
		return False

def set_category_thumbnail(category, thumbnail):
	if thumbnail.find('temp')!=-1:
		try:	
			cat_thumb = CategoryThumbnail.objects.get(category__id=category.id)
		except:
			cat_thumb = CategoryThumbnail()
			cat_thumb.category = category

		spl = thumbnail.split('|')
		temp_id = spl[1]
		cat_temp = CategoryThumbnailTemp.objects.get(id=temp_id)

		thumb = cat_temp.thumbnail.path

		t = time.time()
		t = str(t)
		fn = t.replace('.','_')
		fname = '%s.%s' % (fn,'jpeg')

		path = '%scategories/thumbnail/%s' % (settings.MEDIA_ROOT,fname)

		im = Image.open(thumb)

		size = (settings.CATEGORY_THUMBNAIL_WIDTH, settings.CATEGORY_THUMBNAIL_HEIGHT)

		im.thumbnail(size, Image.ANTIALIAS)

		if im.mode != 'RGB':
			im = im.convert("RGB")

		im.save(path)

		cat_thumb.thumbnail = 'categories/thumbnail/%s' % fname
		cat_thumb.save()
		clear_temp(temp_id)

def manage_category_thumbnail(data):
	try:
		cat_thumb = CategoryThumbnailTemp.objects.get(id=data['id'])
	except:
		cat_thumb = CategoryThumbnailTemp()

	cat_thumb.thumbnail = data['thumbnail']
	cat_thumb.save()
	return cat_thumb

def clear_temp(temp_id):
	try:
		cat_temp = CategoryThumbnailTemp.objects.get(id=temp_id)
		os.unlink(cat_temp.thumbnail.path)
		cat_temp.delete()
	except:
		pass

def category_thumbnails(**kwargs):
	ctid = kwargs.get('ctid',None)
	cid = kwargs.get('cid',None)
	try:
		if ctid:
			cat_thumb = CategoryThumbnail.objects.get(id=ctid)

		if cid:
			cat_thumb = CategoryThumbnail.objects.get(category__id=cid)
	except:
		cat_thumb = None

	return cat_thumb

def convert_to_jpeg(thumb):	
	try:
		s = thumb.split('/')
		l = len(s)
		fn = s[l-1].split('.')
		nfn = fn[0]

		path = '%s%s.%s' % (settings.MEDIA_ROOT,nfn,'jpeg')

		im = Image.open(thumb)

		size = (settings.CATEGORY_THUMBNAIL_WIDTH, settings.CATEGORY_THUMBNAIL_HEIGHT)

		im.thumbnail(size, Image.ANTIALIAS)

		if im.mode != 'RGB':
			im = im.convert("RGB")

		# background = Image.new('RGB', size, (255, 255, 255))
		# im.paste(background, (100,100), background)

		#background.paste(im, (100,100), im)

		im.save(path)

		return path
	except Exception as e:
		return False


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
	categories = get_categories(None)
	tags = """
		<li><a href="#" rel="" class="cat">---- Parent ----</a></li>
	"""
	for cat in categories:
		subcats = get_categories(cat.id)

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
	cats = get_categories(parent_id)
	tags = ''
	for cat in cats:
		subcats = get_categories(cat.id)
		arrow = '&rsaquo;'
		tags += '''
			<li><a href="#" rel="%s" class="cat" id="ddl-cat-%s"> %s <span>%s</span></a>
		''' % (cat.id, cat.id, arrow + level , cat.name)

		if subcats.count() > 0:
			tags += generate_admin_dropdown_sub_category(cat.id, arrow + level)

		tags += '</li>'
	tags += ''
	return tags

def validate_thumbnail(thumbnail=None):
	res = {}
	res['error'] = False
	res['msg'] = ''
	if thumbnail:
		content_type = thumbnail.content_type.split('/')[0]	
		if content_type in settings.CONTENT_TYPES:
			if int(thumbnail._size) > int(settings.MAX_UPLOAD_CATEGORY_IMAGE_SIZE):
				res['error'] = True
				res['msg'] = _('Please keep filesize under %s. Current filesize %s').encode('utf-8') % (filesizeformat(settings.MAX_UPLOAD_CATEGORY_IMAGE_SIZE), filesizeformat(thumbnail._size))
		else:
			res['error'] = True
			res['msg'] = _('File type is not supported').encode('utf-8')
	else:
		res['error'] = True
		res['msg'] = _('Thumbnail is required.').encode('utf-8')

	return res	