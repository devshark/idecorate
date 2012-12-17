from django.core.files.uploadhandler import FileUploadHandler, UploadFileException
from django.shortcuts import HttpResponse, redirect, render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson
import os
from django.conf import settings
from cart.services import generate_unique_id
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _
from django.template import RequestContext
from embellishments.forms import SaveTemplateForm
from admin.services import save_template, getTemplateItems
from django.utils import simplejson
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core import serializers

# class who handles the upload
class ProgressUploadHandler(FileUploadHandler):
	"""
	Download the file and store progression in the session
	"""
	def __init__(self, request=None, outPath="/tmp", filename=None):
		super(ProgressUploadHandler, self).__init__(request)
		self.progress_id = None
		self.cache_key = None
		self.request = request
		self.outPath = outPath
		self.destination = None
		self.filename = filename

	def handle_raw_input(self, input_data, META, content_length, boundary, encoding=None):
		self.content_length = content_length
		if 'X-Progress-ID' in self.request.GET :
			self.progress_id = self.request.GET['X-Progress-ID']
		elif 'X-Progress-ID' in self.request.META:
			self.progress_id = self.request.META['X-Progress-ID']
		if self.progress_id:
			self.cache_key = self.progress_id
			self.request.session['upload_progress_%s' % self.cache_key] =  {
				'length': self.content_length,
				'uploaded' : 0
			}

	def new_file(self, field_name, file_name, content_type, content_length, charset=None):
		ext = file_name.split('.')
		self.filename = '%s.%s' % (self.filename,ext[1])
		self.outPath = os.path.join(self.outPath, self.filename)
		self.destination = open(self.outPath, 'wb+')		
		pass

	def receive_data_chunk(self, raw_data, start):
		data = self.request.session['upload_progress_%s' % self.cache_key]
		data['uploaded'] += self.chunk_size
		self.request.session['upload_progress_%s' % self.cache_key] = data
		self.request.session.save()
		self.destination.write( raw_data)
		# data wont be passed to any other handler
		return None

	def file_complete(self, file_size):
		pass

	def upload_complete(self):
		try:
			self.destination.close()
		except:
			pass
		del self.request.session['upload_progress_%s' % self.cache_key]


# view that display the current upload progress (json)
def upload_embellishment_progress(request):
	"""
	Return JSON object with information about the progress of an upload.
	"""
	progress_id = ''
	if 'X-Progress-ID' in request.GET:
		progress_id = request.GET['X-Progress-ID']
	elif 'X-Progress-ID' in request.META:
		progress_id = request.META['X-Progress-ID']
	if progress_id:
		cache_key = "%s" % (progress_id)
		data = request.session.get('upload_progress_%s' % cache_key, None)
		return HttpResponse(simplejson.dumps(data))
	else:
		return HttpResponseServerError('Server Error: You must provide X-Progress-ID header or query param.')

@csrf_exempt
def upload_embellishment(request):
	return render_to_response('interface/upload.html')

# view thath launch the upload process
@csrf_exempt
def upload_embellishment_action(request):
	if request.method == 'POST':
		outPath = "%s%s" % (settings.MEDIA_ROOT, "embellishments/images/")
		filename = generate_unique_id(10)
		if not os.path.exists(outPath):
			os.makedirs(outPath)
		up = ProgressUploadHandler(request, outPath, filename)
		request.upload_handlers.insert(0, up)

		upload_file = request.FILES.get('picture', None)
		content_type = upload_file.content_type.split('/')[0]
		uploaded = request.read
		fileSize = int(uploaded.im_self.META["CONTENT_LENGTH"])
		
		if content_type in settings.CONTENT_TYPES:		
			if fileSize > settings.MAX_UPLOAD_EMBELLISHMENT_IMAGE_SIZE:
				err =  _('Please keep filesize under %s. Current filesize %s') % (filesizeformat(settings.MAX_UPLOAD_EMBELLISHMENT_IMAGE_SIZE), filesizeformat(fileSize))
				res = 'f1|%s' % err.encode('utf-8')
				return HttpResponse(res)
			else:					
				return HttpResponse('%s|%s'%('s',up.filename))
		else:
			err = _('File type is not supported')
			res = 'f2|%s' % err.encode('utf-8')
			return HttpResponse(res)

@csrf_exempt
def template_upload_embellishment_action(request):
	if request.method == 'POST':
		outPath = "%s%s" % (settings.MEDIA_ROOT, "embellishments/template/")
		filename = generate_unique_id(10)
		if not os.path.exists(outPath):
			os.makedirs(outPath)
		up = ProgressUploadHandler(request, outPath, filename)
		request.upload_handlers.insert(0, up)

		upload_file = request.FILES.get('picture', None)
		content_type = upload_file.content_type.split('/')[0]
		uploaded = request.read
		fileSize = int(uploaded.im_self.META["CONTENT_LENGTH"])
		
		if content_type in settings.CONTENT_TYPES:		
			if fileSize > settings.MAX_UPLOAD_EMBELLISHMENT_IMAGE_SIZE:
				err =  _('Please keep filesize under %s. Current filesize %s') % (filesizeformat(settings.MAX_UPLOAD_EMBELLISHMENT_IMAGE_SIZE), filesizeformat(fileSize))
				res = 'f1|%s' % err.encode('utf-8')
				return HttpResponse(res)
			else:					
				return HttpResponse('%s|%s'%('s',up.filename))
		else:
			err = _('File type is not supported')
			res = 'f2|%s' % err.encode('utf-8')
			return HttpResponse(res)

def save_styleboard_template(request):
	info = {}	
	form = SaveTemplateForm()
	if request.method=="POST":
		form = SaveTemplateForm(request.POST)
		if form.is_valid():
			data = form.cleaned_data
			res = save_template(data)
			if res:
				return render_to_response('embellishments/success.html', info)
			else:
				messages.warning(request, _('An error occured when saving the template. Please try again.'))

	info['form'] = form

	return render_to_response('embellishments/save_styleboard_template.html', info, RequestContext(request))

def get_template_items(request):
	if request.method == "POST":
		template_items = getTemplateItems()
		offset = request.GET.get('offset',25)

		paginator = Paginator(template_items, offset)
		page = request.GET.get('page')
		try:
			templates = paginator.page(page)
		except PageNotAnInteger:
			templates = paginator.page(1)
		except EmptyPage:
			templates = paginator.page(paginator.num_pages)

		reponse_data = {}
		json_data = serializers.serialize("json", templates, fields=('id','name','description','browser'))
		reponse_data['data'] = json_data
		reponse_data['page_number'] = templates.number
		reponse_data['num_pages'] = templates.paginator.num_pages
		reponse_data['product_counts'] = template_items.count()

		return HttpResponse(simplejson.dumps(reponse_data), mimetype="application/json")
	else:
		return HttpResponseServerError()