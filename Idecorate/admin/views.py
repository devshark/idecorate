# Create your views here.
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import HttpResponse, redirect
from django.contrib.auth import authenticate, login, logout
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

@staff_member_required
def admin(request):

	return HttpResponse("Blank Page")

def admin_login(request):

	if request.method == 'POST':

		username = request.POST['username']
		password = request.POST['password']

		request.session['admin_username'] = username
		request.session['admin_password'] = password
		request.session['admin_login_post'] = True

		user = authenticate(username=username, password=password)

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

			else:
				if "showMessages" in request.session:
					messages.error(request, _('Sorry this account is disabled'))
		else:
			if "showMessages" in request.session:
				messages.error(request, _('Sorry we could not verify your username and password'))

	return redirect('admin')


def admin_logout(request):

	logout(request)

	return redirect('admin')

