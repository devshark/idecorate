# Create your views here.
from django.core import serializers
from django.utils import simplejson
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context, RequestContext
from django.shortcuts import HttpResponse, render_to_response
from django.views.decorators.csrf import csrf_exempt

from common.services import render_to_json
from category.models import Categories
from cart.models import Product, ProductPrice
from django.conf import settings

def create(request, category_id=None, styleboard_id=None): 

    info = {}

    info['category_id'] =  category_id if category_id is not None else 0
    info['styleboard_id'] =  styleboard_id if styleboard_id is not None else 0

    return render_to_response('styleboard/styleboard.html', info,RequestContext(request))

@csrf_exempt
def get_all_categories(request):

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

        if int(category_id) == 0:

            if product_page:
                product = ProductPrice.objects.filter(product__is_active=True, product__is_deleted=False)[product_page_offset:settings.STYLEBOARD_GET_PRODUCTS_NUM_RECORDS+product_page_offset]
            else:
                product = ProductPrice.objects.filter(product__is_active=True, product__is_deleted=False)[:settings.STYLEBOARD_GET_PRODUCTS_NUM_RECORDS]

        else:
            if product_page:
                product = ProductPrice.objects.filter(product__categories__id=category_id, product__is_active=True, product__is_deleted=False)[product_page_offset:settings.STYLEBOARD_GET_PRODUCTS_NUM_RECORDS+product_page_offset]
            else:
                product = ProductPrice.objects.filter(product__categories__id=category_id, product__is_active=True, product__is_deleted=False)[:settings.STYLEBOARD_GET_PRODUCTS_NUM_RECORDS]

       
        data['products'] = serializers.serialize("json", product, use_natural_keys=True, fields=('id','product','_unit_price'))
        
        return render_to_json(request, data)


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