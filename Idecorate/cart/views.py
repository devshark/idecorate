from django.contrib.auth.decorators import login_required
from django.shortcuts import HttpResponse, redirect, render_to_response
from django.contrib.auth import authenticate, login, logout
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.http import HttpResponseNotFound
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User

from cart.models import Product, ProductPrice, CartTemp, GuestTableTemp, GuestTable, Contact, OrderStyleboard, OrderData
from cart.services import get_product, generate_unique_id, remove_from_cart_temp, add_to_cart

import plata
#from plata.contact.models import Contact
from plata.discount.models import Discount
from plata.shop.models import Order, OrderPayment, OrderItem
from plata.shop.views import Shop
from plata.shop import signals
from plata.shop.processors import ProcessorBase
from django import forms
import re
import urllib
import urlparse
import ast

from customer.services import get_styleboard_cart_item, get_user_styleboard
from customer.models import CustomerProfile
from idecorate_settings.models import IdecorateSettings
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from common.services import ss_direct, send_email_set_pass, send_email_order, st_save_helper
from interface.views import clear_styleboard_session, st_man
from paypal import PayPal, PayPalItem
from django.core.urlresolvers import reverse
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from django.core.validators import email_re, validate_email
from django.contrib import auth
from uuid import uuid4
from common.models import Countries

from django.core.mail import EmailMultiAlternatives
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.core.exceptions import ValidationError

import logging
logr = logging.getLogger(__name__)

class ShippingProcessor(ProcessorBase):

    def process(self, order, items):

        items_subtotal = 0

        for item in items:

            item_subtotal = item.quantity * item._unit_price

            items_subtotal = items_subtotal + item_subtotal

            item._line_item_price = item_subtotal

        """
            shipping cost is the product of cost and subtotal
        """

        order.items_subtotal = items_subtotal

        cost = settings.PLATA_SHIPPING['cost_percentage'] * order.subtotal
        tax = settings.PLATA_SHIPPING['tax_percentage']

        order.shipping_cost, __ = self.split_cost(cost, tax)
        order.shipping_discount = min(order.discount_remaining, order.shipping_cost)
        order.shipping_tax = tax / 100 * (order.shipping_cost - order.shipping_discount)

        self.set_processor_value('total', 'shipping', order.shipping_cost - order.shipping_discount + order.shipping_tax)
        self.set_processor_value('total', 'items_subtotal', order.subtotal)

        total = sum( self.get_processor_value('total').values(), Decimal('0.00'), )

        order.total = total.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)

        tax_details = dict(order.data.get('tax_details', []))
        self.add_tax_details(tax_details, tax, order.shipping_cost, order.shipping_discount, order.shipping_tax)
        order.data['tax_details'] = tax_details.items()

class BaseCheckoutForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.shop = kwargs.pop('shop')
        self.request = kwargs.pop('request')
        super(BaseCheckoutForm, self).__init__(*args, **kwargs)

    def clean(self):
        data = super(BaseCheckoutForm, self).clean()

        email = data.get('email')
        create_account = data.get('create_account')

        if email:
            users = list(User.objects.filter(username=email))

            if users:
                if self.request.user not in users:
                    if self.request.user.is_authenticated():
                        self._errors['email'] = self.error_class([_('This e-mail address belongs to a different account.')])
                    else:
                        self._errors['email'] = self.error_class([_('This e-mail address might belong to you, but we cannot know for sure because you are not authenticated yet.')])
            else:
                users = list(User.objects.filter(email=email))
                if users:
                    if self.request.user not in users:
                        if self.request.user.is_authenticated():
                            self._errors['email'] = self.error_class([_('This e-mail address belongs to a different account.')])
                        else:
                            self._errors['email'] = self.error_class([_('This e-mail address might belong to you, but we cannot know for sure because you are not authenticated yet.')])
        return data

    def save(self):

        order = super(BaseCheckoutForm, self).save(commit=False)
        contact = self.shop.contact_from_user(self.request.user)

        if contact:
            order.user = contact.user
        elif self.request.user.is_authenticated():
            order.user = self.request.user

        if (self.cleaned_data.get('create_account') and not contact) or (not contact and self.request.user.is_authenticated()):

            password = None
            email = self.cleaned_data.get('email')
            first_name = self.cleaned_data.get('billing_first_name')
            last_name = self.cleaned_data.get('billing_last_name')

            if not self.request.user.is_authenticated():
                password = User.objects.make_random_password()
                user = User.objects.create_user(email, email, password)
                user = auth.authenticate(username=email, password=password)
                user.first_name = first_name
                user.last_name = last_name
                user.save()
                customer_profile = CustomerProfile()
                customer_profile.user = user
                customer_profile.nickname = email
                customer_profile.save()
                auth.login(self.request, user)
                send_email_set_pass(user.id)
            else:
                user = self.request.user
                
                if not email_re.search(user.username):
                    #print "creating......."
                    user = User.objects.get(id=user.id)
                    user.username = email
                    user.email = email
                    user.save()

            contact = self.shop.contact_model(user=user)
            order.user = user

            signals.contact_created.send(sender=self.shop, user=user,contact=contact, password=password)

        order.save()

        if contact:
            contact.update_from_order(order, request=self.request)
            contact.save()

        return order

class IdecorateCheckoutForm(BaseCheckoutForm):
    class Meta:
        fields = ['email'] + ['billing_%s' % f for f in Contact.ADDRESS_FIELDS] + ['shipping_%s' % f for f in Contact.ADDRESS_FIELDS] + ['shipping_same_as_billing']
        model = Order

    def __init__(self, *args, **kwargs):
        shop = kwargs.get('shop')
        request = kwargs.get('request')
        contact = shop.contact_from_user(request.user)
        order = shop.order_from_request(request)

        states = tuple(sorted((('Australian Capital Territory','Australian Capital Territory'), ('New South Wales','New South Wales'), ('Victoria','Victoria'), ('Queensland','Queensland'), ('South Australia','South Australia'), ('Western Australia','Western Australia'), ('Tasmania','Tasmania'), ('Northern Territory','Northern Territory'))))
        cities = tuple(sorted((
            ('Canberra','Canberra'),('Albury','Albury'), ('Armidale','Armidale'), ('Bathurst','Bathurst'), ('Blue Mountains','Blue Mountains'), ('Broken Hill','Broken Hill'), ('Campbelltown','Campbelltown'), ('Cessnock','Cessnock'), ('Dubbo','Dubbo'), ('Goulburn','Goulburn'), ('Grafton','Grafton'), ('Lithgow','Lithgow'), ('Liverpool','Liverpool'), ('Newcastle','Newcastle'), ('Orange','Orange'), ('Parramatta','Parramatta'), ('Penrith','Penrith'), ('Queanbeyan','Queanbeyan'), ('Sydney','Sydney'), 
            ('Tamworth','Tamworth'), ('Wagga','Wagga'),('City of Bankstown','City of Bankstown'), ('City of Blacktown','City of Blacktown'), ('City of Botany Bay','City of Botany Bay'), ('City of Canada Bay','City of Canada Bay'), ('City of Canterbury','City of Canterbury'), ('City of Coffs Harbour','City of Coff Harbour'), ('City of Fairfield','City of Fairfield'), ('City of Gosford','City of Gosford'), ('City of Greater Taree','City of Greater Taree'), ('City of Griffith','City of Griffith'), 
            ('City of Hawkesbury','City of Hawkesbury'), ('City of Holroyd','City of Holroyd'), ('City of Hurtsville','City of Hurtsville'), ('City of Lake Macquarie','City of Lake Macquarie'), ('City of Lismore','City of Lismore'), ('City of Lithgow','City of Lithgow'), ('City of Maitland','City of Maitland'), ('City of Randwick','City of Randwick'), ('City of Rockdale','City of Rockdale'), ('City of Ryde','City of Ryde'), ('City of Shellharbour','City of Shellharbour'), ('City         f Shoalhaven','City of Shoalhaven'), 
            ('City of Willoughby','City of Willoughby'), ('Darwin','Darwin'), ('Palmerston','Palmerston'), ('Brisbane','Brisbane'), ('Bundaberg','Bundaberg'), ('Cairns','Cairns'), ('Caloundra','Caloundra'), ('Gladstone','Gladstone'), ('Gold Coast','Gold Coast'), ('Gympie','Gympie'), ('Hervey Bay','Hervey Bay'), ('Ipswich','Ipswich'), ('Logan City','Logan City'), ('Mackay','Mackay'), ('Maryborough','Maryborough'), ('Mount Isa','Mount Isa'), ('Rockhampton','Rockhampton'), ('Sunshine Coast','Sunshine Coast'), ('Surfers Paradise','Surfers Paradise'), 
            ('Toowoomba','Toowoomba'), ('Townsville','Townsville'), ('Charters Towers','Charters Towers'), ('Redcliffe City','Redcliffe City'), ('Redland City','Redland City'), ('Thuringova','Thuringova'), ('Warwick','Warwick'), ('Adelaide','Adelaide'), ('Mount Barker','Mount Barker'), ('Mount Gambier','Mount Gambier'), ('Murray Bridge','Murray Bridge'), ('Port Adelaide','Port Adelaide'), ('Port Augusta','Port Augusta'), ('Port Pirie','Port Pirie'), ('Port Lincoln','Port Lincoln'), ('Victor Harbor','Victor Harbor'), ('Whyalla','Whyalla'), 
            ('Hobart','Hobart'), ('Burnie','Burnie'), ('Devonport','Devonport'), ('Launceston','Launceston'), ('Melbourne','Melbourne'), ('Ararat','Ararat'), ('Bairnsdale','Bairnsdale'), ('Benalla','Benalla'), ('Ballarat','Ballarat'), ('Bendigo','Bendigo'), ('Dandenong','Dandenong'), ('Frankston','Frankston'), ('Geelong','Geelong'), ('Hamilton','Hamilton'), ('Horsham','Horsham'), ('Melton','Melton'), ('Moe','Moe'), ('Morwell','Morwell'), ('Mildura','Mildura'), ('Mildura','Mildura'), ('Sale','Sale'), ('Shepparton','Shepparton'), ('Swan Hill','Swan Hill'), 
            ('Traralgon','Traralgon'), ('Wangaratta','Wangaratta'), ('Warrnambool','Warrnambool'), ('Wodonga','Wodonga'), ('Perth','Perth'), ('Albany','Albany'), ('Bunbury','Bunbury'), ('Busselton','Busselton'), ('Fremantle','Fremantle'), ('Geraldton','Geraldton'), ('Joondalup','Joondalup'), ('Kalgoorlie','Kalgoorlie'), ('Mandurah','Mandurah'), ('Rockingham','Rockingham'), ('City of Armadale','City of Armadale'), ('City of Bayswater','City of Bayswater'), ('City of Canning','City of Canning'), ('City of Cockburn','City of Cockburn'), ('City of Gosnells','City of Gosnells'), 
            ('City of Melville','City of Melville'), ('City of Nedlands','City of Nedlands'), ('City of South Perth','City of South Perth'), ('City of Stirling','City of Stirling'), ('City of Subiaco','City of Subiaco'), ('City of Swan','City of Swan'), ('City of Wanneroo','City of Wanneroo')
        )))

        country_choices = [('','-Select-')]

        c = Countries.objects.filter()

        for cc in c:
            country_choices.append((cc.name,cc.name))

        country_choices = tuple(country_choices)

        #('PayPal','PayPal'),('Visa','Visa'),('Mastercard','Mastercard'),('American_Express','American Express')
        payment_method_choices = []

        if settings.IDECORATE_ENABLE_PAYPAL:
            payment_method_choices.append(('PayPal', 'PayPal'))

        if settings.IDECORATE_ENABLE_VISA:
            payment_method_choices.append(('Visa','Visa'))

        if settings.IDECORATE_ENABLE_MASTERCARD:
            payment_method_choices.append(('Mastercard','Mastercard'))

        if settings.IDECORATE_ENABLE_AMERICAN_EXPRESS:
            payment_method_choices.append(('American_Express','American Express'))

        payment_method_choices = tuple(payment_method_choices)

        if contact:
            initial = {}
            for f in contact.ADDRESS_FIELDS:
                initial['billing_%s' % f] = getattr(contact, f)
                kwargs['initial'] = initial

            for f in contact.ADDRESS_FIELDS:
                initial['shipping_%s' % f] = getattr(contact, f)
                kwargs['initial'] = initial

            initial['email']                    = contact.user.username
            initial['billing_first_name']       = contact.user.first_name
            initial['billing_last_name']        = contact.user.last_name
            initial['notes']                    = order.notes
            initial['billing_salutation']       = contact.billing_salutation
            initial['shipping_same_as_billing'] = contact.shipping_same_as_billing
            initial['shipping_address']         = contact.address
            initial['billing_address']          = contact.address2
            initial['shipping_address2']        = contact.shipping_address2
            initial['billing_address2']         = contact.billing_address2
            initial['shipping_state']           = contact.shipping_state
            initial['billing_state']            = contact.billing_state
            initial['shipping_city']            = contact.city
            initial['billing_city']             = contact.city2
            initial['shipping_zip_code']        = contact.zip_code
            initial['billing_zip_code']         = contact.zip_code2
            initial['billing_country']          = contact.countries2
            initial['shipping_country']         = contact.countries



        # if request.POST.get('order-shipping_date') is None:
        #     if 'delivery_date' in request.session:
        #         initial['shipping_date'] = request.session['delivery_date']

        try:

            order_data = OrderData.objects.get(order=order)
            misc_data = simplejson.loads(order_data.data)

            initial['shipping_date'] = misc_data['delivery_date']
            initial['billing_contact_number'] = misc_data['billing_contact_number']
            initial['payment_method'] = misc_data['order_payment_method']

        except Exception as e:
            # print e
            pass

        super(IdecorateCheckoutForm, self).__init__(*args, **kwargs)

        self.fields['shipping_address2']        = forms.CharField(max_length=200, label=_("Shipping Address2"), required=False)
        self.fields['shipping_address']         = forms.CharField(max_length=200, label=_("Shipping Address"), required=True, error_messages={'required':_('Delivery Address is a required field.')})
        self.fields['shipping_salutation']      = forms.ChoiceField(label=_("Salutation"), choices=(('Mr','Mr'), ('Ms','Ms'), ('Mrs','Mrs')), required=False,widget=forms.Select, error_messages={'required':_('Salutation is a required field.')})
        self.fields['billing_salutation']       = forms.ChoiceField(label=_("Salutation"), choices=(('Mr','Mr'), ('Ms','Ms'), ('Mrs','Mrs')), required=True,widget=forms.Select)
        self.fields['shipping_state']           = forms.CharField(max_length=150,label=_("Shipping State"),required=True, error_messages={'required':_('Delivery State is a required field. If None, indicate None or N/A')})
        self.fields['shipping_city']            = forms.CharField(max_length=150,label=_("ChoiceFielding City"), required=True, error_messages={'required':_('Delivery City is a required field.')})
        self.fields['shipping_same_as_billing'] = forms.BooleanField(initial=True,label=_("Same as Billing"),required=False)

        self.fields['shipping_date']            = forms.CharField(label=_("Shipping Date"), required=False, error_messages={'required':_('Delivery Date is a required field.')})
        self.fields['shipping_zip_code']        = forms.CharField(label=_("Shipping Zip Code"), required=True, error_messages={'required':_('Delivery Zip Code is a required field.')})        
        self.fields['email']                    = forms.EmailField(label=_("Email"), required=True, error_messages={'invalid':_('Enter a valid Email in Personal Information.'),'required':_('Email in Personal Information is a required field.')})
        self.fields['billing_last_name']        = forms.CharField(max_length=100, label=_("Billing Last Name"), required=True, error_messages={'required':_('Last Name is a required field.')})
        self.fields['billing_first_name']       = forms.CharField(max_length=100, label=_("Billing First Name"), required=True, error_messages={'required':_('First Name is a required field.')})
        self.fields['billing_contact_number']   = forms.CharField(max_length=100, label=_("Billing Contact Number"), required=False)
        self.fields['payment_method']           = forms.ChoiceField(label=_("Payment Method"), choices=payment_method_choices, required=True,widget=forms.RadioSelect, error_messages={'required':_('Payment Method is a required field.')})
        self.fields['notes']                    = forms.CharField(label=_("Special Requests and Comments"), widget=forms.Textarea, required=False)
        self.fields['shipping_country']         = forms.ChoiceField(choices=country_choices,label=_("Shipping Country"), required=True, error_messages={'required':_('Delivery Country is a required field.')})
        self.fields['billing_country']          = forms.ChoiceField(choices=country_choices,label=_("Billing Country"), required=True, error_messages={'required':_('Billing Country is a requimax_length=150,red field.')})


        shipping_same_as_billing = request.POST.get('order-shipping_same_as_billing')
        
        if shipping_same_as_billing:
            self.fields['billing_zip_code']     = forms.CharField(label=_("Billing Zip Code"), required=False, error_messages={'required':_('Billing Zip Code is a required field.')})
            self.fields['billing_address']      = forms.CharField(max_length=200, label=_("Billing Address"), required=False, error_messages={'required':_('Billing Address is a required field.')})
            self.fields['billing_address2']     = forms.CharField(max_length=200, label=_("Billing Address2"), required=False)
            self.fields['billing_state']        = forms.CharField(max_length=150,label=_("Billing State"), required=False)
            self.fields['billing_city']         = forms.CharField(max_length=150,label=_("Billing City"), required=False)
            self.fields['billing_country']      = forms.ChoiceField(choices=country_choices,label=_("Billing Country"), required=False, error_messages={'required':_('Billing Country is a required field.')})
        else:
            self.fields['billing_zip_code']     = forms.CharField(label=_("Billing Zip Code"), required=True, error_messages={'required':_('Billing Zip Code is a required field.')})
            self.fields['billing_address']      = forms.CharField(max_length=200, label=_("Billing Address"), required=True, error_messages={'required':_('Billing Address is a required field.')})
            self.fields['billing_address2']     = forms.CharField(max_length=200, label=_("Billing Address2"), required=False)
            self.fields['billing_state']        = forms.CharField(max_length=150,label=_("Billing State"), required=True, error_messages={'required':_('Billing State is a required field. If None, indicate None or N/A')})
            self.fields['billing_city']         = forms.CharField(max_length=150,label=_("Billing City"), required=True, error_messages={'required':_('Billing City is a required field.')})
            self.fields['billing_country']      = forms.ChoiceField(choices=country_choices,label=_("Billing Country"), required=True, error_messages={'required':_('Billing Country is a required field.')})
        
        if not contact:
            self.fields['create_account'] = forms.BooleanField(
                label=_('create account'),
                required=False, initial=True)

    def clean(self):
        data = super(IdecorateCheckoutForm, self).clean()

        email = data.get('email')
        create_account = data.get('create_account')

        if email:
            users = list(User.objects.filter(email=email))

            if users:
                if self.request.user not in users:
                    if self.request.user.is_authenticated():
                        self._errors['email'] = self.error_class([
                            _('This e-mail address belongs to a different account.')])
                    else:
                        self._errors['email'] = self.error_class([
                            _('The email you entered is already linked to an existing account. If you are the owner of the account, please log in.')])
        
        return data

    def save(self,**kwargs):
        order = super(IdecorateCheckoutForm, self).save()
        notes = kwargs.get('notes')
        billing_salutation = kwargs.get('billing_salutation')

        contact = self.shop.contact_from_user(self.request.user)

        # print kwargs
        shipping_address    = kwargs.get('shipping_address')
        shipping_address2   = kwargs.get('shipping_address2')
        shipping_state      = kwargs.get('shipping_state')
        shipping_city       = kwargs.get('shipping_city')
        shipping_zip_code   = kwargs.get('shipping_zip_code')
        shipping_country    = kwargs.get('shipping_country')

        billing_address     = kwargs.get('billing_address')
        billing_address2    = kwargs.get('billing_address2')
        billing_state       = kwargs.get('billing_state')
        billing_city        = kwargs.get('billing_city')
        billing_zip_code    = kwargs.get('billing_zip_code')
        billing_country     = kwargs.get('billing_country')
        same_as_billing     = kwargs.get('same_as_billing')
        billing_first_name  = kwargs.get('billing_first_name')
        billing_last_name   = kwargs.get('billing_last_name')
        email               = kwargs.get('email')

        if same_as_billing:
            contact.shipping_same_as_billing = same_as_billing
            contact.save()

        if shipping_address:
            contact.address = shipping_address
            contact.save()

        if billing_address:
            contact.address2 = billing_address
            contact.save()

            order.billing_address = billing_address
            order.save()

        #if shipping_address2:
        contact.shipping_address2 = shipping_address2
        contact.save()

        order.data['delivery_address2'] = shipping_address2
        order.save()

        #if billing_address2:
        contact.billing_address2 = billing_address2
        contact.save()

        order.data['billing_address2'] = billing_address2
        order.save()

        if shipping_state:
            contact.shipping_state = shipping_state
            contact.save()

            order.data['delivery_state'] = shipping_state
            order.save()

        if billing_state:
            contact.billing_state = billing_state
            contact.save()

            order.data['billing_state'] = billing_state
            order.save()

        if shipping_city:
            contact.city = shipping_city
            contact.save()

        if billing_city:
            contact.city2 = billing_city
            contact.save()

            order.billing_city = billing_city
            order.save()

        if billing_salutation:
            contact.billing_salutation = billing_salutation
            contact.save()

        if shipping_zip_code:
            contact.zip_code = shipping_zip_code
            contact.save()

        if billing_zip_code:
            contact.zip_code2 = billing_zip_code
            contact.save()

            order.billing_zip_code = billing_zip_code
            order.save()

        if shipping_country:
            contact.countries = shipping_country
            contact.save()

            order.data['delivery_country'] = shipping_country
            order.save()

        if billing_country:
            contact.countries2 = billing_country
            contact.save()

            order.data['billing_country'] = billing_country
            order.save()

        if email:
            c_user = User.objects.get(id=int(self.request.user.id))
            c_user.email = email
            c_user.username = email
            c_user.save()

        if notes:
            order.notes = notes
            order.save()

        if billing_first_name:
            contact.first_name = billing_first_name
            contact.save()

            c_user = User.objects.get(id=int(self.request.user.id))
            c_user.first_name = billing_first_name
            c_user.save()

        if billing_last_name:
            contact.last_name = billing_last_name
            contact.save()

            c_user = User.objects.get(id=int(self.request.user.id))
            c_user.last_name = billing_last_name
            c_user.save()

        return order

    def clean_billing_contact_number(self):

        billing_contact_number = self.cleaned_data.get('billing_contact_number', None)

        if billing_contact_number:

            if not re.search("^\([0-9+]{3}\)[0-9+]{4}\-[0-9+]{4}$",billing_contact_number,re.IGNORECASE):
                raise forms.ValidationError(_('Please enter a valid phone number'))
                
        return billing_contact_number

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

            # print request.session.get('cartsession')

            sessionid = request.session.get('cartsession')
            
            if GuestTableTemp.objects.filter(sessionid=sessionid).exists():

                #print "with session id: %s" % (sessionid)

                if GuestTable.objects.filter(order=order).exists():

                    logr.info("with session id: %s and order: %s exists" % (sessionid,order))

                    guestTable = GuestTable.objects.get(order=order)
                    guestTable.guests = guests
                    guestTable.tables = tables
                    guestTable.save()
                else:

                    logr.info("with session id: %s and no order exists" % (sessionid))

                    guestTable = GuestTable()
                    guestTable.order = order
                    guestTable.guests = guests
                    guestTable.tables = tables
                    guestTable.save()

                self.guest_table = guestTable

            else:

                #print "no session id"

                if GuestTable.objects.filter(order=order).exists():

                    logr.info("no session id and order: %s exists" % (order))

                    guestTable = GuestTable.objects.get(order=order)
                    guestTable.guests = guests
                    guestTable.tables = tables
                    guestTable.save()
                else:

                    logr.info("no session id and no order exists")

                    guestTable = GuestTable()
                    guestTable.order = order
                    guestTable.guests = guests
                    guestTable.tables = tables
                    guestTable.save()

                self.guest_table = guestTable

    def render_checkout(self, request, context):
        try:
            guest_table = GuestTable.objects.get(order=context['order'])
            context.update({'guest_table': guest_table})
        except Exception as e:
            pass
        return self.render(request, 'plata/shop_checkout.html', self.get_context(request, context))
    
    def render_confirmation(self, request, context):
        try:
            guest_table = GuestTable.objects.get(order=context['order'])
            context.update({'guest_table': guest_table})
        except Exception as e:
            print e
        return self.render(request, 'plata/shop_confirmation.html', self.get_context(request, context))

    def checkout_form(self, request, order):
        return IdecorateCheckoutForm

    def confirmation(self, request, order):
        #print type(order.addresses)

        order.recalculate_total()

        card_error = []

        card_number = ""
        name_on_card = ""
        expires = ""
        cvv_code = ""
        show_confirm_infos = True
        process_now_the_order = False
        process_now_the_payment = False

        try:
            thisContact = Contact.objects.get(user__id=int(request.user.id))
        except:
            thisContact = None  

        kwargs = {}
        kwargs['contact'] = thisContact


        ConfirmationForm = self.confirmation_form(request, order)
        kwargs = {
            'order': order,
            'request': request,
            'shop': self,
        }

        order_data = OrderData.objects.get(order=order)
        misc_data = simplejson.loads(order_data.data)
        #print "The total is: %.2f" % order.total

        if request.method == 'POST':
            form = ConfirmationForm(request.POST, **kwargs)

            process_it = request.POST.get('process_now_the_order')
            process_pay = request.POST.get('process_now_the_payment')

            if form.is_valid():
                
                if process_it is not None:
                    show_confirm_infos = False
                    process_now_the_order = True

                if process_pay is not None:
                    process_now_the_payment = True

                if process_now_the_payment:
                    #pass
                    card_number = request.POST.get('card_number', "")
                    name_on_card = request.POST.get('name_on_card', "")
                    expires = request.POST.get('expires', "")
                    cvv_code = request.POST.get('cvv_code', "")

                    if not card_number:
                        card_error.append("Card Number is a required field.")

                    if not name_on_card:
                        card_error.append("Name on card is a required field.")

                    if not expires:
                        card_error.append("Expires is a required field.")
                    else:
                        if not re.search('/',expires):
                            card_error.append("Invalid Expires value.")

                    if not cvv_code:
                        card_error.append("CVV Code is a required field.")

                    if len(card_error) == 0:

                        #if process_now_the_order:

                        # pMethod = request.session.get('order-payment_method','')

                        # if pMethod == "Visa":
                        #     pMethod = "VISA"
                        # elif pMethod == "Mastercard":
                        #     pMethod = "Master"
                        # else:
                        #     pMethod = "AMEX"
                        
                        url = settings.PAYDOLLAR_SS_DIRECT_URL
                        params = {}
                        pMethod = misc_data.get('order_payment_method','')
                        methods = {'Visa': 'VISA','Mastercard': 'Master','American_Express': 'AMEX'}

                        splittedExpires = str(expires).split("/")

                        params['orderRef'] = str("%34d" % int(order.id)).replace(' ','0')
                        params['amount'] = "%.2f" % order.total
                        params['currCode'] = settings.PAYDOLLAR_CURRENCY
                        params['lang'] = "E"
                        params['merchantId'] = settings.PAYDOLLAR_MERCHANT_ID
                        params['pMethod'] = methods[pMethod]
                        params['epMonth'] = splittedExpires[0]
                        params['epYear'] = splittedExpires[1]
                        params['cardNo'] = card_number
                        params['cardHolder'] = name_on_card
                        params['securityCode'] = cvv_code
                        params['payType'] = "N" #N or H

                        if settings.SKIPPING_MODE:
                            ret = {
                                'successcode': '0'
                            }
                        else:

                            ret = ss_direct(params, url, True)

                        if int(ret['successcode']) == -1 or int(ret['successcode']) == 1:

                            card_error.append(ret['errMsg'])
                            form = ConfirmationForm(**kwargs)
                            
                        else:

                            return form.process_confirmation()
                    else:
                        form = ConfirmationForm(**kwargs)
        else:
            form = ConfirmationForm(**kwargs)

        paypal = PayPal(cancel_return_url="%s%s" % (settings.PAYPAL_RETURN_URL, reverse('plata_shop_checkout')), return_url="%s%s" % (settings.PAYPAL_RETURN_URL, reverse('paypal_return_url')))
        paypal_orders = order.items.filter().order_by('-id')

        for paypal_order in paypal_orders:
            paypal.addItems(PayPalItem(item_name=paypal_order.name, amount="%.2f" % paypal_order._unit_price, quantity=paypal_order.quantity))  

        st_save_helper(request, order)
        
        return self.render_confirmation(request, {
            'order': order,
            'form': form,
            'confirmed': request.GET.get('confirmed', False),
            'progress': 'confirmation',
            'card_error': card_error,
            'card_number': card_number,
            'name_on_card': name_on_card,
            'expires': expires,
            'cvv_code': cvv_code,
            'show_confirm_infos':show_confirm_infos,
            'paypal_url': settings.PAYPAL_URL,
            'paypal_form': mark_safe(paypal.generateInputForm()),
            'shop':self,
            'contact': thisContact,
            'misc_data' : misc_data,
            'custom_data' : simplejson.dumps({'order_id':  order.id,'user' : request.user.id if request.user.is_authenticated() else 0}).replace('"', '&quot;')
        })

    def checkout(self, request, order):

        """Handles the first step of the checkout process"""
        if not request.user.is_authenticated():
            if request.method == 'POST' and '_login' in request.POST:
                loginform = AuthenticationForm(data=request.POST, prefix='login')

                if loginform.is_valid():
                    user = loginform.get_user()
                    auth.login(request, user)

                    order.user = user
                    order.save()
                    return HttpResponseRedirect('.')
            else:
                loginform = AuthenticationForm(prefix='login')
        else:
            loginform = None

        if order.status < order.CHECKOUT:
            order.update_status(order.CHECKOUT, 'Checkout process started')

        OrderForm = self.checkout_form(request, order)



        orderform_kwargs = {
            'prefix': 'order',
            'instance': order,
            'request': request,
            'shop': self,
            }

        if request.method == 'POST' and '_checkout' in request.POST:
            orderform = OrderForm(request.POST, **orderform_kwargs)

            if orderform.is_valid():
                notes = request.POST.get('order-notes')
                same_as_billing = request.POST.get('order-shipping_same_as_billing')
                delivery_address = request.POST.get('order-shipping_address')
                billing_address = request.POST.get('order-billing_address')
                delivery_address2 = request.POST.get('order-shipping_address2')
                billing_address2 = request.POST.get('order-billing_address2')
                delivery_date = request.POST.get('order-shipping_date')
                delivery_state = request.POST.get('order-shipping_state')
                billing_state = request.POST.get('order-billing_state')
                delivery_city = request.POST.get('order-shipping_city')
                billing_city = request.POST.get('order-billing_city')
                delivery_zip_code = request.POST.get('order-shipping_zip_code')
                billing_zip_code = request.POST.get('order-billing_zip_code')
                salutation = request.POST.get('order-billing_salutation')
                billing_country = request.POST.get('order-billing_country')
                delivery_country = request.POST.get('order-shipping_country')
                billing_first_name = request.POST.get('order-billing_first_name')
                billing_last_name = request.POST.get('order-billing_last_name')
                email = request.POST.get('order-email')
                billing_contact_number = request.POST.get('order-billing_contact_number')

                if same_as_billing:
                    billing_address = delivery_address
                    billing_address2 = delivery_address2
                    billing_state = delivery_state
                    billing_city = delivery_city
                    billing_zip_code = delivery_zip_code
                    billing_country = delivery_country

                
                # request.session['order-payment_method'] = request.POST.get('order-payment_method','')

                custom_data = {}
                custom_data['order_payment_method'] = request.POST.get('order-payment_method','')
                custom_data['order_notes'] = request.POST.get('order-notes','')
                custom_data['delivery_address2'] = delivery_address2
                custom_data['billing_address2'] = billing_address2
                custom_data['delivery_date'] = delivery_date
                custom_data['delivery_state'] = delivery_state
                custom_data['billing_state'] = billing_state
                custom_data['salutation'] = salutation
                custom_data['billing_country'] = billing_country
                custom_data['shipping_country'] = delivery_country
                custom_data['billing_contact_number'] = billing_contact_number

                try:
                    order_data = OrderData.objects.get(order=order)
                except:
                    order_data = OrderData()

                order_data.order = order
                order_data.data = simplejson.dumps(custom_data)
                order_data.save()
                        
                        
                orderform.save(
                    notes=notes, 
                    billing_salutation=salutation,
                    same_as_billing=True if same_as_billing else False,
                    shipping_address=delivery_address,
                    billing_address=billing_address,
                    shipping_address2=delivery_address2,
                    billing_address2=billing_address2,
                    shipping_state=delivery_state,
                    billing_state=billing_state,
                    shipping_city=delivery_city,
                    billing_city=billing_city,
                    shipping_zip_code=delivery_zip_code,
                    billing_zip_code=billing_zip_code,
                    billing_country=billing_country,
                    shipping_country=delivery_country,
                    billing_first_name=billing_first_name,
                    billing_last_name=billing_last_name,
                    email=email
                )

                """
                added notes
                """
                return redirect('plata_shop_discounts')
        else:

            orderform = OrderForm(**orderform_kwargs)
            

        return self.render_checkout(request, {
            'order': order,
            'loginform': loginform,
            'orderform': orderform,
            'progress': 'checkout'
            })

    def order_success(self, request):
        """Handles order successes (e.g. when an order has been successfully paid for)"""
        order = self.order_from_request(request)

        if not order:
            return self.order_new(request)

        if not order.balance_remaining:
            self.set_order_on_request(request, order=None)


        order_data = OrderData.objects.get(order=order)
        o_data = simplejson.loads(order_data.data)

        paymentData = {}
        paymentData['delivery_address2'] = o_data['delivery_address2']
        paymentData['billing_address2'] = o_data['billing_address2']
        paymentData['delivery_date'] = o_data['delivery_date']
        paymentData['delivery_state'] = o_data['delivery_state']
        paymentData['billing_state'] = o_data['billing_state']
        paymentData['salutation'] = o_data['salutation']
        paymentData['contact_number'] = o_data['billing_contact_number']

        #try:
        oPayment = OrderPayment.objects.get(order=order)
        oPayment.payment_method = o_data['order_payment_method']
        oPayment.data = simplejson.dumps(paymentData)
        oPayment.save()
        #except:
        #   pass

        """
        order update note
        """
        notes = o_data['order_notes']
        order.notes = notes
        order.save()

        # st_save_helper(request, order)

        """
        sbid = None

        if 'customer_styleboard' in request.session:
            sbid = request.session.get('customer_styleboard').id

        if 'personalize_id' in request.session:
            print "There's a personalize_id"
        """

        current_user = User.objects.get(id=int(request.user.id))

        if 'ipn_emailed' in o_data and o_data['ipn_emailed']:

            pass
                
        else:

            emailed = send_email_order(order, current_user, notes, paymentData['contact_number'], self)

            logr.info('emailed order confirmation to : %s from order success' % current_user.email)


        order_data.delete() # not needed after saving to order payment\
        
        clear_styleboard_session(request)

        try:
            del request.session['customer_styleboard']
            del request.session['personalize_id']
        except:
            pass

        return self.render(request, 'plata/shop_order_success.html',
            self.get_context(request, {
                'order': order,
                'progress': 'success',
                }))

shop = IdecorateShop(contact_model=Contact, order_model=Order, discount_model=Discount)

def checkout(request):

    sessionid = request.session.get('cartsession',None)

    # print sessionid
    
    if not sessionid:

        sessionid = generate_unique_id()
        request.session['cartsession'] = sessionid

    cart_item = CartTemp.objects.filter(sessionid=sessionid).order_by('-id')

    order = shop.order_from_request(request, create=True)
    order.items.filter().delete()

    if cart_item.count() > 0:

        guest_table = GuestTableTemp.objects.get(sessionid=sessionid)

        for cart in cart_item:

            try:

                order.modify_item(cart.product, absolute=cart.quantity)

            except Exception as e:

                CartTemp.objects.filter(sessionid=sessionid).delete()

                logr.error("The error is: %s" % e)

                return shop.order_new(request)

        shop.modify_guest_table(request, guest_table.guests, guest_table.tables, order)


    return redirect('plata_shop_checkout')

def checkout_from_view_styleboard(request):

    if request.method=='POST':

        sessionid = request.session.get('cartsession',None)

        if sessionid:

            CartTemp.objects.filter(sessionid=sessionid).delete()
            GuestTableTemp.objects.filter(sessionid=sessionid).delete()

        else:       

            sessionid = generate_unique_id()
            request.session['cartsession'] = sessionid

        styleboard_item_id = request.POST['sid']
        customer_styleboard = get_user_styleboard(None,styleboard_item_id)
        styleboard = customer_styleboard.styleboard_item
        cart_items = get_styleboard_cart_item(styleboard)
        cart_items = cart_items.order_by('-id')

        order = shop.order_from_request(request, create=True)
        order.items.filter().delete()

        idecorateSettings = IdecorateSettings.objects.get(pk=1)
        guests = styleboard.item_guest

        if not guests:

            guests = idecorateSettings.global_default_quantity

        tables = styleboard.item_tables

        if not tables:

            tables = idecorateSettings.global_table

        if cart_items.count() > 0:

            for cart in cart_items:
                data = {}
                data['product'] = cart.product
                data['sessionid'] = sessionid
                data['quantity'] = cart.quantity
                data['guests'] = guests
                data['tables'] = tables
                data['wedding'] = 1
                add_to_cart(data)

        cart_items = CartTemp.objects.filter(sessionid=sessionid).order_by('-id')

        logr.info("The cart_items count from view is: %s" % cart_items.count())

        if cart_items.count() > 0:

            for cart in cart_items:

                try:
                    order.modify_item(cart.product, absolute=cart.quantity)

                except:

                    CartTemp.objects.filter(sessionid=sessionid).delete()

                    return shop.order_new(request)

            shop.modify_guest_table(request, guests, tables, order)

        sms = st_man(request, False)
        
        return redirect('plata_shop_checkout')

    else:

        return redirect('styleboard')

def order_checkout_email(request):

    info = {}
    

    if request.method == "POST":

        email_fields = request.POST.getlist('email')
        name = request.POST.get('name', None)
        mailto_list = []
        email_to_send = []
        errors = []
        post_data = []

        info['name_post'] = str(name)
        info['post_data'] = post_data

        if not name:

            errors.append("Name field is required.")

        for index, email_field in enumerate(email_fields):

            try:
                validate_email(str(email_field))
                email_to_send.append(email_field)
            except ValidationError:
                pass

            post_data.append(email_field)

        if len(email_to_send) == 0:

            errors.append("Please enter atleast one(1) valid email.")
            

        if len(errors) > 0:

            info['errors'] = errors

        else:

            mailto_list += email_to_send

            is_sent = send_order_checkout_email(request, mailto_list, str(name))

            if is_sent:

                info['order_checkout_email_sent'] = "Email sent"

            else:

                info['order_checkout_email_sent'] = "Sending email failed. Please try again."

    else:

        if request.user.is_authenticated():

            info['name_post'] =  '%s %s' % (request.user.first_name, request.user.last_name)

    return render_to_response('customer/iframe/email_order.html', info, RequestContext(request))


def send_order_checkout_email(request,mailto_list, sender):

    info = {}
    is_sent = False
    orderID = 0
    filename = ""

    if 'order_id' in request.GET:

        orderID = request.GET.get('order_id')

    else:

        return is_sent
    
    info['media_root'] = '%s/%s' % (settings.IDECORATE_HOST,settings.MEDIA_URL )
    info['sender'] = sender.title()

    info['cart_list'] = ''
    info['default_multiplier'] = 0

    if orderID:

        try:

            order = Order.objects.get(id=int(orderID))
            info['cart_list'] = OrderItem.objects.filter(order=order)
            info['default_multiplier'] = GuestTable.objects.get(order=order)
            info['total_price'] = order.total

            order_styleboard = OrderStyleboard.objects.get(order=order)

            filename = order_styleboard.styleboard

        except Exception as e:

            logr.error('error on gathering data: %s' % e)

    
    styleboard = "%s%s%s" % (settings.MEDIA_ROOT, "styleboards/", filename)

    info['media_root'] = '%s/%s' % (settings.IDECORATE_HOST,settings.MEDIA_URL )
    info['sender'] = sender.title()

    html = render_to_string('interface/styleboard_email.html', info)

    # top level container, defines plain text version

    email = EmailMultiAlternatives(subject="Checkout iDecorateWeddings.com", body="this email is generated by www.idecorateweddings.com", from_email="noreply@idecorateweddings.com", to=mailto_list)
    
    # Add an image

    image_data = open(styleboard, 'rb').read()
    image = MIMEImage(image_data)
    image.add_header('Content-ID', '<styleboard>')
    image.add_header('Content-Disposition', 'inline')
    email.attach(image)

    # Add the HTML

    email.attach_alternative(html, "text/html")

    # Indicate that only one of the two types (text vs html) should be rendered

    email.mixed_subtype = "related"
    is_sent = email.send()

    return is_sent

def paypal_return_url(request):

    if PayPal.isSuccessfull(st=request.GET.get('st',''), tx=request.GET.get('tx','')):
        
        try:

            OrderPayment.objects.get(transaction_id=str(request.GET.get('tx','')).strip())
            return redirect('plata_order_success')

        except:
            
            pass
        
        order = shop.order_from_request(request, create=True)
        
        payment = order.payments.model(
            order=order,
            payment_module="cod"
        )
       
        payment.currency = request.GET.get('cc','USD')
        payment.amount = Decimal(request.GET.get('amt','0.00'))
        payment.authorized = datetime.now()
        payment.payment_method = 'PayPal'
        payment.payment_module_key = 'cod'
        payment.module = 'Cash on delivery'
        payment.status = OrderPayment.AUTHORIZED
        payment.transaction_id = request.GET.get('tx','')
        payment.save()
        order.user = request.user if request.user.is_authenticated() else None
        order.paid = Decimal(request.GET.get('amt','0.00'))
        order.status = 40
        order.save()
        order = order.reload()

        return redirect('plata_order_success')

    else:
        request.session['checkout_login_error'] = _('An error occurred while processing your payment through Paypal.')
        return redirect('plata_shop_checkout')

@csrf_exempt
def paypal_ipn(request):

    postData = {} 

    for key, value in request.POST.iteritems():
        postData[key] = value
                
    postData['cmd'] = "_notify-validate"

    result = urllib.urlopen(settings.PAYPAL_IPN_URL, urllib.urlencode(postData)).read()

    if result == "VERIFIED":

        txn_id = request.POST.get('txn_id','')
        custom_data = request.POST.get('custom', '')

        try:
            OrderPayment.objects.get(transaction_id=str(txn_id).strip())
            return HttpResponse('existing')

        except Exception as e:
            pass

        if request.POST.get('payment_status') == 'Completed':

            try:
                data = simplejson.loads(custom_data)

                logr.info('custom data sent to paypal: %s' % data)

                order = Order.objects.get(id=int(data['order_id']))
                payment = order.payments.model(order=order,payment_module="cod")
                order_data = OrderData.objects.get(order=order)

                o_data = simplejson.loads(order_data.data)

                logr.info('order data : %s with order ID %s' % (o_data, order.id ))

                paymentData = {}
                paymentData['delivery_address2'] = o_data['delivery_address2']
                paymentData['billing_address2'] = o_data['billing_address2']
                paymentData['delivery_date'] = o_data['delivery_date']
                paymentData['delivery_state'] = o_data['delivery_state']
                paymentData['billing_state'] = o_data['billing_state']
                paymentData['salutation'] = o_data['salutation']
                paymentData['contact_number'] = o_data['billing_contact_number']

                payment.currency = request.POST.get('mc_currency','USD')
                payment.amount = Decimal(request.POST.get('payment_gross','0.00'))
                payment.authorized = datetime.now()
                payment.payment_method = 'PayPal'
                payment.payment_module_key = 'cod'
                payment.module = 'Cash on delivery'
                payment.status = 40
                payment.transaction_id = txn_id
                payment.data = simplejson.dumps(paymentData)
                payment.save()

                order.user = User.objects.get(id=int(data['user']))
                order.paid = Decimal(request.POST.get('payment_gross','0.00'))
                order.status = 40
                order.notes = o_data['order_notes']
                order.save()
                order.reload()

                emailed = send_email_order(order, order.user, order.notes, paymentData['contact_number'], None)

                logr.info('emailed order confirmation to : %s from order IPN' % order.user.email)

                o_data['ipn_emailed'] = bool(emailed)
                
                order_data.data = simplejson.dumps(o_data)
                
                order_data.save()

            except Exception as e:

                logr.error('error on processing payment via IPN: %s' % e)

    return HttpResponse('recieved')

def cart(request):

    info = {}

    return render_to_response('cart/cart.html', info, RequestContext(request))

def add_to_cart_ajax(request):  
    if request.method == "POST":
        product_id = request.POST.get('prod_id')
        quantity = request.POST.get('quantity',1)
        guests = request.POST.get('guests', 1)
        tables = request.POST.get('tables', 1)
        wedding = request.POST.get('wedding', 1) # edited added weding option -ryan -02152013
        product = get_product(product_id)
        sessionid = request.session.get('cartsession',None)
        if not sessionid:
            sessionid = generate_unique_id()
            request.session['cartsession'] = sessionid

        data = {}
        data['product'] = product.product
        data['sessionid'] = sessionid
        data['quantity'] = quantity
        data['guests'] = guests
        data['tables'] = tables
        data['wedding'] = wedding # edited added weding option -ryan -02152013
        add_to_cart(data)

        # exists = CartTemp.objects.filter(product=product.product,sessionid=sessionid).exists()
        # existsGT = GuestTableTemp.objects.filter(sessionid=sessionid).exists()        

        # if not exists:
        #   cartTemp = CartTemp()
        #   cartTemp.product = product.product
        #   cartTemp.quantity = quantity
        #   cartTemp.sessionid = sessionid
        #   cartTemp.save()

        # if not existsGT:
        #   guestTable = GuestTableTemp()
        #   guestTable.guests = guests
        #   guestTable.tables = tables
        #   guestTable.sessionid = sessionid
        #   guestTable.save()

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
        if not sessionid:
            sessionid = generate_unique_id()
            request.session['cartsession'] = sessionid
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

        except Exception as e:
            # print e
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

"""
def payment(request):
    info = {}

    return render_to_response('plata/payment.html',info,RequestContext(request))
"""