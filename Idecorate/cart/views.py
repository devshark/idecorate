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
from django.contrib.auth.models import User

from cart.models import Product, ProductPrice, CartTemp, GuestTableTemp, GuestTable, Contact
from cart.services import get_product, generate_unique_id, remove_from_cart_temp

import plata
#from plata.contact.models import Contact
from plata.discount.models import Discount
from plata.shop.models import Order
from plata.shop.views import Shop
from plata.shop import forms as shop_forms
from django import forms


class IdecorateCheckoutForm(shop_forms.BaseCheckoutForm):
    class Meta:
        fields = ['email'] + ['billing_%s' % f for f in Contact.ADDRESS_FIELDS] + ['shipping_%s' % f for f in Contact.ADDRESS_FIELDS]
        model = Order

    def __init__(self, *args, **kwargs):
        shop = kwargs.get('shop')
        request = kwargs.get('request')
        contact = shop.contact_from_user(request.user)

        if contact:
            initial = {}
            for f in contact.ADDRESS_FIELDS:
                initial['billing_%s' % f] = getattr(contact, f)
                kwargs['initial'] = initial

            for f in contact.ADDRESS_FIELDS:
                initial['shipping_%s' % f] = getattr(contact, f)
                kwargs['initial'] = initial

            initial['email'] = contact.user.email

        super(IdecorateCheckoutForm, self).__init__(*args, **kwargs)

        self.fields['billing_address2'] = forms.CharField(label=_("Billing Address2"), required=True)
        self.fields['shipping_address2'] = forms.CharField(label=_("Shipping Address2"), required=True)
        self.fields['billing_address'] = forms.CharField(label=_("Billing Address"), required=True)
        self.fields['shipping_address'] = forms.CharField(label=_("Shipping Address"), required=True)
        self.fields['shipping_salutation'] = forms.ChoiceField(label=_("Salutation"), choices=(('Mr','Mr'), ('Ms','Ms'), ('Mrs','Mrs')), required=True,widget=forms.Select)
        self.fields['billing_salutation'] = forms.ChoiceField(label=_("Salutation"), choices=(('Mr','Mr'), ('Ms','Ms'), ('Mrs','Mrs')), required=True,widget=forms.Select)
        self.fields['shipping_state'] = forms.ChoiceField(label=_("Shipping State"), choices=(), required=True,widget=forms.Select)
        self.fields['billing_state'] = forms.ChoiceField(label=_("Billing State"), choices=(), required=True,widget=forms.Select)

        if not contact:
            self.fields['create_account'] = forms.BooleanField(
                label=_('create account'),
                required=False, initial=True)

class IdecorateShop(Shop):

	def modify_guest_table(self, request, guests, tables, order):

		if 'cartsession' in request.session:
			sessionid = request.session.get('cartsession')
			
			if GuestTableTemp.objects.filter(sessionid=sessionid).exists():

				if GuestTable.objects.filter(order=order).exists():
					guestTable = GuestTable.objects.get(order=order)
					guestTable.guests = guests
					guestTable.tables = tables
					guestTable.save()
				else:
					guestTable = GuestTable()
					guestTable.order = order
					guestTable.guests = guests
					guestTable.tables = tables
					guestTable.save()

				self.guest_table = guestTable

	def render_checkout(self, request, context):
		context.update({'guest_table': self.guest_table})
		return self.render(request, 'plata/shop_checkout.html', self.get_context(request, context))
	
	def checkout_form(self, request, order):
		return IdecorateCheckoutForm

shop = IdecorateShop(
	contact_model=Contact,
	order_model=Order,
	discount_model=Discount,
	)

def add_to_cart_ajax(request):	
	if request.method == "POST":
		product_id = request.POST.get('prod_id')
		quantity = request.POST.get('quantity',1)
		guests = request.POST.get('guests', 1)
		tables = request.POST.get('tables', 1)
		product = get_product(product_id)
		sessionid = request.session.get('cartsession',None)
		if not sessionid:
			sessionid = generate_unique_id()
			request.session['cartsession'] = sessionid

		exists = CartTemp.objects.filter(product=product.product,sessionid=sessionid).exists()
		existsGT = GuestTableTemp.objects.filter(sessionid=sessionid).exists()		

		if not exists:
			cartTemp = CartTemp()
			cartTemp.product = product.product
			cartTemp.quantity = quantity
			cartTemp.sessionid = sessionid
			cartTemp.save()

		if not existsGT:
			guestTable = GuestTableTemp()
			guestTable.guests = guests
			guestTable.tables = tables
			guestTable.sessionid = sessionid
			guestTable.save()

		reponse_data = {}
		reponse_data['id'] = product.product.id
		reponse_data['original_image_thumbnail'] = product.product.original_image_thumbnail
		reponse_data['sku'] = product.product.sku
		reponse_data['name'] = product.product.name
		reponse_data['default_quantity'] = product.product.default_quantity
		reponse_data['price'] = product._unit_price
		reponse_data['currency'] = product.currency
		reponse_data['original_image'] = product.product.original_image
		guest_table = 'Table'
		try:
			guest_table = product.product.guest_table.name
		except:
			pass
		reponse_data['guest_table'] = guest_table
		return HttpResponse(simplejson.dumps(reponse_data), mimetype="application/json")
	else:
		return HttpResponseNotFound()

def update_cart(request):
	if request.method == "POST":
		product_id = request.POST.get('prod_id')
		quantity = request.POST.get('quantity',1)
		guests = request.POST.get('guests', 1)
		tables = request.POST.get('tables', 1)
		sessionid = request.session.get('cartsession',None)
		reponse_data = {}
		try:
			product = get_product(product_id)
			cartTemp = CartTemp.objects.get(product=product.product, sessionid=sessionid)
			cartTemp.quantity = quantity
			cartTemp.save()

			guestTable = GuestTableTemp.objects.get(sessionid=sessionid)
			guestTable.guests = guests
			guestTable.tables = tables
			guestTable.save()

		except:
			return HttpResponse(0)
		return HttpResponse(1)
	else:
		return HttpResponseNotFound()

def remove_from_cart_ajax(request):
	if request.method == "POST":		
		prod_id = int(request.POST.get('prod_id'))
		sessionid = request.session.get('cartsession',None)

		if sessionid:
			CartTemp.objects.get(sessionid=sessionid, product__id=prod_id).delete()

			if CartTemp.objects.filter(sessionid=sessionid).count() == 0:

				GuestTableTemp.objects.get(sessionid=sessionid).delete()

		return HttpResponse('ok')
	else:
		return HttpResponseNotFound()

def checkout(request):
	sessionid = request.session.get('cartsession',None)
	if not sessionid:
		sessionid = generate_unique_id()
		request.session['cartsession'] = sessionid
	cart_item = CartTemp.objects.filter(sessionid=sessionid)

	guest_table = GuestTableTemp.objects.get(sessionid=sessionid)

	if cart_item.count() > 0:
		for cart in cart_item:
			order = shop.order_from_request(request, create=True)
			order.modify_item(cart.product, absolute=cart.quantity)
			#remove_from_cart_temp(cart.id)
		shop.modify_guest_table(request, guest_table.guests, guest_table.tables, order)

	return redirect('plata_shop_checkout')