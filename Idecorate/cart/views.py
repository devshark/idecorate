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
import re

from customer.services import get_styleboard_cart_item, get_user_styleboard

class IdecorateCheckoutForm(shop_forms.BaseCheckoutForm):
    class Meta:
        fields = ['email'] + ['billing_%s' % f for f in Contact.ADDRESS_FIELDS] + ['shipping_%s' % f for f in Contact.ADDRESS_FIELDS] + ['shipping_same_as_billing']
        model = Order

    def __init__(self, *args, **kwargs):
        shop = kwargs.get('shop')
        request = kwargs.get('request')
        contact = shop.contact_from_user(request.user)

        states = tuple(sorted((('Australian Capital Territory','Australian Capital Territory'), ('New South Wales','New South Wales'), ('Victoria','Victoria'), ('Queensland','Queensland'), ('South Australia','South Australia'), ('Western Australia','Western Australia'), ('Tasmania','Tasmania'), ('Northern Territory','Northern Territory'))))
        cities = tuple(sorted((
        	('Canberra','Canberra'),('Albury','Albury'), ('Armidale','Armidale'), ('Bathurst','Bathurst'), ('Blue Mountains','Blue Mountains'), ('Broken Hill','Broken Hill'), ('Campbelltown','Campbelltown'), ('Cessnock','Cessnock'), ('Dubbo','Dubbo'), ('Goulburn','Goulburn'), ('Grafton','Grafton'), ('Lithgow','Lithgow'), ('Liverpool','Liverpool'), ('Newcastle','Newcastle'), ('Orange','Orange'), ('Parramatta','Parramatta'), ('Penrith','Penrith'), ('Queanbeyan','Queanbeyan'), ('Sydney','Sydney'), 
        	('Tamworth','Tamworth'), ('Wagga','Wagga'),('City of Bankstown','City of Bankstown'), ('City of Blacktown','City of Blacktown'), ('City of Botany Bay','City of Botany Bay'), ('City of Canada Bay','City of Canada Bay'), ('City of Canterbury','City of Canterbury'), ('City of Coffs Harbour','City of Coff Harbour'), ('City of Fairfield','City of Fairfield'), ('City of Gosford','City of Gosford'), ('City of Greater Taree','City of Greater Taree'), ('City of Griffith','City of Griffith'), 
        	('City of Hawkesbury','City of Hawkesbury'), ('City of Holroyd','City of Holroyd'), ('City of Hurtsville','City of Hurtsville'), ('City of Lake Macquarie','City of Lake Macquarie'), ('City of Lismore','City of Lismore'), ('City of Lithgow','City of Lithgow'), ('City of Maitland','City of Maitland'), ('City of Randwick','City of Randwick'), ('City of Rockdale','City of Rockdale'), ('City of Ryde','City of Ryde'), ('City of Shellharbour','City of Shellharbour'), ('City 		f Shoalhaven','City of Shoalhaven'), 
        	('City of Willoughby','City of Willoughby'), ('Darwin','Darwin'), ('Palmerston','Palmerston'), ('Brisbane','Brisbane'), ('Bundaberg','Bundaberg'), ('Cairns','Cairns'), ('Caloundra','Caloundra'), ('Gladstone','Gladstone'), ('Gold Coast','Gold Coast'), ('Gympie','Gympie'), ('Hervey Bay','Hervey Bay'), ('Ipswich','Ipswich'), ('Logan City','Logan City'), ('Mackay','Mackay'), ('Maryborough','Maryborough'), ('Mount Isa','Mount Isa'), ('Rockhampton','Rockhampton'), ('Sunshine Coast','Sunshine Coast'), ('Surfers Paradise','Surfers Paradise'), 
        	('Toowoomba','Toowoomba'), ('Townsville','Townsville'), ('Charters Towers','Charters Towers'), ('Redcliffe City','Redcliffe City'), ('Redland City','Redland City'), ('Thuringova','Thuringova'), ('Warwick','Warwick'), ('Adelaide','Adelaide'), ('Mount Barker','Mount Barker'), ('Mount Gambier','Mount Gambier'), ('Murray Bridge','Murray Bridge'), ('Port Adelaide','Port Adelaide'), ('Port Augusta','Port Augusta'), ('Port Pirie','Port Pirie'), ('Port Lincoln','Port Lincoln'), ('Victor Harbor','Victor Harbor'), ('Whyalla','Whyalla'), 
        	('Hobart','Hobart'), ('Burnie','Burnie'), ('Devonport','Devonport'), ('Launceston','Launceston'), ('Melbourne','Melbourne'), ('Ararat','Ararat'), ('Bairnsdale','Bairnsdale'), ('Benalla','Benalla'), ('Ballarat','Ballarat'), ('Bendigo','Bendigo'), ('Dandenong','Dandenong'), ('Frankston','Frankston'), ('Geelong','Geelong'), ('Hamilton','Hamilton'), ('Horsham','Horsham'), ('Melton','Melton'), ('Moe','Moe'), ('Morwell','Morwell'), ('Mildura','Mildura'), ('Mildura','Mildura'), ('Sale','Sale'), ('Shepparton','Shepparton'), ('Swan Hill','Swan Hill'), 
        	('Traralgon','Traralgon'), ('Wangaratta','Wangaratta'), ('Warrnambool','Warrnambool'), ('Wodonga','Wodonga'), ('Perth','Perth'), ('Albany','Albany'), ('Bunbury','Bunbury'), ('Busselton','Busselton'), ('Fremantle','Fremantle'), ('Geraldton','Geraldton'), ('Joondalup','Joondalup'), ('Kalgoorlie','Kalgoorlie'), ('Mandurah','Mandurah'), ('Rockingham','Rockingham'), ('City of Armadale','City of Armadale'), ('City of Bayswater','City of Bayswater'), ('City of Canning','City of Canning'), ('City of Cockburn','City of Cockburn'), ('City of Gosnells','City of Gosnells'), 
        	('City of Melville','City of Melville'), ('City of Nedlands','City of Nedlands'), ('City of South Perth','City of South Perth'), ('City of Stirling','City of Stirling'), ('City of Subiaco','City of Subiaco'), ('City of Swan','City of Swan'), ('City of Wanneroo','City of Wanneroo')
        )))

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

        self.fields['shipping_address2'] = forms.CharField(max_length=200, label=_("Shipping Address2"), required=False)
        self.fields['shipping_address'] = forms.CharField(max_length=200, label=_("Shipping Address"), required=True, error_messages={'required':_('Delivery Address is a required field.')})
        self.fields['shipping_salutation'] = forms.ChoiceField(label=_("Salutation"), choices=(('Mr','Mr'), ('Ms','Ms'), ('Mrs','Mrs')), required=False,widget=forms.Select, error_messages={'required':_('Salutation is a required field.')})
        self.fields['billing_salutation'] = forms.ChoiceField(label=_("Salutation"), choices=(('Mr','Mr'), ('Ms','Ms'), ('Mrs','Mrs')), required=True,widget=forms.Select)
        self.fields['shipping_state'] = forms.ChoiceField(label=_("Shipping State"), choices=states, required=True,widget=forms.Select)
        self.fields['shipping_city'] = forms.ChoiceField(label=_("Shipping City"), choices=cities, required=True,widget=forms.Select)
        self.fields['shipping_same_as_billing'] = forms.BooleanField(initial=True,label=_("Same as Billing"),required=False)
        self.fields['shipping_date'] = forms.CharField(label=_("Shipping Date"), required=True, error_messages={'required':_('Delivery Date is a required field.')})
        self.fields['shipping_zip_code'] = forms.CharField(label=_("Shipping Zip Code"), required=True, error_messages={'required':_('Delivery Zip Code is a required field.')})        
        self.fields['email'] = forms.EmailField(label=_("Email"), required=True, error_messages={'invalid':_('Enter a valid Email in Personal Information.'),'required':_('Email in Personal Information is a required field.')})
        self.fields['billing_last_name'] = forms.CharField(max_length=100, label=_("Billing Last Name"), required=True, error_messages={'required':_('Last Name is a required field.')})
        self.fields['billing_first_name'] = forms.CharField(max_length=100, label=_("Billing First Name"), required=True, error_messages={'required':_('First Name is a required field.')})
        self.fields['payment_method'] = forms.ChoiceField(label=_("Payment Method"), choices=(('Paypal','Paypal'),('Visa_Mastercard','Visa/Mastercard'),('American_Express','American Express'),), required=True,widget=forms.RadioSelect, error_messages={'required':_('Payment Method is a required field.')})

        shipping_same_as_billing = request.POST.get('order-shipping_same_as_billing')
        
        if shipping_same_as_billing:
	        self.fields['billing_zip_code'] = forms.CharField(label=_("Billing Zip Code"), required=False, error_messages={'required':_('Billing Zip Code is a required field.')})
	        self.fields['billing_address'] = forms.CharField(max_length=200, label=_("Billing Address"), required=False, error_messages={'required':_('Billing Address is a required field.')})
	        self.fields['billing_address2'] = forms.CharField(max_length=200, label=_("Billing Address2"), required=False)
	        self.fields['billing_state'] = forms.ChoiceField(label=_("Billing State"), choices=states, required=False,widget=forms.Select)
	        self.fields['billing_city'] = forms.ChoiceField(label=_("Billing City"), choices=cities, required=False,widget=forms.Select)
        else:
	        self.fields['billing_zip_code'] = forms.CharField(label=_("Billing Zip Code"), required=True, error_messages={'required':_('Billing Zip Code is a required field.')})
	        self.fields['billing_address'] = forms.CharField(max_length=200, label=_("Billing Address"), required=True, error_messages={'required':_('Billing Address is a required field.')})
	        self.fields['billing_address2'] = forms.CharField(max_length=200, label=_("Billing Address2"), required=False)
	        self.fields['billing_state'] = forms.ChoiceField(label=_("Billing State"), choices=states, required=True,widget=forms.Select)
	        self.fields['billing_city'] = forms.ChoiceField(label=_("Billing City"), choices=cities, required=True,widget=forms.Select)

        if not contact:
            self.fields['create_account'] = forms.BooleanField(
                label=_('create account'),
                required=False, initial=True)

    def clean_shipping_zip_code(self):

		shipping_zip_code = self.cleaned_data['shipping_zip_code']

		if not re.search("(^[0-9]{1,}$)",shipping_zip_code,re.IGNORECASE):
			raise forms.ValidationError(_("Invalid Delivery Postal Code"))			

		return shipping_zip_code

    def clean_billing_zip_code(self):

		billing_zip_code = self.cleaned_data['billing_zip_code']
		if self.fields['billing_zip_code'].required: 
			if not re.search("(^[0-9]{1,}$)",billing_zip_code,re.IGNORECASE):
				raise forms.ValidationError(_("Invalid Billing Postal Code"))			

		return billing_zip_code

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

		else:
			if GuestTable.objects.filter(order=order).exists():
				guestTable = GuestTable.objects.get(order=order)
				guestTable.guests = styleboard.item_guest
				guestTable.tables = styleboard.item_tables
				guestTable.save()
			else:
				guestTable = GuestTable()
				guestTable.order = order
				guestTable.guests = styleboard.item_guest
				guestTable.tables = styleboard.item_tables
				guestTable.save()

			self.guest_table = guestTable

	def render_checkout(self, request, context):
		context.update({'guest_table': self.guest_table})
		return self.render(request, 'plata/shop_checkout.html', self.get_context(request, context))
	
	def checkout_form(self, request, order):
		#print request.method
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

def remove_all_cart_ajax(request):
	if request.method == "POST":		
		sessionid = request.session.get('cartsession',None)

		if sessionid:
			CartTemp.objects.filter(sessionid=sessionid).delete()
			GuestTableTemp.objects.filter(sessionid=sessionid).delete()

		return HttpResponse('ok')

	else:
		return HttpResponseNotFound()

def checkout(request):
	sessionid = request.session.get('cartsession',None)
	if not sessionid:
		sessionid = generate_unique_id()
		request.session['cartsession'] = sessionid
	cart_item = CartTemp.objects.filter(sessionid=sessionid).order_by('-id')

	guest_table = GuestTableTemp.objects.get(sessionid=sessionid)

	order = shop.order_from_request(request, create=True)
	order.items.filter().delete()

	if cart_item.count() > 0:
		for cart in cart_item:
			order.modify_item(cart.product, absolute=cart.quantity)
			#remove_from_cart_temp(cart.id)
		shop.modify_guest_table(request, guest_table.guests, guest_table.tables, order)

	return redirect('plata_shop_checkout')

def checkout_from_view_styleboard(request):
	if request.method=='POST':
		styleboard_item_id = request.POST['sid']
		customer_styleboard = get_user_styleboard(None,styleboard_item_id)
		styleboard = customer_styleboard.styleboard_item
		cart_items = get_styleboard_cart_item(styleboard)

		order = shop.order_from_request(request, create=True)

		if cart_items.count() > 0:
			for cart in cart_items:
				order.modify_item(cart.product, absolute=cart.quantity)

			shop.modify_guest_table(request, styleboard.item_guest, styleboard.item_tables, order)

		return redirect('plata_shop_checkout')
	else:
		return redirect('styleboard')