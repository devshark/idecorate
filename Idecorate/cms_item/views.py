import logging
from django.conf import  settings
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.shortcuts import render_to_response, redirect, HttpResponse
from django.contrib import messages
from django.contrib.flatpages.models import FlatPage
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.flatpages.forms import FlatpageForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from cms_item.forms import EditFlatpageForm
from django.core.urlresolvers import reverse
from django.http import HttpResponseNotFound, Http404

@staff_member_required
def flatpage_admin(request):
	context_instance = RequestContext(request)
	info = {}

	flatpages = FlatPage.objects.all()
	info['flatpages'] = flatpages

	return render_to_response('admin/flatpages/flatpage_admin.html',info,context_instance)

@staff_member_required
def add_flatpage(request):
	context_instance = RequestContext(request)
	info = {}

	form = FlatpageForm()

	if request.method == 'POST':
		data = request.POST.copy()
		data['sites'] = 1
		form = FlatpageForm(data)
		if form.is_valid():
			try:
				form.save()
				messages.success(request, 'Created new site page.')
				return render_to_response('wallet_admin/iframe/closer.html',info,context_instance)
			except Exception as e:
				messages.error(request, 'An error has occurred.')

	info['form'] = form
	info['mod'] = 'Create'

	return render_to_response('admin/flatpages/add_flatpage.html',info,context_instance)

@staff_member_required
def edit_flatpage(request, page_id=None):
	context_instance = RequestContext(request)
	info = {}
	try:
		flatPage = FlatPage.objects.get(id=page_id)
	except Exception as e:
		return redirect('flatpage_admin')

	form = EditFlatpageForm(instance=flatPage)

	if request.method == 'POST':
		data = request.POST.copy()
		data['sites'] = 1
		data['flatPage'] = flatPage
		form = EditFlatpageForm(data)
		if form.is_valid():
			res = save_flatpage(data)
			if res:
				messages.success(request, 'Successfully modified site page.')
				#return render_to_response('wallet_admin/iframe/closer.html',info,context_instance)
				return redirect(reverse('edit_flatpage', args=[page_id]))
			else:
				messages.error(request, 'Flatpage with url %s already exists.' % data['url'])			

	info['form'] = form
	info['mod'] = 'Modify'

	return render_to_response('admin/flatpages/add_flatpage.html',info,context_instance)

def save_flatpage(data):
	flatPage = data['flatPage']
	url = data['url']
	sites = [data['sites']]
	same_url = FlatPage.objects.filter(url=url)
	same_url = same_url.exclude(pk=flatPage.pk)		

	if same_url.filter(sites__in=sites).exists():
		for site in sites:
			if same_url.filter(sites=site).exists():
				return False

	flatPage.content = data['content']
	flatPage.url = data['url']
	flatPage.title = data['title']
	flatPage.save()
	return True

def delete_flatpage(request):
	if request.method == "POST":
		id = request.POST['id']
		fp = FlatPage.objects.get(id=id)
		fp.delete()
		return HttpResponse(1)
	else:
		return HttpResponseNotFound()
