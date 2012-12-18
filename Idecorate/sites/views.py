from django.shortcuts import HttpResponse, redirect, render_to_response

def help(request):
	return render_to_response('sites/help.html')

def about(request):
	return render_to_response('sites/about.html')

def contact(request):
	return render_to_response('sites/contact.html')

def tos(request):
	return render_to_response('sites/tos.html')

def returnspolicy(request):
	return render_to_response('sites/returnspolicy.html')

def privacy(request):
	return render_to_response('sites/privacy.html')

def copyright(request):
	return render_to_response('sites/copyright.html')
