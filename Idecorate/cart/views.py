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
from cart.services import get_product, generate_unique_id, remove_from_cart_temp, add_to_cart

import plata
#from plata.contact.models import Contact
from plata.discount.models import Discount
from plata.shop.models import Order, OrderPayment
from plata.shop.views import Shop
from plata.shop import signals
from django import forms
import re

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
from decimal import Decimal

from django.core.validators import email_re
from django.contrib import auth
from uuid import uuid4
from common.models import Countries

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

        if same_as_billing:
            contact.shipping_same_as_billing = same_as_billing
            contact.save()

        if shipping_address:
            contact.address = shipping_address
            contact.save()

        if billing_address:
            contact.address2 = billing_address
            contact.save()

        #if shipping_address2:
        contact.shipping_address2 = shipping_address2
        contact.save()

        order.data['delivery_address2'] = shipping_address2
        order.save()

        if billing_address2:
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

        if billing_salutation:
            contact.billing_salutation = billing_salutation
            contact.save()

        if shipping_zip_code:
            contact.zip_code = shipping_zip_code
            contact.save()

        if billing_zip_code:
            contact.zip_code2 = billing_zip_code
            contact.save()

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

        if request.POST.get('order-shipping_date') is None:
            if 'delivery_date' in request.session:
                initial['shipping_date'] = request.session['delivery_date']

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
        self.fields['payment_method']           = forms.ChoiceField(label=_("Payment Method"), choices=(('PayPal','PayPal'),('Visa','Visa'),('Mastercard','Mastercard'),('American_Express','American Express'),), required=True,widget=forms.RadioSelect, error_messages={'required':_('Payment Method is a required field.')})
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
        try:
            context.update({'guest_table': self.guest_table})
        except:
            pass
        return self.render(request, 'plata/shop_checkout.html', self.get_context(request, context))
    
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

                        url = settings.PAYDOLLAR_SS_DIRECT_URL
                        params = {}
                        pMethod = request.session.get('order-payment_method','')

                        if pMethod == "Visa":
                            pMethod = "VISA"
                        elif pMethod == "Mastercard":
                            pMethod = "Master"
                        else:
                            pMethod = "AMEX"

                        splittedExpires = str(expires).split("/")

                        params['orderRef'] = str("%34d" % int(order.id)).replace(' ','0')
                        params['amount'] = "%.2f" % order.total
                        params['currCode'] = settings.PAYDOLLAR_CURRENCY
                        params['lang'] = "E"
                        params['merchantId'] = settings.PAYDOLLAR_MERCHANT_ID
                        params['pMethod'] = pMethod
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
                            #print "The payment method is: %s" % dir(order)             
                            return form.process_confirmation()
                            
                            #form = ConfirmationForm(**kwargs) #TEMPORARY ONLY
                    else:
                        form = ConfirmationForm(**kwargs)
        else:
            form = ConfirmationForm(**kwargs)

        paypal = PayPal(cancel_return_url="%s%s" % (settings.PAYPAL_RETURN_URL, reverse('plata_shop_checkout')), return_url="%s%s" % (settings.PAYPAL_RETURN_URL, reverse('paypal_return_url')))
        paypal_orders = order.items.filter().order_by('-id')

        for paypal_order in paypal_orders:
            paypal.addItems(PayPalItem(item_name=paypal_order.name, amount="%.2f" % paypal_order._unit_price, quantity=paypal_order.quantity))  

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
            'contact': thisContact
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
                    print "testing"
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
            #print request.POST
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

                if same_as_billing:
                    billing_address = delivery_address
                    billing_address2 = delivery_address2
                    billing_state = delivery_state
                    billing_city = delivery_city
                    billing_zip_code = delivery_zip_code
                    billing_country = delivery_country

                request.session['order-payment_method'] = request.POST.get('order-payment_method','')
                request.session['order_notes'] = request.POST.get('order-notes','')
                request.session['delivery_address2'] = delivery_address2
                request.session['billing_address2'] = billing_address2
                request.session['delivery_date'] = delivery_date
                request.session['delivery_state'] = delivery_state
                request.session['billing_state'] = billing_state
                request.session['salutation'] = salutation
                request.session['billing_country'] = billing_country
                request.session['shipping_country'] = delivery_country

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
                    billing_last_name=billing_last_name
                )

                """
                added notes
                """
                request.session['notes'] = notes
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

        oData = {}
        oData['delivery_address2'] = request.session['delivery_address2']
        oData['billing_address2'] = request.session['billing_address2']
        oData['delivery_date'] = request.session['delivery_date']
        oData['delivery_state'] = request.session['delivery_state']
        oData['billing_state'] = request.session['billing_state']
        oData['salutation'] = request.session['salutation']

        #try:
        oPayment = OrderPayment.objects.get(order=order)
        oPayment.payment_method = request.session.get('order-payment_method','')
        oPayment.data = simplejson.dumps(oData)
        oPayment.save()
        #except:
        #   pass

        """
        order update note
        """
        notes = request.session.get('notes','')
        order.notes = notes
        order.save()

        st_save_helper(request, order)
        sbid = None

        if 'customer_styleboard' in request.session:
            sbid = request.session.get('customer_styleboard').id

        if 'personalize_id' in request.session:
            print "There's a personalize_id"

        current_user = User.objects.get(id=int(request.user.id))
        send_email_order(order, current_user, self, sbid, notes)
        clear_styleboard_session(request)

        try:
            del request.session['order-payment_method']
            del request.session['delivery_address2']
            del request.session['billing_address2']
            del request.session['delivery_date']
            del request.session['delivery_state']
            del request.session['billing_state']
            del request.session['salutation']
            del request.session['notes']
            del request.session['billing_country']
            del request.session['shipping_country']
        except:
            pass

        return self.render(request, 'plata/shop_order_success.html',
            self.get_context(request, {
                'order': order,
                'progress': 'success',
                }))

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
            print e
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

    order = shop.order_from_request(request, create=True)
    order.items.filter().delete()

    if cart_item.count() > 0:
        guest_table = GuestTableTemp.objects.get(sessionid=sessionid)
        for cart in cart_item:
            try:
                order.modify_item(cart.product, absolute=cart.quantity)
            except Exception as e:
                CartTemp.objects.filter(sessionid=sessionid).delete()
                print "The error is: %s" % e
                return shop.order_new(request)
            #remove_from_cart_temp(cart.id)
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
        print "The cart_items count from view is: %s" % cart_items.count()
        if cart_items.count() > 0:
            for cart in cart_items:
                try:
                    order.modify_item(cart.product, absolute=cart.quantity)
                except:
                    CartTemp.objects.filter(sessionid=sessionid).delete()
                    return shop.order_new(request)

            shop.modify_guest_table(request, guests, tables, order)

        sms = st_man(request, False)

        #request.session['personalize_id'] = styleboard.id
        return redirect('plata_shop_checkout')
    else:
        return redirect('styleboard')

def paypal_return_url(request):

    if PayPal.isSuccessfull(st=request.GET.get('st',''), tx=request.GET.get('tx','')):
        
        try:
            OrderPayment.objects.get(transaction_id=str(request.GET.get('tx','')).strip())
            return redirect('styleboard')
        except:
            pass

        request.session['delivery_address2'] = ''
        request.session['billing_address2'] = ''
        request.session['delivery_date'] = ''
        request.session['delivery_state'] = ''
        request.session['billing_state'] = ''
        request.session['salutation'] = ''
        request.session['order-payment_method'] = 'PayPal'

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

"""
def payment(request):
    info = {}

    return render_to_response('plata/payment.html',info,RequestContext(request))
"""