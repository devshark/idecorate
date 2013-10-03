# Create your views here.
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance
import math
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
from cart.models import Product, ProductPrice, ProductDetails, ProductAlternateImage

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
