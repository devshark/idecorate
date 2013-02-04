from django.contrib.auth.decorators import login_required
from django.shortcuts import HttpResponse, redirect, render_to_response
from django.contrib.auth import authenticate, login, logout
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.template import RequestContext
from django.utils import simplejson
from django.http import HttpResponseNotFound
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.safestring import mark_safe
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance
from models import StyleboardItems, CustomerProfile
from django.contrib.auth.models import User

from forms import LoginForm, SignupForm, SaveStyleboardForm, EditProfileForm, PassForm
from services import register_user, customer_profile, get_client_ip, get_user_styleboard, save_styleboard_item,\
	get_customer_styleboard_item, manage_styleboard_cart_items, get_styleboard_cart_item
from admin.models import LoginLog, TextFonts, Embellishments, EmbellishmentsType
from django.conf import settings
import re
import math
from idecorate_settings.models import IdecorateSettings
from urllib import unquote
from admin.services import getExtensionAndFileName
from cart.services import generate_unique_id
from embellishments.models import StyleboardTemplateItems
from django.utils.html import strip_tags
from cart.models import Contact
from social_auth.models import UserSocialAuth
from django.template.defaultfilters import filesizeformat
import shutil
from cart.views import shop

def login_signup(request):

	info = {}
	login_form = LoginForm()
	signup_form = SignupForm()
	info['action'] = 'login_signup'
	if request.method=="POST":
		action = request.POST['btnSubmit']
		if action=='Login':			
			login_form = LoginForm(request.POST)
			ip = get_client_ip(request)
			loginLog = LoginLog.objects.filter(created__gte=(datetime.now() - timedelta(minutes=5)), ip_address=ip)
			if loginLog.count() >= 5:
				messages.error(request, _('You have failed to login 5 consecutive times. Please try to login after 5 minutes'))
				return redirect('login_signup')

			if login_form.is_valid():
				user = authenticate(username=login_form.cleaned_data['username'], password=login_form.cleaned_data['password'])
				if user is not None:
					if user.is_active:
						login(request, user)
						profile = customer_profile(user)
						info['username'] = profile['nickname']
						#Successfull login, delete all the log attempts
						LoginLog.objects.filter(ip_address=ip).delete()

						personalize_styleboard = request.session.get('personalize_styleboard',None)
						if personalize_styleboard:
							if personalize_styleboard.user.id == user.id:
								request.session['customer_styleboard'] = personalize_styleboard
								del request.session['personalize_styleboard']

						customer_styleboard = request.session.get('customer_styleboard',None)
						if customer_styleboard:
							if customer_styleboard.user.id != request.user.id:
								del request.session['customer_styleboard']
						
						return render_to_response('customer/iframe/success.html', info)
					else:
						messages.warning(request, _('Sorry we could not verify your e-mail address and password.'))
				else:
					loginLog = LoginLog()
					loginLog.created = datetime.now()
					loginLog.ip_address = ip
					loginLog.save()
					messages.warning(request, _('Sorry we could not verify your e-mail address and password.'))
		else:
			signup_form = SignupForm(request.POST)
			if signup_form.is_valid():
				user = register_user(signup_form.cleaned_data)
				if user:
					user = authenticate(username=signup_form.cleaned_data['username'], password=signup_form.cleaned_data['password'])
					login(request, user)
					profile = customer_profile(user)
					info['username'] = profile['nickname']
					personalize_styleboard = request.session.get('personalize_styleboard',None)
					if personalize_styleboard:
						if personalize_styleboard.user.id == user.id:
							request.session['customer_styleboard'] = save_styleboard
							del request.session['personalize_styleboard']
					customer_styleboard = request.session.get('customer_styleboard',None)
					if customer_styleboard:
						if customer_styleboard.user.id != request.user.id:
							del request.session['customer_styleboard']
					return render_to_response('customer/iframe/success.html', info)
				else:
					messages.warning(request, _('Sorry you could not register at the moment. Please try again later.'))

	info['login_form'] = login_form
	info['signup_form'] = signup_form
	return render_to_response('customer/iframe/login_signup.html', info, RequestContext(request))

def customer_logout(request):
	if request.user.is_authenticated():
		logout(request)
	if request.is_ajax():
		return HttpResponse('ok')
	else:
		return redirect('home')

def forgot_password(request):
	return HttpResponse('<h1>Under Construction.</h1>')

def profile(request):

	user_id = request.GET.get('id',None)
	if user_id:
		try:
			user = User.objects.get(id=user_id)
		except:
			if request.user.is_authenticated():
				user = request.user
			else:
				return redirect('home')
	else:
		if request.user.is_authenticated():
			user = request.user
		else:
			return redirect('home')
	info = {}
	user_profile = customer_profile(user)
	info['user_profile'] = user_profile
	info['currentUrl'] = request.get_full_path()
	user_styleboard = get_user_styleboard(user)	
	info['user_styleboard'] = user_styleboard

	idecorateSettings = IdecorateSettings.objects.get(pk=1)
	info['global_default_quantity'] = idecorateSettings.global_default_quantity
	info['global_guest_table'] = idecorateSettings.global_table

	return render_to_response('customer/profile.html', info, RequestContext(request))

def edit_profile(request):
	if not request.user.is_authenticated():
		return redirect('home')
	
	info = {}

	u = User.objects.get(id=request.user.id)

	try:
		u_prof = CustomerProfile.objects.get(user=u)
	except:
		u_prof = CustomerProfile()
		u_prof.nickname = u.email
		u_prof.user = u
		u_prof.save()

	try:
		u_contact = Contact.objects.get(user=u)
	except:
		u_contact = Contact()
		u_contact.user = u
		u_contact.currency = "USD"
		u_contact.save()
		#shop.contact_model(user=u)

	try:
		user_twitter = UserSocialAuth.objects.get(user=u, provider='twitter')
	except:
		user_twitter = None

	try:
		user_facebook = UserSocialAuth.objects.get(user=u, provider='facebook')
	except:
		user_facebook = None

	initial_form_data = {
		'firstname': u.first_name,
		'lastname': u.last_name,
		'salutation': u_contact.billing_salutation,
		'user_image': u_prof.picture,
		'about': u_prof.description,
		'username': u.username,
		'gender': u_prof.gender,
		'language': u_prof.language,
		'shipping_same_as_billing': u_contact.shipping_same_as_billing,
		'shipping_address': u_contact.address,
		'shipping_address2': u_contact.shipping_address2,
		'shipping_state':u_contact.shipping_state,
		'shipping_city': u_contact.city,
		'shipping_country': u_contact.countries,
		'shipping_zip_code':u_contact.zip_code,
		'billing_address': u_contact.address2,
		'billing_address2': u_contact.billing_address2,
		'billing_state':u_contact.billing_state,
		'billing_city': u_contact.city2,
		'billing_country': u_contact.countries2,
		'billing_zip_code':u_contact.zip_code2,
	}

	form = EditProfileForm(this_user=u, initial=initial_form_data, request=request)

	pass_form = PassForm()

	if request.method == "POST":

		task = request.POST.get('task','1')

		if int(task) == 1:
			initial_form_data = {}
			form = EditProfileForm(request.POST,this_user=u, request=request)

			if form.is_valid():
				c_data = form.cleaned_data
				u.first_name = c_data['firstname']
				u.last_name = c_data['lastname']
				u.save()

				u_prof.description = c_data['about']
				u_prof.gender = c_data['gender']
				u_prof.language = c_data['language']

				if c_data['user_image'] != u_prof.picture:
					if re.search('^http', c_data['user_image']):
						u_prof.picture = c_data['user_image']
					else:
						shutil.move("%s%s" % (settings.MEDIA_ROOT, "profiles/temp/%s" % c_data['user_image']), "%s%s" % (settings.MEDIA_ROOT, "profiles/%s" % c_data['user_image']))
						u_prof.picture = "/media/profiles/%s" % c_data['user_image']

				u_prof.save()

				u_contact.billing_salutation = c_data['salutation']
				u_contact.shipping_same_as_billing = c_data['shipping_same_as_billing']
				u_contact.address = c_data['shipping_address']
				u_contact.shipping_address2 = c_data['shipping_address2']
				u_contact.shipping_state = c_data['shipping_state']
				u_contact.city = c_data['shipping_city']
				u_contact.countries = c_data['shipping_country']
				u_contact.zip_code = c_data['shipping_zip_code']
				u_contact.address2 = c_data['billing_address']
				u_contact.billing_address2 = c_data['billing_address2']
				u_contact.billing_state = c_data['billing_state']
				u_contact.city2 = c_data['billing_city']
				u_contact.countries2 = c_data['billing_country']
				u_contact.zip_code2 = c_data['billing_zip_code']
				u_contact.save()

				messages.success(request, _('Profile saved.'))
				return redirect('edit_profile')
		else:
			pass_form = PassForm(request.POST)

			if pass_form.is_valid():
				u.set_password(pass_form.cleaned_data['password'])
				u.save()

				messages.success(request, _('Password changed.'))
				return redirect('edit_profile')

	info['idecorate_user'] = u
	info['idecorate_profile'] = u_prof
	info['idecorate_contact'] = u_contact
	info['user_twitter'] = user_twitter
	info['user_facebook'] = user_facebook
	info['form'] = form
	info['pass_form'] = pass_form
	info['initial_form_data'] = initial_form_data

	return render_to_response('customer/edit_profile.html', info, RequestContext(request))

@csrf_exempt
def customer_upload_image(request):

	if request.method == "POST":

		uploaded = request.FILES['image']
		content_type = uploaded.content_type.split('/')[0]

		if content_type in settings.CONTENT_TYPES:
			if int(uploaded.size) > int(settings.MAX_UPLOAD_PROFILE_PIC):
				return HttpResponse(_('notok:Please keep filesize under %s. Current filesize %s').encode('utf-8') % (filesizeformat(settings.MAX_UPLOAD_PROFILE_PIC), filesizeformat(uploaded.size)))
			else:
				splittedName = getExtensionAndFileName(uploaded.name)
				newFileName = "%s-%s%s" % (splittedName[0],datetime.now().strftime('%b-%d-%I%M%s%p-%G'),splittedName[1])

				destination = open("%s%s%s" % (settings.MEDIA_ROOT, "profiles/temp/", newFileName), 'wb+')
				for chunk in uploaded.chunks():
					destination.write(chunk)

				destination.close()

				return HttpResponse('ok:%s' % newFileName)
		else:
			return HttpResponse(_('notok:File type is not supported').encode('utf-8'))

def save_styleboard(request):
	if not request.user.is_authenticated():
		return redirect('styleboard')
	info = {}	
	customer_styleboard = request.session.get('customer_styleboard',None)
	if not customer_styleboard:
		sbid = request.GET.get('sbid',None)
		if sbid:
			personalize_styleboard = get_user_styleboard(None, sbid)
			if personalize_styleboard:
				if personalize_styleboard.user.id:				
					if int(personalize_styleboard.user.id) == int(request.user.id):
						customer_styleboard = personalize_styleboard

	if customer_styleboard:
		form = SaveStyleboardForm(initial={'name':customer_styleboard.styleboard_item.name,'description':customer_styleboard.styleboard_item.description})
	else:
		form = SaveStyleboardForm()
	if request.method == "POST":
		form = SaveStyleboardForm(request.POST)		
		if form.is_valid():
			cleaned_datas = form.cleaned_data
			cleaned_datas['user'] = request.user
			cleaned_datas['customer_styleboard'] = customer_styleboard
			cleaned_datas['sessionid'] = request.session.get('cartsession',generate_unique_id())
			cleaned_datas['description'] = strip_tags(cleaned_datas['description'])
			cleaned_datas['session_in_request'] = request.session		
			res = save_styleboard_item(cleaned_datas)
			request.session['customer_styleboard'] = res
			info['action'] = 'save_styleboard'
			info['msg'] =  _('Style board saved.')
			return render_to_response('customer/iframe/success.html', info)
	info['form'] = form
	return render_to_response('customer/iframe/save_styleboard.html', info, RequestContext(request))

def styleboard_view(request,sid=None):
	if not sid:
		return redirect('home')
	info = {}
	styleboard = get_user_styleboard(None, sid)
	if not styleboard:
		return redirect('home')

	"""
	manage add to cart
	"""
	if request.method=="POST":
		styleboard_item_id = request.POST['sid']
		styleboard = get_user_styleboard(None,styleboard_item_id)
		cart_items = get_styleboard_cart_item(styleboard)

	user_profile = customer_profile(styleboard.user)
	info['user_profile'] = user_profile
	info['styleboard'] = get_user_styleboard(None, sid)
	info['cart_items'] = get_styleboard_cart_item(styleboard.styleboard_item)
	return render_to_response('customer/styleboard_view.html', info, RequestContext(request))


def generate_styleboard_view(request, id, w, h):
	
	styleboardItem = StyleboardItems.objects.get(id=id)
	itemString = str(styleboardItem.item).replace(',null','')
	itemList = []
	
	imageWidth = int(w)
	imageHeight = int(h)

	lowestTop = None
	highestTop = None
	lowestLeft = None
	highestLeft = None

	finalHeight = 0
	finalWidth = 0
	widthIndex = 0
	heightIndex = 0
	true = True
	false = False

	exec('itemList=%s' % itemString)

	for iList in itemList:

		try:
			if re.search('/media/products/',iList['img'][0]['src']):

				imgFile = iList['img'][0]['src'].split('/')
				imgFile = imgFile[len(imgFile) - 1].split('?')[0]
				imgFile = "%s%s%s" % (settings.MEDIA_ROOT, 'products/', unquote(imgFile))

			elif re.search('/generate_embellishment/', iList['img'][0]['src']):
				eProperties = iList['img'][0]['src'].split("?")[1].split('&')

				directory = ""

				embObj = Embellishments.objects.get(id=int(eProperties[0].split('=')[1]))

				if embObj.e_type.id == 1:
					directory = "images"
				elif embObj.e_type.id == 2:
					directory = "textures"
				elif embObj.e_type.id == 3:
					directory = "patterns"
				elif embObj.e_type.id == 4:
					directory = "shapes"
				elif embObj.e_type.id == 5:
					directory = "borders"

				imgFile = "%s%s%s" % (settings.MEDIA_ROOT, "embellishments/%s/" % directory, embObj.image)
			elif re.search('/media/embellishments/',iList['img'][0]['src']):

				imgFile = iList['img'][0]['src'].split('/')
				imgFile = imgFile[len(imgFile) - 1]
				imgFile = imgFile.split('?')[0]
				imgFile = "%s%s%s" % (settings.MEDIA_ROOT, 'embellishments/images/', unquote(imgFile))

			elif re.search('/generate_text/',iList['img'][0]['src']):
				eProperties = iList['img'][0]['src'].split("?")[1].split('&')

				fontObj = TextFonts.objects.get(id=int(eProperties[3].split('=')[1]))
				imgFile = "%s%s%s" % (settings.MEDIA_ROOT, "fonts/", fontObj.font)
				font_size = int(eProperties[0].split('=')[1])
				font_color = eProperties[2].split('=')[1]
				font_color = (int(font_color[0:3]), int(font_color[3:6]), int(font_color[6:9]))
				image_text = unquote(eProperties[1].split('=')[1])
			elif re.search('/cropped/',iList['img'][0]['src']):
				eProperties = iList['img'][0]['src'].split("?")[1].split('&')

				imgFile = "%s%s%s" % (settings.MEDIA_ROOT, "products/", unquote(eProperties[3].split('=')[1]))
				task = eProperties[1].split('=')[1]

				splittedPosts = unquote(eProperties[2].split('=')[1]).split(',')
		except KeyError:
			continue

		style = iList['style']
		splittedStyle = style.split(';')

		#find width and height index
		ctr = 0
		for item in splittedStyle:
			if re.search('width', item):
				widthIndex = ctr
			if re.search('height', item):
				heightIndex = ctr
			ctr += 1

		w = int(float(str(splittedStyle[widthIndex].split(':')[1]).strip().replace('px','')))
		h = int(float(str(splittedStyle[heightIndex].split(':')[1]).strip().replace('px','')))

		try:
			if re.search('/generate_text/',iList['img'][0]['src']):

				font = ImageFont.truetype(imgFile, font_size)
				
				image_text = image_text.replace("\r", "")
				splittedTexts = image_text.split("\n")
				totalHeight = 0
				upperWidth = 0
				heightList = [0]

				#compute the final width and height first
				for splittedText in splittedTexts:
					textSize = font.getsize(splittedText)
					totalHeight += textSize[1]
					heightList.append(totalHeight)

					if upperWidth == 0:
						upperWidth = textSize[0]
					else:
						if textSize[0] > upperWidth:
							upperWidth = textSize[0]

				#image with background transparent
				img = Image.new("RGBA", (upperWidth, totalHeight), (255,255,255, 0))
				#create draw object	
				draw = ImageDraw.Draw(img)
				#draw the text
				ctr = 0

				for splittedText in splittedTexts:
					#draw text
					draw.text((0,heightList[ctr]), splittedText, font_color, font=font)
					ctr += 1

				imgObj = img
				#imgObj.thumbnail((w,h),Image.ANTIALIAS)
				imgObj = imgObj.resize((w,h), Image.ANTIALIAS)
				imgObj = imgObj.rotate(float(iList['angle']), expand=1)
				w, h = imgObj.size
			elif re.search('/cropped/',iList['img'][0]['src']):

				img = Image.open(imgFile)
				back = Image.new('RGBA', (400,400), (255, 255, 255, 0))
				back.paste(img, ((400 - img.size[0]) / 2, (400 - img.size[1]) /2 ))

				poly = Image.new('RGBA', (settings.PRODUCT_WIDTH,settings.PRODUCT_HEIGHT), (255, 255, 255, 0))
				pdraw = ImageDraw.Draw(poly)

				dimensionList = []

				if task == 'poly':
					for splittedPost in splittedPosts:
						spl = splittedPost.split(':')
						dimensionList.append((float(spl[0]),float(spl[1])))

					pdraw.polygon(dimensionList,fill=(255,255,255,255),outline=(255,255,255,255))

				elif task == 'rect':
					for splittedPost in splittedPosts:
						dimensionList.append(float(splittedPost))
					pdraw.rectangle(dimensionList,fill=(255,255,255,255),outline=(255,255,255,255))


				poly.paste(back,mask=poly)

				newImg = poly.crop(((400 - img.size[0]) / 2, (400 - img.size[1]) /2 , ((400 - img.size[0]) / 2) + img.size[0], ((400 - img.size[1]) / 2) + img.size[1]))
				imgObj = newImg
				imgObj = imgObj.resize((w,h), Image.ANTIALIAS)
				imgObj = imgObj.rotate(float(iList['angle']), expand=1)
				w, h = imgObj.size
			else:
				imgObj = Image.open(imgFile).convert('RGBA')
				#imgObj.thumbnail((w,h),Image.ANTIALIAS)
				imgObj = imgObj.resize((w,h), Image.ANTIALIAS)
				imgObj = imgObj.rotate(float(iList['angle']), expand=1)
				w, h = imgObj.size
		except:
			pass

		if lowestTop is None:
			lowestTop = int(float(iList['top']))
		else:
			if int(float(iList['top'])) < lowestTop:
				lowestTop = int(float(iList['top']))

		if highestTop is None:
			highestTop = int(float(iList['top'])) + h
		else:
			if (int(float(iList['top'])) + h) > highestTop:
				highestTop = int(float(iList['top'])) + h

		if lowestLeft is None:
			lowestLeft = int(float(iList['left']))
		else:
			if int(float(iList['left'])) < lowestLeft:
				lowestLeft = int(float(iList['left']))

		if highestLeft is None:
			highestLeft = int(float(iList['left'])) + w
		else:
			if (int(float(iList['left'])) + w) > highestLeft:
				highestLeft = int(float(iList['left'])) + w

	finalWidth = highestLeft - lowestLeft
	finalHeight = highestTop - lowestTop

	#create main image
	mainImage = Image.new('RGBA', (finalWidth, finalHeight), (255, 255, 255, 0))


	for iList in itemList:

		try:
			if re.search('/media/products/',iList['img'][0]['src']):

				imgFile = iList['img'][0]['src'].split('/')
				imgFile = imgFile[len(imgFile) - 1].split('?')[0]
				imgFile = "%s%s%s" % (settings.MEDIA_ROOT, 'products/', unquote(imgFile))
			elif re.search('/generate_embellishment/', iList['img'][0]['src']):
				eProperties = iList['img'][0]['src'].split("?")[1].split('&')

				directory = ""

				embObj = Embellishments.objects.get(id=int(eProperties[0].split('=')[1]))

				if embObj.e_type.id == 1:
					directory = "images"
				elif embObj.e_type.id == 2:
					directory = "textures"
				elif embObj.e_type.id == 3:
					directory = "patterns"
				elif embObj.e_type.id == 4:
					directory = "shapes"
				elif embObj.e_type.id == 5:
					directory = "borders"

				imgFile = "%s%s%s" % (settings.MEDIA_ROOT, "embellishments/%s/" % directory, embObj.image)
			elif re.search('/media/embellishments/',iList['img'][0]['src']):

				imgFile = iList['img'][0]['src'].split('/')
				imgFile = imgFile[len(imgFile) - 1]
				imgFile = imgFile.split('?')[0]
				imgFile = "%s%s%s" % (settings.MEDIA_ROOT, 'embellishments/images/', unquote(imgFile))

				"""
				if re.search('?', imgFile):
					splRnd = imgFile.split('?')
					imgFile = splRnd[0]
				"""
			elif re.search('/generate_text/',iList['img'][0]['src']):
				eProperties = iList['img'][0]['src'].split("?")[1].split('&')

				fontObj = TextFonts.objects.get(id=int(eProperties[3].split('=')[1]))
				imgFile = "%s%s%s" % (settings.MEDIA_ROOT, "fonts/", fontObj.font)
				font_size = int(eProperties[0].split('=')[1])
				font_color = eProperties[2].split('=')[1]
				font_color = (int(font_color[0:3]), int(font_color[3:6]), int(font_color[6:9]))
				image_text = unquote(eProperties[1].split('=')[1])
				#print "The text is: %s" % image_text
			elif re.search('/cropped/',iList['img'][0]['src']):
				eProperties = iList['img'][0]['src'].split("?")[1].split('&')

				imgFile = "%s%s%s" % (settings.MEDIA_ROOT, "products/", unquote(eProperties[3].split('=')[1]))
				task = eProperties[1].split('=')[1]

				splittedPosts = unquote(eProperties[2].split('=')[1]).split(',')
		except KeyError:
			continue

		style = iList['style']
		splittedStyle = style.split(';')

		#find width and height index
		ctr = 0
		for item in splittedStyle:
			if re.search('width', item):
				widthIndex = ctr
			if re.search('height', item):
				heightIndex = ctr
			ctr += 1

		w = int(float(str(splittedStyle[widthIndex].split(':')[1]).strip().replace('px','')))
		h = int(float(str(splittedStyle[heightIndex].split(':')[1]).strip().replace('px','')))


		if re.search('/generate_text/',iList['img'][0]['src']):

			font = ImageFont.truetype(imgFile, font_size)
			
			image_text = image_text.replace("\r", "")	
			splittedTexts = image_text.split("\n")
			totalHeight = 0
			upperWidth = 0
			heightList = [0]

			#compute the final width and height first
			for splittedText in splittedTexts:
				textSize = font.getsize(splittedText)
				totalHeight += textSize[1]
				heightList.append(totalHeight)

				if upperWidth == 0:
					upperWidth = textSize[0]
				else:
					if textSize[0] > upperWidth:
						upperWidth = textSize[0]

			#image with background transparent
			img = Image.new("RGBA", (upperWidth, totalHeight), (255,255,255, 0))
			#create draw object	
			draw = ImageDraw.Draw(img)
			#draw the text
			ctr = 0

			for splittedText in splittedTexts:
				#draw text
				draw.text((0,heightList[ctr]), splittedText, font_color, font=font)
				ctr += 1

			imgObj = img
		elif re.search('/cropped/',iList['img'][0]['src']):

			img = Image.open(imgFile)
			back = Image.new('RGBA', (400,400), (255, 255, 255, 0))
			back.paste(img, ((400 - img.size[0]) / 2, (400 - img.size[1]) /2 ))

			poly = Image.new('RGBA', (settings.PRODUCT_WIDTH,settings.PRODUCT_HEIGHT), (255, 255, 255, 0))
			pdraw = ImageDraw.Draw(poly)

			dimensionList = []

			if task == 'poly':
				for splittedPost in splittedPosts:
					spl = splittedPost.split(':')
					dimensionList.append((float(spl[0]),float(spl[1])))

				pdraw.polygon(dimensionList,fill=(255,255,255,255),outline=(255,255,255,255))

			elif task == 'rect':
				for splittedPost in splittedPosts:
					dimensionList.append(float(splittedPost))
				pdraw.rectangle(dimensionList,fill=(255,255,255,255),outline=(255,255,255,255))

			poly.paste(back,mask=poly)

			newImg = poly.crop(((400 - img.size[0]) / 2, (400 - img.size[1]) /2 , ((400 - img.size[0]) / 2) + img.size[0], ((400 - img.size[1]) / 2) + img.size[1]))

			"""
			splittedName = getExtensionAndFileName(imgFile)
			if splittedName[1] == '.jpg':
				img2 = Image.open("%s%s" % (settings.MEDIA_ROOT, "products/white_background.png"))
				img2 = img2.resize((newImg.size[0],newImg.size[1]), Image.ANTIALIAS)
				img2 = img2.convert('RGBA')				
				#img2 = Image.blend(img2, newImg, 0.0)
				img2.paste(newImg, mask=newImg)
				newImg = img2
			"""
			imgObj = newImg
		else:
			#print "The type is: %s and it is else" % iList['_type']
			
			imgObj = Image.open(imgFile).convert('RGBA')

			if iList['_type'] == "box":
				boxImage = Image.new("RGBA", (w,h), (255,255,255,0))
				imgObj.thumbnail((w,h), Image.ANTIALIAS)
				boxImage.paste(imgObj, ((w - imgObj.size[0]) / 2, (h - imgObj.size[1]) /2 ))
				imgObj = boxImage

		if re.search('/generate_embellishment/', iList['img'][0]['src']):
			embellishment_color = eProperties[1].split('=')[1]
			embellishment_color = (int(embellishment_color[0:3]), int(embellishment_color[3:6]), int(embellishment_color[6:9]))
			newImg = Image.new("RGBA", imgObj.size, embellishment_color)
			r, g, b, alpha = imgObj.split()

			if embObj.e_type.id == 3:
				newImg.paste(imgObj, mask=b)
				imgObj = newImg
			elif embObj.e_type.id == 2 or embObj.e_type.id == 4:
				imgObj.paste(newImg, mask=alpha)


		#apply opacity
		if int(iList['opacity']) != 100:
			#adjust opacity
			floatOpacity = float(float(iList['opacity']) / float(100))
			alpha = imgObj.split()[3]
			alpha = ImageEnhance.Brightness(alpha).enhance(floatOpacity)
			imgObj.putalpha(alpha)

		#try to rotate
		try:
			#imgObj.thumbnail((w,h),Image.ANTIALIAS)
			imgObj = imgObj.resize((w,h), Image.ANTIALIAS)
			imgObj = imgObj.rotate(float(iList['angle']), expand=1,resample=Image.BICUBIC)
			"""
			print "The width is: %s, and height is: %s" % (w,h)
			print "The new width is: %s, and the new height is: %s" % imgObj.size
			
			aW = int((w / 2) * math.cos(float(iList['angle']))) + int((h / 2) * math.cos(90 - float(iList['angle'])))
			aH = int((w / 2) * math.sin(float(iList['angle']))) + int((h / 2) * math.sin(90 - float(iList['angle'])))
			
			
			imgObj.thumbnail((w,h),Image.ANTIALIAS)
			"""
		except:
			#imgObj.thumbnail((w,h),Image.ANTIALIAS)
			imgObj = imgObj.resize((w,h), Image.ANTIALIAS)
			

		#flip and flap
		exec('matrix=%s' % iList['matrix'])

		if matrix[0]['e']:
			#flip
			imgObj = imgObj.transpose(Image.FLIP_TOP_BOTTOM)

		if matrix[0]['f']:
			#flap
			imgObj = imgObj.transpose(Image.FLIP_LEFT_RIGHT)
		
		"""
		try:

			if splittedName[1] == '.jpg':
				mainImage.paste(imgObj,(int(float(iList['left'])) - lowestLeft,int(float(iList['top'])) - lowestTop))
			else:	
				mainImage.paste(imgObj,(int(float(iList['left'])) - lowestLeft,int(float(iList['top'])) - lowestTop), mask=imgObj)
		except:

			mainImage.paste(imgObj,(int(float(iList['left'])) - lowestLeft,int(float(iList['top'])) - lowestTop), mask=imgObj)
		"""
		mainImage.paste(imgObj,(int(float(iList['left'])) - lowestLeft,int(float(iList['top'])) - lowestTop), mask=imgObj)
		#paste image
		#mainImage.paste(imgObj, (highestWidth - (w + int(iList['left'])), highestHeight - (h + int(iList['top']))))

	response = HttpResponse(mimetype="image/png")
	
	mainImage.thumbnail((imageWidth,imageHeight), Image.ANTIALIAS)
	bgImg = Image.new('RGBA', (imageWidth, imageHeight), (255, 255, 255, 0))
	bgImg.paste(mainImage,((imageWidth - mainImage.size[0]) / 2, (imageHeight - mainImage.size[1]) / 2))
	bgImg.save(response, "PNG")
	"""
	mainImage.save(response, "PNG")
	"""
	return response

def social_redirect(request):

	if 'fb_auth_error' in request.session:
		return redirect('invite_friends')
	else:

		if "last_page_idecorate" in request.session:
			print request.session['last_page_idecorate']
			return redirect(request.session.get('last_page_idecorate'))
		else:
			return redirect('/')


def generate_styleboard_template_view(request, id, w, h):
	
	styleboardItem = StyleboardTemplateItems.objects.get(id=id)
	itemString = str(styleboardItem.item).replace('null,','')
	itemList = []
	
	imageWidth = int(w)
	imageHeight = int(h)

	lowestTop = None
	highestTop = None
	lowestLeft = None
	highestLeft = None

	finalHeight = 0
	finalWidth = 0
	widthIndex = 0
	heightIndex = 0
	true = True
	false = False

	exec('itemList=%s' % itemString)

	for iList in itemList:

		if re.search('/media/products/',iList['img'][0]['src']):

			imgFile = iList['img'][0]['src'].split('/')
			imgFile = imgFile[len(imgFile) - 1].split('?')[0]
			imgFile = "%s%s%s" % (settings.MEDIA_ROOT, 'products/', unquote(imgFile))

		elif re.search('/generate_embellishment/', iList['img'][0]['src']):
			eProperties = iList['img'][0]['src'].split("?")[1].split('&')

			directory = ""

			embObj = Embellishments.objects.get(id=int(eProperties[0].split('=')[1]))

			if embObj.e_type.id == 1:
				directory = "images"
			elif embObj.e_type.id == 2:
				directory = "textures"
			elif embObj.e_type.id == 3:
				directory = "patterns"
			elif embObj.e_type.id == 4:
				directory = "shapes"
			elif embObj.e_type.id == 5:
				directory = "borders"

			imgFile = "%s%s%s" % (settings.MEDIA_ROOT, "embellishments/%s/" % directory, embObj.image)
		elif re.search('/media/embellishments/',iList['img'][0]['src']):

			imgFile = iList['img'][0]['src'].split('/')
			imgFile = imgFile[len(imgFile) - 1]
			imgFile = "%s%s%s" % (settings.MEDIA_ROOT, 'embellishments/images/', unquote(imgFile))

		elif re.search('/generate_text/',iList['img'][0]['src']):
			eProperties = iList['img'][0]['src'].split("?")[1].split('&')

			fontObj = TextFonts.objects.get(id=int(eProperties[3].split('=')[1]))
			imgFile = "%s%s%s" % (settings.MEDIA_ROOT, "fonts/", fontObj.font)
			font_size = int(eProperties[0].split('=')[1])
			font_color = eProperties[2].split('=')[1]
			font_color = (int(font_color[0:3]), int(font_color[3:6]), int(font_color[6:9]))
			image_text = unquote(eProperties[1].split('=')[1])
		elif re.search('/cropped/',iList['img'][0]['src']):
			eProperties = iList['img'][0]['src'].split("?")[1].split('&')

			imgFile = "%s%s%s" % (settings.MEDIA_ROOT, "products/", unquote(eProperties[3].split('=')[1]))
			task = eProperties[1].split('=')[1]

			splittedPosts = unquote(eProperties[2].split('=')[1]).split(',')
		elif re.search('/media/admin/img/fake_BG.png',iList['img'][0]['src']):
			imgFile = "%s%s" % (settings.MEDIA_ROOT, "products/white_background.png")


		style = iList['style']
		splittedStyle = style.split(';')

		#find width and height index
		ctr = 0
		for item in splittedStyle:
			if re.search('width', item):
				widthIndex = ctr
			if re.search('height', item):
				heightIndex = ctr
			ctr += 1

		w = int(float(str(splittedStyle[widthIndex].split(':')[1]).strip().replace('px','')))
		h = int(float(str(splittedStyle[heightIndex].split(':')[1]).strip().replace('px','')))

		try:
			if re.search('/generate_text/',iList['img'][0]['src']):

				font = ImageFont.truetype(imgFile, font_size)
				
				image_text = image_text.replace("\r", "")
				splittedTexts = image_text.split("\n")
				totalHeight = 0
				upperWidth = 0
				heightList = [0]

				#compute the final width and height first
				for splittedText in splittedTexts:
					textSize = font.getsize(splittedText)
					totalHeight += textSize[1]
					heightList.append(totalHeight)

					if upperWidth == 0:
						upperWidth = textSize[0]
					else:
						if textSize[0] > upperWidth:
							upperWidth = textSize[0]

				#image with background transparent
				img = Image.new("RGBA", (upperWidth, totalHeight), (255,255,255, 0))
				#create draw object	
				draw = ImageDraw.Draw(img)
				#draw the text
				ctr = 0

				for splittedText in splittedTexts:
					#draw text
					draw.text((0,heightList[ctr]), splittedText, font_color, font=font)
					ctr += 1

				imgObj = img
				#imgObj.thumbnail((w,h),Image.ANTIALIAS)
				imgObj = imgObj.resize((w,h), Image.ANTIALIAS)
				imgObj = imgObj.rotate(float(iList['angle']), expand=1)
				w, h = imgObj.size
			elif re.search('/cropped/',iList['img'][0]['src']):

				img = Image.open(imgFile)
				back = Image.new('RGBA', (400,400), (255, 255, 255, 0))
				back.paste(img, ((400 - img.size[0]) / 2, (400 - img.size[1]) /2 ))

				poly = Image.new('RGBA', (settings.PRODUCT_WIDTH,settings.PRODUCT_HEIGHT), (255, 255, 255, 0))
				pdraw = ImageDraw.Draw(poly)

				dimensionList = []

				if task == 'poly':
					for splittedPost in splittedPosts:
						spl = splittedPost.split(':')
						dimensionList.append((float(spl[0]),float(spl[1])))

					pdraw.polygon(dimensionList,fill=(255,255,255,255),outline=(255,255,255,255))

				elif task == 'rect':
					for splittedPost in splittedPosts:
						dimensionList.append(float(splittedPost))
					pdraw.rectangle(dimensionList,fill=(255,255,255,255),outline=(255,255,255,255))


				poly.paste(back,mask=poly)

				newImg = poly.crop(((400 - img.size[0]) / 2, (400 - img.size[1]) /2 , ((400 - img.size[0]) / 2) + img.size[0], ((400 - img.size[1]) / 2) + img.size[1]))
				imgObj = newImg
				imgObj = imgObj.resize((w,h), Image.ANTIALIAS)
				imgObj = imgObj.rotate(float(iList['angle']), expand=1)
				w, h = imgObj.size
			else:
				imgObj = Image.open(imgFile).convert('RGBA')
				#imgObj.thumbnail((w,h),Image.ANTIALIAS)
				imgObj = imgObj.resize((w,h), Image.ANTIALIAS)
				imgObj = imgObj.rotate(float(iList['angle']), expand=1)
				w, h = imgObj.size
		except:
			pass

		if lowestTop is None:
			lowestTop = int(float(iList['top']))
		else:
			if int(float(iList['top'])) < lowestTop:
				lowestTop = int(float(iList['top']))

		if highestTop is None:
			highestTop = int(float(iList['top'])) + h
		else:
			if (int(float(iList['top'])) + h) > highestTop:
				highestTop = int(float(iList['top'])) + h

		if lowestLeft is None:
			lowestLeft = int(float(iList['left']))
		else:
			if int(float(iList['left'])) < lowestLeft:
				lowestLeft = int(float(iList['left']))

		if highestLeft is None:
			highestLeft = int(float(iList['left'])) + w
		else:
			if (int(float(iList['left'])) + w) > highestLeft:
				highestLeft = int(float(iList['left'])) + w

	finalWidth = highestLeft - lowestLeft
	finalHeight = highestTop - lowestTop

	#create main image
	mainImage = Image.new('RGBA', (finalWidth, finalHeight), (255, 255, 255, 0))


	for iList in itemList:

		if re.search('/media/products/',iList['img'][0]['src']):

			imgFile = iList['img'][0]['src'].split('/')
			imgFile = imgFile[len(imgFile) - 1].split('?')[0]
			imgFile = "%s%s%s" % (settings.MEDIA_ROOT, 'products/', unquote(imgFile))
		elif re.search('/generate_embellishment/', iList['img'][0]['src']):
			eProperties = iList['img'][0]['src'].split("?")[1].split('&')

			directory = ""

			embObj = Embellishments.objects.get(id=int(eProperties[0].split('=')[1]))

			if embObj.e_type.id == 1:
				directory = "images"
			elif embObj.e_type.id == 2:
				directory = "textures"
			elif embObj.e_type.id == 3:
				directory = "patterns"
			elif embObj.e_type.id == 4:
				directory = "shapes"
			elif embObj.e_type.id == 5:
				directory = "borders"

			imgFile = "%s%s%s" % (settings.MEDIA_ROOT, "embellishments/%s/" % directory, embObj.image)
		elif re.search('/media/embellishments/',iList['img'][0]['src']):

			imgFile = iList['img'][0]['src'].split('/')
			imgFile = imgFile[len(imgFile) - 1]
			imgFile = "%s%s%s" % (settings.MEDIA_ROOT, 'embellishments/images/', unquote(imgFile))
		elif re.search('/generate_text/',iList['img'][0]['src']):
			eProperties = iList['img'][0]['src'].split("?")[1].split('&')

			fontObj = TextFonts.objects.get(id=int(eProperties[3].split('=')[1]))
			imgFile = "%s%s%s" % (settings.MEDIA_ROOT, "fonts/", fontObj.font)
			font_size = int(eProperties[0].split('=')[1])
			font_color = eProperties[2].split('=')[1]
			font_color = (int(font_color[0:3]), int(font_color[3:6]), int(font_color[6:9]))
			image_text = unquote(eProperties[1].split('=')[1])
			#print "The text is: %s" % image_text
		elif re.search('/cropped/',iList['img'][0]['src']):
			eProperties = iList['img'][0]['src'].split("?")[1].split('&')

			imgFile = "%s%s%s" % (settings.MEDIA_ROOT, "products/", unquote(eProperties[3].split('=')[1]))
			task = eProperties[1].split('=')[1]

			splittedPosts = unquote(eProperties[2].split('=')[1]).split(',')
		elif re.search('/media/admin/img/fake_BG.png',iList['img'][0]['src']):
			imgFile = "%s%s" % (settings.MEDIA_ROOT, "products/white_background.png")

		style = iList['style']
		splittedStyle = style.split(';')

		#find width and height index
		ctr = 0
		for item in splittedStyle:
			if re.search('width', item):
				widthIndex = ctr
			if re.search('height', item):
				heightIndex = ctr
			ctr += 1

		w = int(float(str(splittedStyle[widthIndex].split(':')[1]).strip().replace('px','')))
		h = int(float(str(splittedStyle[heightIndex].split(':')[1]).strip().replace('px','')))


		if re.search('/generate_text/',iList['img'][0]['src']):

			font = ImageFont.truetype(imgFile, font_size)
			
			image_text = image_text.replace("\r", "")	
			splittedTexts = image_text.split("\n")
			totalHeight = 0
			upperWidth = 0
			heightList = [0]

			#compute the final width and height first
			for splittedText in splittedTexts:
				textSize = font.getsize(splittedText)
				totalHeight += textSize[1]
				heightList.append(totalHeight)

				if upperWidth == 0:
					upperWidth = textSize[0]
				else:
					if textSize[0] > upperWidth:
						upperWidth = textSize[0]

			#image with background transparent
			img = Image.new("RGBA", (upperWidth, totalHeight), (255,255,255, 0))
			#create draw object	
			draw = ImageDraw.Draw(img)
			#draw the text
			ctr = 0

			for splittedText in splittedTexts:
				#draw text
				draw.text((0,heightList[ctr]), splittedText, font_color, font=font)
				ctr += 1

			imgObj = img
		elif re.search('/cropped/',iList['img'][0]['src']):

			img = Image.open(imgFile)
			back = Image.new('RGBA', (400,400), (255, 255, 255, 0))
			back.paste(img, ((400 - img.size[0]) / 2, (400 - img.size[1]) /2 ))

			poly = Image.new('RGBA', (settings.PRODUCT_WIDTH,settings.PRODUCT_HEIGHT), (255, 255, 255, 0))
			pdraw = ImageDraw.Draw(poly)

			dimensionList = []

			if task == 'poly':
				for splittedPost in splittedPosts:
					spl = splittedPost.split(':')
					dimensionList.append((float(spl[0]),float(spl[1])))

				pdraw.polygon(dimensionList,fill=(255,255,255,255),outline=(255,255,255,255))

			elif task == 'rect':
				for splittedPost in splittedPosts:
					dimensionList.append(float(splittedPost))
				pdraw.rectangle(dimensionList,fill=(255,255,255,255),outline=(255,255,255,255))

			poly.paste(back,mask=poly)

			newImg = poly.crop(((400 - img.size[0]) / 2, (400 - img.size[1]) /2 , ((400 - img.size[0]) / 2) + img.size[0], ((400 - img.size[1]) / 2) + img.size[1]))

			"""
			splittedName = getExtensionAndFileName(imgFile)
			if splittedName[1] == '.jpg':
				img2 = Image.open("%s%s" % (settings.MEDIA_ROOT, "products/white_background.png"))
				img2 = img2.resize((newImg.size[0],newImg.size[1]), Image.ANTIALIAS)
				img2 = img2.convert('RGBA')				
				#img2 = Image.blend(img2, newImg, 0.0)
				img2.paste(newImg, mask=newImg)
				newImg = img2
			"""
			imgObj = newImg
		else:

			imgObj = Image.open(imgFile).convert('RGBA')

		if re.search('/generate_embellishment/', iList['img'][0]['src']):
			embellishment_color = eProperties[1].split('=')[1]
			embellishment_color = (int(embellishment_color[0:3]), int(embellishment_color[3:6]), int(embellishment_color[6:9]))
			newImg = Image.new("RGBA", imgObj.size, embellishment_color)
			r, g, b, alpha = imgObj.split()

			if embObj.e_type.id == 3:
				newImg.paste(imgObj, mask=b)
				imgObj = newImg
			elif embObj.e_type.id == 2 or embObj.e_type.id == 4:
				imgObj.paste(newImg, mask=alpha)


		if re.search('/media/admin/img/fake_BG.png',iList['img'][0]['src']):

			alpha = imgObj.split()[3]
			alpha = ImageEnhance.Brightness(alpha).enhance(0.50)
			imgObj.putalpha(alpha)

			borderImage = ImageOps.expand(imgObj, border=5, fill='black')
			imgObj = borderImage

		#apply opacity
		if int(iList['opacity']) != 100:
			#adjust opacity
			floatOpacity = float(float(iList['opacity']) / float(100))
			alpha = imgObj.split()[3]
			alpha = ImageEnhance.Brightness(alpha).enhance(floatOpacity)
			imgObj.putalpha(alpha)

		#try to rotate
		try:
			#imgObj.thumbnail((w,h),Image.ANTIALIAS)
			imgObj = imgObj.resize((w,h), Image.ANTIALIAS)
			imgObj = imgObj.rotate(float(iList['angle']), expand=1,resample=Image.BICUBIC)
			"""
			print "The width is: %s, and height is: %s" % (w,h)
			print "The new width is: %s, and the new height is: %s" % imgObj.size
			
			aW = int((w / 2) * math.cos(float(iList['angle']))) + int((h / 2) * math.cos(90 - float(iList['angle'])))
			aH = int((w / 2) * math.sin(float(iList['angle']))) + int((h / 2) * math.sin(90 - float(iList['angle'])))
			
			
			imgObj.thumbnail((w,h),Image.ANTIALIAS)
			"""
		except:
			#imgObj.thumbnail((w,h),Image.ANTIALIAS)
			imgObj = imgObj.resize((w,h), Image.ANTIALIAS)
			

		#flip and flap
		exec('matrix=%s' % iList['matrix'])

		if matrix[0]['e']:
			#flip
			imgObj = imgObj.transpose(Image.FLIP_TOP_BOTTOM)

		if matrix[0]['f']:
			#flap
			imgObj = imgObj.transpose(Image.FLIP_LEFT_RIGHT)
		
		"""
		try:

			if splittedName[1] == '.jpg':
				mainImage.paste(imgObj,(int(float(iList['left'])) - lowestLeft,int(float(iList['top'])) - lowestTop))
			else:	
				mainImage.paste(imgObj,(int(float(iList['left'])) - lowestLeft,int(float(iList['top'])) - lowestTop), mask=imgObj)
		except:

			mainImage.paste(imgObj,(int(float(iList['left'])) - lowestLeft,int(float(iList['top'])) - lowestTop), mask=imgObj)
		"""
		mainImage.paste(imgObj,(int(float(iList['left'])) - lowestLeft,int(float(iList['top'])) - lowestTop), mask=imgObj)
		#paste image
		#mainImage.paste(imgObj, (highestWidth - (w + int(iList['left'])), highestHeight - (h + int(iList['top']))))

	response = HttpResponse(mimetype="image/png")
	
	mainImage.thumbnail((imageWidth,imageHeight), Image.ANTIALIAS)
	bgImg = Image.new('RGBA', (imageWidth, imageHeight), (255, 255, 255, 0))
	bgImg.paste(mainImage,((imageWidth - mainImage.size[0]) / 2, (imageHeight - mainImage.size[1]) / 2))
	bgImg.save(response, "PNG")
	"""
	mainImage.save(response, "PNG")
	"""
	return response