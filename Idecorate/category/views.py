from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import HttpResponse, redirect, render_to_response
from django.contrib.auth import authenticate, login, logout
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.core.urlresolvers import reverse

from admin.models import LoginLog
from datetime import datetime, timedelta
from django.template import RequestContext
from forms import CategoryForm, CategoryThumbnailForm
from services import new_category, category_edit, delete_category, update_order, generate_admin_dropdown_category, parent_is_my_sub,\
validate_thumbnail, manage_category_thumbnail, category_thumbnails, clear_temp

from category.models import Categories

@staff_member_required
def category(request, cat_id=None):
	info = {}
	parent = None
	info['method'] = 'Add'
	info['heade_title'] = 'Add New Category'
	
	form = CategoryForm()		

	if request.method == 'POST':
		form = CategoryForm(request.POST)			

		if form.is_valid():
			data = form.cleaned_data
			res = new_category(data)
			messages.success(request, _('New Category saved.'))
			return redirect('category')

	categories = Categories.objects.filter(parent__id=None, deleted=0).order_by('order')
	info['form'] = form
	info['categories'] = categories
	return render_to_response('admin/category.html', info, RequestContext(request))

@staff_member_required
def edit_category(request, cat_id=None):
	info = {}
	parent = None
	info['method'] = 'Add'
	info['heade_title'] = 'Add New Category'
	
	msg = 'Edit Category saved.'
	parent_name = '---- Parent ----'
	info['method'] = 'Save'
	info['heade_title'] = 'Edit Category'
	try:
		cat = Categories.objects.get(id=cat_id)		
		try:
			parent = cat.parent.id
			parent_name = cat.parent.name
		except:
			pass
		info['cat'] = cat		
		info['parent'] = parent_name

		thumb_id = None
		cat_thumb = category_thumbnails(cid=cat.id)
		if cat_thumb:
			thumb_id = cat_thumb.id
		
		form = CategoryForm(initial={'name':cat.name,'parent':parent, 'id':cat.id, 'thumbnail': thumb_id })
	except Exception as e:
		return redirect('category')

	if request.method == 'POST':
		form = CategoryForm(request.POST, request.FILES)
		if form.is_valid():
			data = form.cleaned_data
			if parent_is_my_sub(data['id'],data['parent']):
				messages.error(request, _('Cannot assign as parent that is a sub category. Please try again.'))
			else:
				res = category_edit(data)
				if res:
					messages.success(request, _(msg))
				else:
					messages.error(request, _('Edit category failed. Please try again.'))
			return redirect('category')				

	categories = Categories.objects.filter(parent__id=None, deleted=0).order_by('order')
	info['form'] = form
	info['categories'] = categories
	return render_to_response('admin/category.html', info, RequestContext(request))

@staff_member_required
def remove_category(request):
	if request.method == 'POST':
		cat_id = request.POST['cat_id']
		res = delete_category(cat_id)
		tags = generate_admin_dropdown_category()
		if res:			
			return HttpResponse(tags)
		else:
			return HttpResponse('0')

@staff_member_required
def order_category(request):
	if request.method == 'POST':
		cats = request.POST.getlist('cat[]')			
		for cat in cats:
			splited = cat.split(':')
			cid = int(splited[0])
			order = int(splited[1])
			parent = None
			if splited[2] != 'None':
				parent = int(splited[2])
			data = {}
			data['id'] = cid
			data['order'] = order
			data['parent'] = parent
			
			update_order(data)

		tags = generate_admin_dropdown_category()

		return HttpResponse(tags)
	else:
		return HttpResponse('0')

@staff_member_required
def category_thumbnail(request):
	info = {}

	created_temp = request.session.get('TEMP_CAT_ID',None)
	if created_temp:
		clear_temp(created_temp)
		del request.session['TEMP_CAT_ID']

	form = CategoryThumbnailForm()

	if request.method == "POST":		
		thumbnail = request.FILES['thumbnail']
		res = validate_thumbnail(thumbnail)
		if res['error']:
			messages.error(request, res['msg'])
		else:
			data = {}
			data['id'] = request.POST['id']
			data['thumbnail'] = thumbnail
			cat_thumb = manage_category_thumbnail(data)
			request.session['TEMP_CAT_ID'] = cat_thumb.id
			info['cat_thumb'] = cat_thumb

	info['form'] = form
	return render_to_response('admin/iframe/category_thumbnail.html', info, RequestContext(request))

@staff_member_required
def category_thumbnail_view(request, ctid=None):
	info = {}

	created_temp = request.session.get('TEMP_CAT_ID',None)
	if created_temp:
		clear_temp(created_temp)
		del request.session['TEMP_CAT_ID']
	
	cat_thumb = category_thumbnails(ctid=ctid)
	if not cat_thumb:
		return redirect('category_thumbnail')

	form = CategoryThumbnailForm()

	if request.method == "POST":		
		thumbnail = request.FILES['thumbnail']
		res = validate_thumbnail(thumbnail)
		if res['error']:
			messages.error(request, res['msg'])
		else:
			data = {}
			data['id'] = request.POST['id']
			data['thumbnail'] = thumbnail
			cat_thumb = manage_category_thumbnail(data)
			request.session['TEMP_CAT_ID'] = cat_thumb.id
			info['cat_thumb'] = cat_thumb

	info['form'] = form
	info['cat_thumb'] = cat_thumb
	return render_to_response('admin/iframe/category_thumbnail.html', info, RequestContext(request))