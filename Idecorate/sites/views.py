from django.shortcuts import HttpResponse, redirect, render_to_response

def help(request):
	return render_to_response('sites/help.html')

def privacy(request):
	return render_to_response('sites/privacy.html')