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
				messages.success(request, 'Added new flatpage.')
				return render_to_response('wallet_admin/iframe/closer.html',info,context_instance)
			except Exception as e:
				messages.error(request, 'An error has occurred.')

	info['form'] = form

	return render_to_response('admin/flatpages/add_flatpage.html',info,context_instance)

# @staff_member_required
# def edit_flatpage(request, flatpage_id):
# 	context_instance = RequestContext(request)
# 	info = {}

# 	if not FlatPage.objects.filter(sites__in=[1,]).filter(id=flatpage_id).exists():
# 		messages.error(request, 'Invalid flatpage id.')
# 		return render_to_response('wallet_admin/iframe/closer.html',info,context_instance)

# 	try:
# 		flatpage = FlatPage.objects.get(pk=flatpage_id)
# 	except Exception as e:
# 		messages.error(request, 'Invalid flatpage id.')
# 		return render_to_response('wallet_admin/iframe/closer.html',info,context_instance)

# 	form = AddFlatpageForm(instance=flatpage)

# 	if request.method == 'POST':
# 		data = request.POST.copy()
# 		data['sites'] = 1
# 		form = AddFlatpageForm(data,instance=flatpage)
# 		if form.is_valid():
# 			try:
# 				form.save()
# 				messages.success(request, 'Changes saved.')
# 				return render_to_response('wallet_admin/iframe/closer.html',info,context_instance)
# 			except Exception as e:
# 				messages.error(request, 'An error has occurred.')

# 	info['form'] = form
# 	info['id'] = flatpage.id

# 	return render_to_response('cms/iframe/edit_flatpage.html',info,context_instance)

# @staff_member_required
# def toggle_flatpage(request, flatpage_id):
# 	context_instance = RequestContext(request)
# 	info = {}

# 	try:
# 		flatpage = FlatPage.objects.get(pk=flatpage_id)
# 	except Exception as e:
# 		messages.error(request, 'Invalid flatpage id.')
# 		return redirect('flatpage_admin')

# 	try:
# 		if flatpage.status == 0:
# 			flatpage.status = 1
# 			flatpage.save()
# 			messages.success(request, 'Flatpage deactivated.')
# 		elif flatpage.status == 1:
# 			flatpage.status = 0
# 			flatpage.save()
# 			messages.success(request, 'Flatpage activated.')
# 	except Exception as e:
#         messages.error(request, 'Error activating/deactivating flatpage.')
#         return redirect('flatpage_admin')
    
#     return redirect('flatpage_admin')

# @staff_member_required
# def delete_flatpage(request, flatpage_id):
# 	context_instance = RequestContext(request)
# 	info = {}

# 	try:
# 		flatpage = FlatPage.objects.get(pk=flatpage_id)
# 	except Exception as e:
# 		messages.error(request, 'Invalid flatpage id.')
# 		return redirect('flatpage_admin')

# 	try:
# 		flatpage.delete()
# 		messages.success(request, 'Flatpage deleted.')
# 	except Exception as e:
# 		messages.error(request, 'Error deleting flatpage.')
# 		return redirect('flatpage_admin')

# 	return redirect('flatpage_admin')

# @staff_member_required
# def idecorate_page_admin(request):
# 	context_instance = RequestContext(request)
# 	info = {}

# 	form = WalletPageSearchForm()
# 	pages = WalletPage.objects.all()

# 	if request.method == 'POST':
# 		form = WalletPageSearchForm(request.POST)
# 		if form.is_valid():
# 			pages = wallet_page_search_helper(form.cleaned_data)

# 	page_data = pagination(request,pages,10,'title','ASC')

# 	info['pages'] = page_data['query']
# 	info['page'] = page_data['pager']
# 	info['sort'] = page_data['sort_options']
# 	info['form'] = form

# 	return render_to_response('cms/idecorate_page_admin.html',info,context_instance)

# @staff_member_required
# def add_idecorate_page(request):
# 	context_instance = RequestContext(request)
# 	info = {}

# 	form = AddWalletPageForm()

# 	if request.method == 'POST':
# 		data = request.POST.copy()
# 		data['status'] = 0
# 		data['view_name'] = data['url']
# 		form = AddWalletPageForm(data)
# 		if form.is_valid():
# 			try:
# 				form.save()
# 				messages.success(request, 'Added new CMS page.')
# 				return render_to_response('wallet_admin/iframe/closer.html',info,context_instance)
# 			except Exception as e:
# 				messages.error(request, 'An error has occurred.')
# 				logger.error('Error adding CMS page: %e' %e)

# 	info['form'] = form

# 	return render_to_response('cms/iframe/add_idecorate_page.html',info,context_instance)

# @staff_member_required
# def edit_idecorate_page(request, page_id):
# 	context_instance = RequestContext(request)
# 	info = {}

# 	if not WalletPage.objects.filter(status=0).filter(id=page_id).exists():
# 		messages.error(request, 'Invalid CMS page id.')
# 		return render_to_response('wallet_admin/iframe/closer.html',info,context_instance)

# 	try:
# 		page = WalletPage.objects.get(pk=page_id)
# 	except Exception as e:
# 		messages.error(request, 'Invalid CMS page id.')
# 		return render_to_response('wallet_admin/iframe/closer.html',info,context_instance)

# 	form = AddWalletPageForm(instance=page)

# 	if request.method == 'POST':
# 		data = request.POST.copy()
# 		data['status'] = 0
# 		data['view_name'] = data['url']
# 		form = AddWalletPageForm(data,instance=page)
# 		if form.is_valid():
# 			try:
# 				form.save()
# 				messages.success(request, 'Changes saved.')
# 				return render_to_response('wallet_admin/iframe/closer.html',info,context_instance)
# 			except Exception as e:
# 				messages.error(request, 'An error has occurred.')

# 	info['form'] = form
# 	info['id'] = page.id
# 	info['page'] = page

# 	return render_to_response('cms/iframe/edit_idecorate_page.html',info,context_instance)

# @staff_member_required
# def delete_idecorate_page(request, page_id):
# 	context_instance = RequestContext(request)
# 	info = {}

# 	try:
# 		page = WalletPage.objects.get(pk=page_id)
# 	except Exception as e:
# 		messages.error(request, 'Invalid CMS page id.')
# 		return redirect('idecorate_page_admin')

# 	try:
# 		page.delete()
# 		messages.success(request, 'CMS page deleted.')
# 	except Exception as e:
# 		messages.error(request, 'Error deleting CMS page.')
# 		return redirect('idecorate_page_admin')

# 	return redirect('idecorate_page_admin')

# @staff_member_required
# def add_idecorate_page_item(request, page_id):
# 	context_instance = RequestContext(request)
# 	info = {}

# 	if not WalletPage.objects.filter(status=0).filter(id=page_id).exists():
# 		messages.error(request, 'Invalid CMS page id.')
# 		return render_to_response('wallet_admin/iframe/closer.html',info,context_instance)

# 	form = AddWalletPageItemForm()

# 	cancel = request.POST.get('cancel',None)
# 	if cancel:
# 		return redirect('edit_idecorate_page', page_id=page_id)

# 	if request.method == 'POST':
# 		data = request.POST.copy()
# 		data['status'] = 0
# 		data['page'] = page_id
# 		form = AddWalletPageItemForm(data)
# 		if form.is_valid():
# 			try:
# 				form.save()
# 				messages.success(request, 'Added new CMS page item.')
# 				return redirect('edit_idecorate_page', page_id=page_id)
# 			except Exception as e:
# 				messages.error(request, 'An error has occurred.')
# 				logger.error('Error adding CMS page item: %e' %e)

# 	info['form'] = form

# 	return render_to_response('cms/iframe/add_page_item.html',info,context_instance)

# @staff_member_required
# def edit_idecorate_page_item(request, page_id, item_id):
# 	context_instance = RequestContext(request)
# 	info = {}

# 	if not WalletPage.objects.filter(status=0).filter(id=page_id).exists():
# 		messages.error(request, 'Invalid CMS page id.')
# 		return redirect('edit_idecorate_page', page_id=page_id)

# 	if not WalletPageItem.objects.filter(status=0).filter(page__id=page_id).filter(id=item_id).exists():
# 		messages.error(request, 'Invalid CMS page item id.')
# 		return redirect('edit_idecorate_page', page_id=page_id)

# 	try:
# 		item = WalletPageItem.objects.get(pk=item_id)
# 	except Exception as e:
# 		messages.error(request, 'Invalid CMS page item id.')
# 		return render_to_response('wallet_admin/iframe/closer.html',info,context_instance)

# 	form = AddWalletPageItemForm(instance=item)

# 	cancel = request.POST.get('cancel',None)
# 	if cancel:
# 		return redirect('edit_idecorate_page', page_id=page_id)

# 	if request.method == 'POST':
# 		data = request.POST.copy()
# 		data['status'] = 0
# 		data['page'] = page_id
# 		form = AddWalletPageItemForm(data,instance=item)
# 		if form.is_valid():
# 			try:
# 				form.save()
# 				messages.success(request, 'Changes saved.')
# 				return redirect('edit_idecorate_page', page_id=page_id)
# 			except Exception as e:
# 				messages.error(request, 'An error has occurred.')
# 				logger.error('Error editing CMS page item: %e' %e)

# 	info['form'] = form

# 	return render_to_response('cms/iframe/edit_page_item.html',info,context_instance)

# @staff_member_required
# def toggle_idecorate_page_item(request, page_id, item_id):
# 	context_instance = RequestContext(request)
# 	info = {}

# 	if not WalletPage.objects.filter(id=page_id).exists():
# 		messages.error(request, 'Invalid CMS page id.')
# 		return redirect('edit_idecorate_page', page_id=page_id)

# 	try:
# 		item = WalletPageItem.objects.get(pk=item_id,page__id=page_id)
# 	except Exception as e:
# 		messages.error(request, 'Invalid CMS page id.')
# 		return redirect('edit_idecorate_page', page_id=page_id)

# 	try:
# 		if item.status == 0:
# 			item.status = 1
# 			item.save()
# 			messages.success(request, 'CMS Page item deactivated.')
# 		elif item.status == 1:
# 			item.status = 0
# 			item.save()
# 			messages.success(request, 'CMS Page item activated.')
# 	except Exception as e:
# 		messages.error(request, 'Error activating/deactivating CMS page item.')
# 		return redirect('edit_idecorate_page', page_id=page_id)

# 	return redirect('edit_idecorate_page', page_id=page_id)

# @staff_member_required
# def delete_idecorate_page_item(request, page_id, item_id):
# 	context_instance = RequestContext(request)
# 	info = {}

# 	if not WalletPage.objects.filter(id=page_id).exists():
# 		messages.error(request, 'Invalid CMS page id.')
# 		return redirect('edit_idecorate_page', page_id=page_id)

# 	try:
# 		item = WalletPageItem.objects.get(pk=item_id,page__id=page_id)
# 	except Exception as e:
# 		messages.error(request, 'Invalid CMS page id.')
# 		return redirect('edit_idecorate_page', page_id=page_id)

# 	try:
# 		item.delete()
# 		messages.success(request, 'CMS page item deleted.')
# 	except Exception as e:
# 		messages.error(request, 'Error deleting CMS page item.')
# 		return redirect('edit_idecorate_page', page_id=page_id)

# 	return redirect('edit_idecorate_page', page_id=page_id)
