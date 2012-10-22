from django.contrib.auth.decorators import login_required
from django.shortcuts import HttpResponse, redirect, render_to_response
from django.contrib.auth import authenticate, login, logout
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.template import RequestContext
from django.utils import simplejson
from django.http import HttpResponseNotFound
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.safestring import mark_safe

from cart.models import Product, ProductPrice
from cart.services import get_product

import plata
from plata.contact.models import Contact
from plata.discount.models import Discount
from plata.shop.models import Order
from plata.shop.views import Shop

shop = Shop(
	contact_model=Contact,
	order_model=Order,
	discount_model=Discount,
	)

def add_to_cart_ajax(request):
	if request.method == "POST":
		product_id = request.POST.get('prod_id')
		quantity = request.POST.get('quantity',1)
		product = get_product(product_id)

		order = shop.order_from_request(request, create=True)
		order.modify_item(product.product, relative=quantity)

		print order

		reponse_data = {}
		reponse_data['id'] = product.product.id
		reponse_data['original_image_thumbnail'] = product.product.original_image_thumbnail
		reponse_data['sku'] = product.product.sku
		reponse_data['name'] = product.product.name
		reponse_data['default_quantity'] = product.product.default_quantity
		reponse_data['default_quantity'] = product.product.default_quantity
		reponse_data['price'] = product._unit_price
		reponse_data['currency'] = product.currency
		reponse_data['original_image'] = product.product.original_image
		reponse_data['guest_table'] = product.product.original_image
		return HttpResponse(simplejson.dumps(reponse_data), mimetype="application/json")
	else:
		return HttpResponseNotFound()

def remove_from_cart_ajax(request):
	if request.method == "POST":		
		return HttpResponse(200)
	else:
		return HttpResponseNotFound()