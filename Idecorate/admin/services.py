import os
import Image as pil
from cStringIO import StringIO
from PIL import ImageOps
from django.conf import settings
from cart.services import generate_unique_id
from django.utils.translation import ugettext_lazy as _
from admin.models import HomeBanners, HomeBannerImages
from django.db import DatabaseError, transaction

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
		id = data.get('id',None)
		if id:
			hb = HomeBanners.objects.get(id=id)
			delete_home_banner_images(hb)
		else:		
			hb = HomeBanners()

		hb.size = data['sizes']
		hb.save()	
		s = int(data['sizes']) 
		if s==1:
			save_home_banner_image(data['image11'],data['wholelink'],hb)
		elif s==2:
			save_home_banner_image(data['image21'],data['half1link'],hb)
			save_home_banner_image(data['image22'],data['half2link'],hb)
		else:
			save_home_banner_image(data['image31'],data['third1link'],hb)
			save_home_banner_image(data['image32'],data['third2link'],hb)
			save_home_banner_image(data['image33'],data['third3link'],hb)

		return True
	except Exception as e:
		print e
		return False

def save_edit_home_banner(data):
	id = data['id']
	hb = HomeBanners.objects.get(id=id)
	hb.size = data['sizes']
	s = int(data['sizes'])
	delete_home_banner_images(hb)
	if s==1:
		save_home_banner_image(data['image11'],data['wholelink'],hb)
	elif s==2:
		save_home_banner_image(data['image21'],data['half1link'],hb)
		save_home_banner_image(data['image22'],data['half2link'],hb)
	else:
		save_home_banner_image(data['image31'],data['third1link'],hb)
		save_home_banner_image(data['image32'],data['third2link'],hb)
		save_home_banner_image(data['image33'],data['third3link'],hb)

def delete_home_banner_images(home_banner):
	images = HomeBannerImages.objects.filter(home_banner=home_banner)
	for image in images:
		path = "%s%s%s" % (settings.MEDIA_ROOT, "banners/", image.image)
		image.delete()

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

def save_home_banner_image(img,link,home_banner):	
	hbi = HomeBannerImages()
	hbi.home_banner = home_banner
	hbi.image = rename_image_banner(img)
	hbi.link = link
	hbi.save()	

def validate_home_banner_form(data):
	s = int(data['sizes']) 
	validation = {}
	error = False
	if s==1:
		if(len(data['image11'])==0):
			error = True
			validation['image11'] = _('Image is a required field.')
		if (len(data['wholelink'])==0):
			error = True
			validation['link'] = _('Link is a required field.')			
	elif s==2:
		if(len(data['image21'])==0):
			error = True
			validation['image21'] = _('Image 1 is a required field.')
		if(len(data['image22'])==0):
			error = True
			validation['image22'] = _('Image 2 is a required field.')
		if (len(data['half1link'])==0 or len(data['half2link'])==0):
			error = True
			validation['link'] = _('Link is a required field.')
	else:
		if(len(data['image31'])==0):
			error = True
			validation['image31'] = _('Image 1 is a required field.')
		if(len(data['image32'])==0):
			error = True
			validation['image32'] = _('Image 2 is a required field.')
		if(len(data['image33'])==0):
			error = True
			validation['image33'] = _('Image 3 is a required field.')
		if (len(data['third1link'])==0 or len(data['third2link'])==0 or len(data['third3link'])==0):
			error = True
			validation['link'] = _('Link is a required field.')

	if not error:
		validation = False
	return validation

def get_home_banners():
	return HomeBanners.objects.filter(is_active=1,is_deleted=0).order_by('-id')

def get_home_banner(id):
	try:
		return HomeBanners.objects.get(id=id)
	except:
		return False

def get_home_banner_images(home_banner_id):
	return HomeBannerImages.objects.filter(home_banner__id=home_banner_id)