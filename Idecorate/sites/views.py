from django.shortcuts import HttpResponse, redirect, render_to_response
from django.contrib.flatpages.models import FlatPage

def help(request):
	info = {}
	flatPage = get_flatpage_details('Help')
	info['flatPage'] = flatPage
	info['user'] = request.user
	return render_to_response('sites/help.html', info)

def about(request):
	info = {}
	flatPage = get_flatpage_details('About Us')
	if not flatPage:
		flatPage = get_flatpage_details('About')

	info['flatPage'] = flatPage
	info['user'] = request.user
	return render_to_response('sites/about.html', info)

def contact(request):
	info = {}
	flatPage = get_flatpage_details('Contact Us')
	if not flatPage:
		flatPage = get_flatpage_details('Contact')
	info['flatPage'] = flatPage
	info['user'] = request.user
	return render_to_response('sites/contact.html', info)

def tos(request):
	return render_to_response('sites/tos.html')

def returnspolicy(request):
	return render_to_response('sites/returnspolicy.html')

def privacy(request):
	return render_to_response('sites/privacy.html')

def copyright(request):
	return render_to_response('sites/copyright.html')

def get_flatpage_details(title):
	flatPage = None
	try:
		flatPage = FlatPage.objects.get(title=title)
	except:
		try:
			flatPage = FlatPage.objects.get(title=title)
		except:
			pass

	return flatPage