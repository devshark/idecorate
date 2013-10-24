# Create your views here.
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance
import math
import random
from django.core import serializers
from django.utils import simplejson
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context, RequestContext
from django.shortcuts import HttpResponse, render_to_response, render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.conf import settings

from common.services import render_to_json
from category.models import Categories
from embellishments.models import StyleboardTemplateItems
from cart.models import Product, ProductPrice, ProductDetails, ProductAlternateImage
from admin.models import TextFonts, Embellishments, EmbellishmentsType

def create(request, category_id=None, styleboard_id=None): 

    info = {}

    info['category_id'] =  category_id if category_id is not None else 0
    info['styleboard_id'] =  styleboard_id if styleboard_id is not None else 0

    return render_to_response('styleboard/styleboard.html', info,RequestContext(request))

@csrf_exempt
def get_categories(request):

    data = {}

    if request.method == "POST":

        categories = Categories.objects.filter(deleted=False)
        data['categories'] = serializers.serialize("json", categories, fields=('id','name','thumbnail','parent'))

        return render_to_json(request, data)

@csrf_exempt
def get_products(request):

    data = {}

    if request.method == "POST":

        category_id = int(request.POST.get('category_id'))
        product_page = int(request.POST.get('product_page', 0))
        product_page_offset = product_page*settings.STYLEBOARD_GET_PRODUCTS_NUM_RECORDS
        q = ~Q(product__categories__id=category_id)  if category_id == 0 else Q(product__categories__id=category_id)

        product_keyword = request.POST.get('product_keyword')
        if product_keyword != '':
            search_q = Q(product__name__icontains=product_keyword)
            search_q.add(Q(product__description__icontains=product_keyword), Q.OR)
            search_q.add(Q(product__categories__name__icontains=product_keyword), Q.OR)
            q.add(search_q, Q.AND)

        product = ProductPrice.objects.filter(q, product__is_active=True, product__is_deleted=False) \
                                                .distinct() \
                                                [product_page_offset:settings.STYLEBOARD_GET_PRODUCTS_NUM_RECORDS+product_page_offset]

        data['products'] = serializers.serialize("json", product, use_natural_keys=True, fields=('id','product','_unit_price'))
        data['total_page'] = math.ceil(ProductPrice.objects.filter(q, product__is_active=True, product__is_deleted=False).count()/settings.STYLEBOARD_GET_PRODUCTS_NUM_RECORDS)
        
        return render_to_json(request, data)


def get_product_info(request, product_id=0):

    product = get_object_or_404(Product, pk=int(product_id))
    product_details = ProductDetails.objects.get(product=product)
    suggested_products = product.suggestedproduct_set.all()
    alternate_images = product.productalternateimage_set.all()
    context = {
        'product' : product,
        'suggested_products' : suggested_products,
        'alternate_images' : alternate_images,
        'product_details' : product_details,
    }

    return render(request, 'styleboard/product_info.html', context)


def zoom_product_image(request, object_id, size, is_product):

    dimension = int(size), int(size)
    imageObject = None

    try:
        if bool(int(is_product)): 
            imageObject = Product.objects.get(pk=int(object_id))
        else:
            imageObject = ProductAlternateImage.objects.get(pk=int(object_id))
    except Exception as e:
        print "cant parse object. error: '%s'" % e

    if imageObject is not None:
        try:
            image = Image.open("%s%s%s" % (settings.MEDIA_ROOT, "products/", imageObject.original_image))
            image.load()
            wpercent = (dimension[0]/float(image.size[0]))
            hsize = int((float(image.size[1])*float(wpercent)))
            image = image.resize((dimension[0],hsize), Image.ANTIALIAS)
            image.thumbnail(dimension,Image.ANTIALIAS)
            bgImg = Image.new("RGB", dimension, (255, 255, 255))
            bgImg.paste(image,((dimension[0] - image.size[0]) / 2, (dimension[1] - image.size[1]) / 2))
        except IOError:
            print "cannot create thumbnail for '%s'" % imageObject.original_image

    response = HttpResponse(mimetype="image/jpg")
    bgImg.save(response, 'JPEG')

    return response

@csrf_exempt
def get_embellishment_categories(request):

    data = {}
    embellishment_categories = EmbellishmentsType.objects.all()
    data['embellishment_categories'] = serializers.serialize("json", embellishment_categories, fields=('id','name','title'))

    return render_to_json(request, data)


@csrf_exempt
def get_embellishments(request):

    data = {}
    category_id = int(request.POST.get('embellishment_category_id',0))
    embellishment_page = int(request.POST.get('embellishment_page', 0))
    embellishment_page_offset = embellishment_page*settings.STYLEBOARD_GET_PRODUCTS_NUM_RECORDS
    q = ~Q(e_type=category_id)  if category_id == 0 else Q(e_type=category_id)
    embellishment = Embellishments.objects.filter(q, is_active=True, is_deleted=False)[embellishment_page_offset:settings.STYLEBOARD_GET_PRODUCTS_NUM_RECORDS+embellishment_page_offset]
    total_page = Embellishments.objects.filter(q, is_active=True, is_deleted=False).count()
    textFonts = {}
    if category_id == 0 or category_id == 6:
        textFonts = TextFonts.objects.filter(is_deleted=False)[embellishment_page_offset:settings.STYLEBOARD_GET_PRODUCTS_NUM_RECORDS+embellishment_page_offset]
        total_page += TextFonts.objects.filter(is_deleted=False).count()
    combined = list(embellishment)+list(textFonts)
    random.shuffle(combined)
    data['embellishments'] = serializers.serialize("json", combined, fields=('id','description','e_type','image','image_thumb', 'font'))
    data['total_page'] = math.ceil(total_page/settings.STYLEBOARD_GET_PRODUCTS_NUM_RECORDS)
        
    return render_to_json(request, data)

@csrf_exempt
def get_templates(request):

    data = {}
    template_page = int(request.POST.get('template_page', 0))
    template_page_offset = template_page*settings.STYLEBOARD_GET_PRODUCTS_NUM_RECORDS
    templates = StyleboardTemplateItems.objects.filter(deleted=0)[template_page_offset:settings.STYLEBOARD_GET_PRODUCTS_NUM_RECORDS+template_page_offset]
    data['templates'] = serializers.serialize("json", templates, fields=('id','description','name'))
    data['total_page'] = math.ceil(StyleboardTemplateItems.objects.filter(deleted=0).count()/settings.STYLEBOARD_GET_PRODUCTS_NUM_RECORDS)
    
    return render_to_json(request, data)


def crop(request):

    info = {}
    filename = request.GET.get('filename');
    info['coordinates'] = ""
    try:
        Image.open("%s%s%s" % (settings.MEDIA_ROOT, "products/", filename));
    except:
        files = filename.split('/')
        file_data = files[3].split('&')
        coordinates = file_data[1].split('=')[1]
        filename = file_data[2].split('=')[1]
        info['coordinates'] = coordinates

    info['filename'] = filename
    return render_to_response('styleboard/crop.html', info,RequestContext(request))


def crop_image(request):

    filename = request.GET.get('filename')

    img = Image.open("%s%s%s" % (settings.MEDIA_ROOT, "products/", filename))
    back = Image.new('RGBA', (400,400), (255, 255, 255, 0))
    back.paste(img, ((400 - img.size[0]) / 2, (400 - img.size[1]) /2 ))

    poly = Image.new('RGBA', (settings.PRODUCT_WIDTH,settings.PRODUCT_HEIGHT), (255, 255, 255, 0))
    pdraw = ImageDraw.Draw(poly)

    dimensionList = []
    splittedPosts = request.GET.get('coordinates').split(',')

    for splittedPost in splittedPosts:
        spl = splittedPost.split(':')
        dimensionList.append((float(spl[0]),float(spl[1])))

    pdraw.polygon(dimensionList,fill=(255,255,255,255),outline=(255,255,255,255))
        
    poly.paste(back,mask=poly)
    response = HttpResponse(mimetype="image/png")

    newImg = poly.crop(((400 - img.size[0]) / 2, (400 - img.size[1]) /2 , ((400 - img.size[0]) / 2) + img.size[0], ((400 - img.size[1]) / 2) + img.size[1]))
    newImg.save(response, "PNG")
    return response


@csrf_exempt
def sidebar_items(request):

    data = {}

    if request.method == "POST":
        category_id = request.POST.get('categoryId', None)
        category_id = None if int(category_id) == 0 else int(category_id)
        breadcrumb = [];

        if category_id is not None:
            breadcrumb = get_parent_categories(category_id)

            try:
                currentCategory = Categories.objects.get(id=category_id, deleted=False)
                breadcrumb.append([currentCategory.id,currentCategory.name])
            except Categories.DoesNotExist:
                pass
            
        data['breadcrumb'] = breadcrumb
        categories = Categories.objects.filter(parent__id=category_id, deleted=False);

        if categories.count() > 0:
            categories = categories.order_by('order')
            data['categories'] = serializers.serialize("json", categories, fields=('id','name','thumbnail','parent'))
        else:
            products = Product.objects.filter(categories__id=category_id, is_active=True, is_deleted=False)
            products = products.order_by('ordering')
            data['products'] = serializers.serialize("json", products)
        
    return  HttpResponse(simplejson.dumps(data), mimetype="application/json")

def get_parent_categories(cat_id, data=None):
 
    cat_id = int(cat_id)
    data = [] if data is None else data

    try:
        category = Categories.objects.get(id=cat_id, deleted=False)

        if category.parent is not None:
            parentCategory = Categories.objects.get(id=int(category.parent.id), deleted=False)
            data.append([parentCategory.id,parentCategory.name])
            data = get_parent_categories(parentCategory.id, data)

    except Categories.DoesNotExist:
        pass

    return data
