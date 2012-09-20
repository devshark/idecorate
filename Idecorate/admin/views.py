# Create your views here.
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import HttpResponse, redirect, render_to_response
from django.contrib.auth import authenticate, login, logout
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from admin.models import LoginLog
from datetime import datetime, timedelta
from django.template import RequestContext

@staff_member_required
def admin(request):
    info = {}

    return render_to_response('admin/index.html',info,RequestContext(request))

@staff_member_required
def admin_manage_menu(request):
    info = {}

    return render_to_response('admin/admin_manage_menu.html',info,RequestContext(request))

def admin_login(request):

	if request.method == 'POST':

		loginLog = LoginLog.objects.filter(created__gte=(datetime.now() - timedelta(minutes=5)), ip_address=request.META['REMOTE_ADDR'])

		username = request.POST['username']
		password = request.POST['password']

		request.session['admin_username'] = username
		request.session['admin_password'] = password
		request.session['admin_login_post'] = True

		user = authenticate(username=username, password=password)

		if loginLog.count() >= 5:
			request.session['showMessages'] = True
			messages.error(request, _('Please try to login after 5 minutes'))
			return redirect('admin')

		if str(username).strip() != "" and str(password).strip() != "":
			request.session['showMessages'] = True

		if user is not None:

			if user.is_active:
				login(request, user)
				del request.session['admin_username']
				del request.session['admin_password']
				del request.session['admin_login_post']

				try:
					request.session['showMessages']
				except KeyError:
					pass

				#Successfull login, delete all the log attempts
				LoginLog.objects.filter(ip_address=request.META['REMOTE_ADDR']).delete()

			else:
				if "showMessages" in request.session:
					messages.error(request, _('Sorry this account is disabled'))
		else:
			if "showMessages" in request.session:
				#log ip address
				loginLog = LoginLog()
				loginLog.created = datetime.now()
				loginLog.ip_address = request.META['REMOTE_ADDR']
				loginLog.save()

				messages.error(request, _('Sorry we could not verify your username and password'))

	return redirect('admin')


def admin_logout(request):

	logout(request)

	return redirect('admin')

