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
from PIL import Image, ImageDraw, ImageFont, ImageOps
from models import StyleboardItems

from forms import LoginForm, SignupForm, SaveStyleboardForm
from services import register_user, customer_profile, get_client_ip, get_user_styleboard, save_styleboard_item,\
	get_customer_styleboard_item, manage_styleboard_cart_items
from admin.models import LoginLog, TextFonts, Embellishments, EmbellishmentsType
from django.conf import settings
import re
import math

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
	if not request.user.is_authenticated():
		return redirect('home')
	info = {}
	user_profile = customer_profile(request.user)
	info['user_profile'] = user_profile
	info['currentUrl'] = request.get_full_path()
	user_styleboard = get_user_styleboard(request.user)
	info['user_styleboard'] = user_styleboard
	return render_to_response('customer/profile.html', info, RequestContext(request))

def save_styleboard(request):
	if not request.user.is_authenticated():
		return redirect('styleboard')
	info = {}
	customer_styleboard = None
	try:		
		customer_styleboard = request.session['customer_styleboard']	
		form = SaveStyleboardForm(initial={'name':customer_styleboard.styleboard_item.name,'description':customer_styleboard.styleboard_item.description})
	except Exception as e:
		print e
		form = SaveStyleboardForm()
	if request.method == "POST":
		form = SaveStyleboardForm(request.POST)		
		if form.is_valid():
			cleaned_datas = form.cleaned_data
			cleaned_datas['user'] = request.user
			cleaned_datas['customer_styleboard'] = customer_styleboard				
			res = save_styleboard_item(cleaned_datas)
			request.session['customer_styleboard'] = res
			info['action'] = 'save_styleboard'
			info['msg'] =  _('Style board saved.')
			return render_to_response('customer/iframe/success.html', info)
	info['form'] = form
	return render_to_response('customer/iframe/save_styleboard.html', info, RequestContext(request))

def styleboard_view(request):
	info = {}
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

		if re.search('/media/products/',iList['img'][0]['src']):

			imgFile = iList['img'][0]['src'].split('/')
			imgFile = imgFile[len(imgFile) - 1].split('?')[0]
			imgFile = "%s%s%s" % (settings.MEDIA_ROOT, 'products/', imgFile)

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
			imgFile = "%s%s%s" % (settings.MEDIA_ROOT, 'products/', imgFile)
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

		#try to rotate
		try:
			#imgObj.thumbnail((w,h),Image.ANTIALIAS)
			imgObj = imgObj.resize((w,h), Image.ANTIALIAS)
			imgObj = imgObj.rotate(float(iList['angle']), expand=1)
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

		if matrix['e']:
			#flip
			imgObj = imgObj.transpose(Image.FLIP_TOP_BOTTOM)

		if matrix['f']:
			#flap
			imgObj = imgObj.transpose(Image.FLIP_LEFT_RIGHT)
		

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
