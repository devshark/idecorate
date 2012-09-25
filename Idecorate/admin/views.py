# Create your views here.
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import HttpResponse, redirect, render_to_response
from django.contrib.auth import authenticate, login, logout
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from admin.models import LoginLog
from datetime import datetime, timedelta
from django.template import RequestContext
from admin.forms import CategoryForm, MenuAddForm
from admin.services import save_category

from category.models import Categories
from menu.services import addMenu
from menu.models import InfoMenu, SiteMenu, FooterMenu

@staff_member_required
def admin(request):
    info = {}

    return render_to_response('admin/index.html',info,RequestContext(request))

@staff_member_required
def admin_manage_menu(request):
    info = {}

    form_info_menu = MenuAddForm(initial={'menu_type':'1'})
    form_site_menu = MenuAddForm(initial={'menu_type':'2'})
    form_footer_menu = MenuAddForm(initial={'menu_type':'3'})

    info_menus = InfoMenu.objects.filter(parent__id=None).order_by('order')
    site_menus = SiteMenu.objects.filter(parent__id=None).order_by('order')
    footer_menus = FooterMenu.objects.filter(parent__id=None).order_by('order')

    task = request.POST.get('task', None)

    if request.method == 'POST':

		info['menu_type'] = request.POST.get('menu_type')
		
		if request.POST.get('menu_type') == "1":

			if task:
				arrangement = request.POST.get('arrangement')

				arrangementList = arrangement.split(';')

				for a in arrangementList:
					if a != "":
						splitValues = a.split(':')
						arrange_info = InfoMenu.objects.get(id=int(splitValues[0]))
						arrange_info.order = int(splitValues[1])

						if splitValues[2].strip() == "None":
							arrange_info.parent = None
						else:
							arrange_info.parent = InfoMenu.objects.get(id=int(splitValues[2]))

						arrange_info.save()
				info['info_message'] = True
				messages.success(request, _('Arrangement saved.'))

			else:

				form_info_menu = MenuAddForm(request.POST)

				info['info_message'] = True

				if form_info_menu.is_valid():
					addMenu(form_info_menu.cleaned_data['name'], form_info_menu.cleaned_data['link'], form_info_menu.cleaned_data['menu_type'])
					form_info_menu = MenuAddForm(initial={'menu_type':'1'})
					messages.success(request, _('Menu saved.'))

		elif request.POST.get('menu_type') == "2":

			if task:
				arrangement = request.POST.get('arrangement')

				arrangementList = arrangement.split(';')

				for a in arrangementList:
					if a != "":
						splitValues = a.split(':')
						arrange_site = SiteMenu.objects.get(id=int(splitValues[0]))
						arrange_site.order = int(splitValues[1])

						if splitValues[2].strip() == "None":
							arrange_site.parent = None
						else:
							arrange_site.parent = SiteMenu.objects.get(id=int(splitValues[2]))

						arrange_site.save()
				info['site_message'] = True
				messages.success(request, _('Arrangement saved.'))
			else:

				form_site_menu = MenuAddForm(request.POST)

				info['site_message'] = True

				if form_site_menu.is_valid():
					addMenu(form_site_menu.cleaned_data['name'], form_site_menu.cleaned_data['link'], form_site_menu.cleaned_data['menu_type'])
					form_site_menu = MenuAddForm(initial={'menu_type':'2'})
					messages.success(request, _('Menu saved.'))

		elif request.POST.get('menu_type') == "3":

			if task:
				arrangement = request.POST.get('arrangement')

				arrangementList = arrangement.split(';')

				for a in arrangementList:
					if a != "":
						splitValues = a.split(':')
						arrange_footer = FooterMenu.objects.get(id=int(splitValues[0]))
						arrange_footer.order = int(splitValues[1])

						if splitValues[2].strip() == "None":
							arrange_footer.parent = None
						else:
							arrange_footer.parent = FooterMenu.objects.get(id=int(splitValues[2]))

						arrange_footer.save()
				info['footer_message'] = True
				messages.success(request, _('Arrangement saved.'))
			else:

				form_footer_menu = MenuAddForm(request.POST)

				info['footer_message'] = True

				if form_footer_menu.is_valid():
					addMenu(form_footer_menu.cleaned_data['name'], form_footer_menu.cleaned_data['link'], form_footer_menu.cleaned_data['menu_type'])
					form_footer_menu = MenuAddForm(initial={'menu_type':'3'})
					messages.success(request, _('Menu saved.'))

    info['form_info_menu'] = form_info_menu
    info['form_site_menu'] = form_site_menu
    info['form_footer_menu'] = form_footer_menu
    info['info_menus'] = info_menus
    info['site_menus'] = site_menus
    info['footer_menus'] = footer_menus
    return render_to_response('admin/admin_manage_menu.html',info,RequestContext(request))


@staff_member_required
def admin_delete_menu(request,id_delete,menuType):
	pass

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

@staff_member_required
def category(request):
	info = {}
	parent = None	
	form = CategoryForm()

	if request.method == 'POST':
		form = CategoryForm(request.POST)
		if form.is_valid():
			data = form.cleaned_data
			res = save_category(data)
			return redirect('category')

	categories = Categories.objects.filter(parent__id=None)
	info['form'] = form
	info['categories'] = categories
	return render_to_response('admin/category.html', info, RequestContext(request))