import os
import Image as pil
from common.services import tinyurl
from cStringIO import StringIO
from PIL import ImageOps
from django.conf import settings
from cart.services import generate_unique_id
from django.utils.translation import ugettext_lazy as _
from admin.models import HomeBanners, HomeBannerImages, HomeInfoGrapics
from django.db import DatabaseError, transaction
from django.template.defaultfilters import filesizeformat
from embellishments.models import StyleboardTemplateItems
from customer.models import CustomerStyleBoard, KeepImages
from plata.shop.models import Order
from django.db.models import Q

def getExtensionAndFileName(filename):

	filename, extension = os.path.splitext(filename)

	return (filename, extension)

def home_banner(f, width, height, force=True):
	max_width = width
	max_height = height
	# path = default_storage.save('tmp/somename.mp3', ContentFile(data.read()))

	splittedName = getExtensionAndFileName(f.name)
	newFileName = "%s%s" % (generate_unique_id(),splittedName[1])
	temp_path = "%s%s%s" % (settings.MEDIA_ROOT, "banners/temp/", newFileName)
	if save_destination(f,temp_path):
		img = pil.open(temp_path)
		if not force:
			img.thumbnail((max_width, max_height), pil.ANTIALIAS)		
		else:
			img = ImageOps.fit(img, (max_width, max_height), method=pil.ANTIALIAS)
		newFileName = '%s%s' % ('temp_',newFileName)
		new_path = "%s%s%s" % (settings.MEDIA_ROOT, "banners/", newFileName)
		try:
			os.unlink(temp_path)
		except:
			pass
		img.save(new_path)		
		return newFileName
	else:
		return False

def save_destination(f,path):
	destination = open(path, 'wb+')
	for chunk in f.chunks():
		destination.write(chunk)
	return True

def get_home_banners():
	return HomeBanners.objects.filter(is_active=1,is_deleted=0).order_by('-id')

def get_home_banner(id):
	try:
		return HomeBanners.objects.get(id=id)
	except:
		return False

def get_home_banner_images(home_banner_id):
	return HomeBannerImages.objects.filter(home_banner__id=home_banner_id)

def validate_banner(image=None):
	res = {}
	res['error'] = False
	res['msg'] = ''
	if image:
		splitted_content_type = image.content_type.split('/')
		content_type = splitted_content_type[0]
		file_type = splitted_content_type[1]
		if content_type in settings.CONTENT_TYPES:
			if int(image._size) > int(settings.MAX_BANNER_SIZE):
				res['error'] = True
				max_size = filesizeformat(settings.MAX_BANNER_SIZE)
				image_size = filesizeformat(image._size)
				msg = _('Please keep filesize under %s. Current filesize %s') % (max_size, image_size)
				res['msg'] = msg.encode('utf-8')
		else:
			res['error'] = True
			res['msg'] = _('File type is not supported').encode('utf-8')
	else:
		res['error'] = True
		res['msg'] = _('Thumbnail is required.').encode('utf-8')

	return res

def save_home_banner(data):
	try:
		size 				= data.get('size')
		form_data 			= data.get('form_data')
		home_banner 		= HomeBanners()
		home_banner.size 	= size
		home_banner.save()

		for form in form_data:
			
			save_data 		= form.cleaned_data
			hbi 			= HomeBannerImages()
			hbi.home_banner = home_banner
			hbi.image 		= rename_image_banner(save_data.get('image'))
			hbi.link 		= save_data.get('link')
			hbi.name 		= save_data.get('name')
			hbi.description = save_data.get('description')
			hbi.tinyUrl 	= tinyurl(save_data.get('link'))
			hbi.save()

		return True

	except Exception as e:
		print e
		return False

def update_home_banner(data):

	try:

		for form in data:
			
			save_data 		= form.cleaned_data
			hbi 			= HomeBannerImages.objects.get(id=int(save_data.get('image_id')))
			hbi.image 		= rename_image_banner(save_data.get('image'))
			hbi.link 		= save_data.get('link')
			hbi.name 		= save_data.get('name')
			hbi.description = save_data.get('description')
			hbi.tinyUrl 	= tinyurl(save_data.get('link'))
			hbi.save()

		return True

	except Exception as e:
		print e
		return False
		
def delete_homebanner(home_banner_id):

	deleted = False

	home_banner = HomeBanners.objects.get(id=home_banner_id)

	home_banner_images = HomeBannerImages.objects.filter(home_banner__id=home_banner_id)

	q = None

	for home_banner_image in home_banner_images :

		if q is not None:
			q.add(Q(image=home_banner_image.id), Q.OR)
		else:
			q = Q(image=home_banner_image.id)

	kept_images = KeepImages.objects.filter(q)

	try:

		delete_home_banner_images(home_banner)
		kept_images.delete()
		home_banner_images.delete()
		home_banner.delete()

		deleted = True

	except Exception as e:
		print "The error when deleting image is: %s" % str(e)

	return deleted


def delete_home_banner_images(home_banner):
	images = HomeBannerImages.objects.filter(home_banner=home_banner)

	for image in images:
		path = "%s%s%s" % (settings.MEDIA_ROOT, "banners/", image.image)
		os.unlink(path)
		thumb_path = "%s%s%s" % (settings.MEDIA_ROOT, "banners/thumb/", image.image)
		os.unlink(thumb_path)

def rename_image_banner(img):
	if img.find('temp')!=-1:
		path = "%s%s%s" % (settings.MEDIA_ROOT, "banners/", img)
		img = img.split('_')
		new_path = "%s%s%s" % (settings.MEDIA_ROOT, "banners/", img[1])
		os.rename(path,new_path)
		generate_banner_thumb(img[1])
		# img = pil.open(path)
		# img.save(new_path)
		# os.unlink(path)
		return img[1]
	else:
		return img

def generate_banner_thumb(img):
	path = "%s%s%s" % (settings.MEDIA_ROOT, "banners/", img)
	im = pil.open(path)
	size = (100,100)
	im.thumbnail(size, pil.ANTIALIAS)
	background = pil.new('RGBA', size, (255, 255, 255, 0))
	background.paste(im,((size[0] - im.size[0]) / 2, (size[1] - im.size[1]) / 2))
	thumb_path = "%s%s%s" % (settings.MEDIA_ROOT, "banners/thumb/", img)
	background.save(thumb_path)

def is_kept(home_banner_id):
	
	kept = False

	home_banner_images = HomeBannerImages.objects.filter(home_banner__id=home_banner_id)

	q = None

	for home_banner_image in home_banner_images :

		if q is not None:
			q.add(Q(image=home_banner_image.id), Q.OR)
		else:
			q = Q(image=home_banner_image.id)

	kept_images = KeepImages.objects.filter(q)

	if kept_images.count() > 0 :

		kept = True

	return kept
	

def save_template(data):

	try:

		sti = StyleboardTemplateItems.objects.get(id=int(data['template_id']))

	except:

		sti = StyleboardTemplateItems()

	try:

		sti.name 		= data['name']
		sti.description = data['description']
		sti.item 		= data['item']
		sti.browser 	= data['browser']
		sti.save()

		return True

	except Exception as e:
		
		return False

def getTemplateItems(id=None):
	return StyleboardTemplateItems.objects.filter(deleted=0) if id == None else StyleboardTemplateItems.objects.get(id=id)

def save_Infographics(data):
	try:
		set_InactiveHomeInfographics()
		hig = HomeInfoGrapics()
		hig.is_active = True
		hig.image = rename_image_infographics(data['image'])
		hig.save()
		return True
	except Exception as e:
		return False

def rename_image_infographics(img):
	if img.find('temp')!=-1:
		path = "%s%s%s" % (settings.MEDIA_ROOT, "infographics/", img)
		img = img.split('_')
		new_path = "%s%s%s" % (settings.MEDIA_ROOT, "infographics/", img[1])
		os.rename(path,new_path)
		generate_infographics_thumb(img[1])
		return img[1]
	else:
		return img

def generate_infographics_thumb(img):
	path = "%s%s%s" % (settings.MEDIA_ROOT, "infographics/", img)
	im = pil.open(path)
	size = (100,100)
	im.thumbnail(size, pil.ANTIALIAS)
	background = pil.new('RGBA', size, (255, 255, 255, 0))
	background.paste(im,((size[0] - im.size[0]) / 2, (size[1] - im.size[1]) / 2))
	thumb_path = "%s%s%s" % (settings.MEDIA_ROOT, "infographics/thumb/", img)
	background.save(thumb_path)

def manage_infographic(f, width, height, force=True):
	max_width = width
	max_height = height

	splittedName = getExtensionAndFileName(f.name)
	newFileName = "%s%s" % (generate_unique_id(),splittedName[1])
	temp_path = "%s%s%s" % (settings.MEDIA_ROOT, "infographics/temp/", newFileName)
	if save_destination(f,temp_path):
		img = pil.open(temp_path)
		if not force:
			img.thumbnail((max_width, max_height), pil.ANTIALIAS)		
		else:
			img = ImageOps.fit(img, (max_width, max_height), method=pil.BICUBIC)
		newFileName = '%s%s' % ('temp_',newFileName)
		new_path = "%s%s%s" % (settings.MEDIA_ROOT, "infographics/", newFileName)
		try:
			os.unlink(temp_path)
		except:
			pass
		img.save(new_path)		
		return newFileName
	else:
		return False

def set_HomeInfographicStatus(id):
	try:
		set_InactiveHomeInfographics()
		hig = HomeInfoGrapics.objects.get(id=id)
		hig.is_active = True
		hig.save()
		return True
	except:
		return False

def set_InactiveHomeInfographics():
	infographics = HomeInfoGrapics.objects.all()
	for info in infographics:
		info.is_active = False
		info.save()

def validate_Infographic(image=None):
	res = {}
	res['error'] = False
	res['msg'] = ''
	if image:
		splitted_content_type = image.content_type.split('/')
		content_type = splitted_content_type[0]
		file_type = splitted_content_type[1]
		if content_type in settings.CONTENT_TYPES:
			if int(image._size) > int(settings.HOME_INFO_GRAPHICS_SIZE):
				res['error'] = True
				max_size = filesizeformat(settings.HOME_INFO_GRAPHICS_SIZE)
				image_size = filesizeformat(image._size)
				msg = _('Please keep filesize under %s. Current filesize %s') % (max_size, image_size)
				res['msg'] = msg.encode('utf-8')
		else:
			res['error'] = True
			res['msg'] = _('File type is not supported').encode('utf-8')
	else:
		res['error'] = True
		res['msg'] = _('Thumbnail is required.').encode('utf-8')

	return res


def get_HomeInfographics():
	return HomeInfoGrapics.objects.filter(is_deleted=0)

def get_all_styleboards(filters=None,order_by='created'):

	return CustomerStyleBoard.objects.filter().order_by(order_by) if filters is None else CustomerStyleBoard.objects.filter(filters).order_by(order_by)

def get_all_orders(filters=None,order_by='created'):

	query = Order.objects.filter(~Q(user__id=None)).filter(status__gt=20).order_by(order_by) if filters is None else Order.objects.filter(~Q(user__id=None)).filter(status__gt=20).filter(filters).order_by(order_by)

	return query

def get_all_templates(filters=None,order_by='created'):

	query = StyleboardTemplateItems.objects.filter().filter(deleted=0).order_by(order_by) if filters is None else StyleboardTemplateItems.objects.filter(filters).filter(deleted=0).order_by(order_by)

	return query