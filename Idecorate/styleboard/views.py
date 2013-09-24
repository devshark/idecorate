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
from cart.models import Product

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
def get_all_products(request):

    if request.method == "POST":

        products = Product.objects.filter(is_active=True, is_deleted=False)
        data['categories'] = serializers.serialize("json", products, fields=('id','name','thumbnail','parent'))
        return render_to_json(request, data)

@csrf_exempt
def get_product_by_category(request):

    if request.method == "POST":
        return  HttpResponse(simplejson.dumps(Product.objects.filter(is_active=True, is_deleted=False)), mimetype="application/json")

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