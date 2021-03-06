from django.contrib.auth.decorators import login_required
from django.shortcuts import HttpResponse, redirect, render_to_response
from django.contrib.auth import authenticate, login, logout
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.template import RequestContext, Context
from django.template.loader import get_template, render_to_string
from django.utils import simplejson
from django.http import HttpResponseNotFound, Http404, HttpResponseRedirect
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.safestring import mark_safe
from django.db import transaction
from django.db.models import Q
from django.contrib.auth.models import User
from django_xhtml2pdf.utils import generate_pdf, render_to_pdf_response
import os
import time
import random

from category.services import get_categories, get_cat, category_tree_crumb, search_category, get_cat_ids
from category.models import Categories
from cart.models import Product, CartTemp, ProductPopularity, GuestTableTemp, ProductPrice, SuggestedProduct, ProductAlternateImage
from cart.services import generate_unique_id, clear_cart_temp, add_to_cart, get_product, get_product_detail, strip_tags
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
from django.core.urlresolvers import reverse
import re
from admin.services import getExtensionAndFileName
from idecorate_settings.models import IdecorateSettings
from admin.models import TextFonts, Embellishments, EmbellishmentsType, HomeInfoGrapics, HomeBanners, HomeBannerImages
from customer.services import get_user_styleboard, get_styleboard_cart_item, get_facebook_friends
import admin
from admin.services import get_home_banners, get_home_banner_images
from embellishments.models import StyleboardTemplateItems 
from customer.models import (CustomerStyleBoard, CustomerProfile, 
                                StyleboardInstruction, StyleboardInstructionCookie, 
                                StyleboardJsonize, WishList,
                                StyleboardItems) #, CustomerFacebookFriends
from customer.services import print_styleboard
from forms import SetPasswordForm, SearchFriendsForm
from social_auth.models import UserSocialAuth
from common.services import set_cookie, IdecorateEmail, render_to_json
from common.forms import NewsletterSubscriberForm
import urllib #urtl_plus(ncode

from django.core.mail import EmailMultiAlternatives
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.core.validators import validate_email
from django.core.exceptions import ValidationError     
import logging
logr = logging.getLogger(__name__)


def home(request):
    info = {}
    items = get_home_banners()
    items = items.order_by('-id')
    lists = []
    for item in items:
        images = get_home_banner_images(item.id)
        images = images.order_by('id')
        lists.append(images)
    
    info['lists'] = lists

    page = request.GET.get('page', 1)
    info['page'] = page

    if page:
        product_list = Product.objects.filter(is_deleted=False, 
                                                is_active=True)[(page-1)*settings.PRODUCT_HOME_NUM_RECORDS:settings.PRODUCT_HOME_NUM_RECORDS]
        styleboard_list = CustomerStyleBoard.objects.all()[(page-1)*settings.STYLEBOARD_HOME_NUM_RECORDS:settings.STYLEBOARD_HOME_NUM_RECORDS]
        inspiration_list = HomeBanners.objects.filter(is_deleted=False)[(page-1)*settings.INSPIRATION_NUM_RECORDS:settings.INSPIRATION_NUM_RECORDS]
        #product_situation_list = ProductAlternateImage.objects.filter(product__is_deleted=False)[(page-1)*settings.PRODUCT_SITUATION_NUM_RECORDS:settings.PRODUCT_SITUATION_NUM_RECORDS]
    else:
        product_list = Product.objects.filter(is_deleted=False, 
                                                is_active=True)[:settings.PRODUCT_HOME_NUM_RECORDS]
        styleboard_list = CustomerStyleBoard.objects.all()[:settings.STYLEBOARD_HOME_NUM_RECORDS]
        inspiration_list = HomeBanners.objects.filter(is_deleted=False)[:settings.INSPIRATION_NUM_RECORDS]
        #product_situation_list = ProductAlternateImage.objects.filter(product__is_deleted=False)[:settings.PRODUCT_SITUATION_NUM_RECORDS]

    #query_list = list(product_list) + list(styleboard_list) + list(inspiration_list) + list(product_situation_list)
    query_list = list(product_list) + list(styleboard_list) + list(inspiration_list)
    random.shuffle(query_list)

    #paginator = Paginator(query_list, settings.PRODUCT_HOME_NUM_RECORDS + settings.STYLEBOARD_HOME_NUM_RECORDS + settings.INSPIRATION_NUM_RECORDS + settings.PRODUCT_SITUATION_NUM_RECORDS)
    paginator = Paginator(query_list, settings.PRODUCT_HOME_NUM_RECORDS + settings.STYLEBOARD_HOME_NUM_RECORDS + settings.INSPIRATION_NUM_RECORDS)
    
    try:
        info['products'] = paginator.page(page)
    except PageNotAnInteger:
        info['products'] = paginator.page(1)    

    try:
        info['infographic'] = HomeInfoGrapics.objects.get(is_active=True)
    except:
        pass

    return render_to_response('interface/home.html',info,RequestContext(request))

 
@csrf_exempt
def load_products_ajax(request):
    html = ''
    if request.method == 'POST':
        page = request.POST.get('page')
        keywords = request.POST.get('keywords', False)
        wishlist = request.POST.get('wishlist', False)
        celebrity_styleboards = request.POST.get('celebrity_styleboards', False)
        
        if page:
            product_offset = (int(page)-1)*settings.PRODUCT_HOME_NUM_RECORDS
            styleboard_offset = (int(page)-1)*settings.STYLEBOARD_HOME_NUM_RECORDS
            inspiration_offset = (int(page)-1)*settings.INSPIRATION_NUM_RECORDS
            #situation_offset = (int(page)-1)*settings.PRODUCT_SITUATION_NUM_RECORDS
            if wishlist:
                wishlist_products = None
                wishlist_styleboards = None
                if request.user.is_authenticated():
                    wishlist_products = WishList.objects.filter(user=request.user,
                                                                object_type='products').values_list('object_id')
                    wishlist_styleboards = WishList.objects.filter(user=request.user,
                                                                    object_type='styleboards').values_list('object_id')
                    wishlist_inspirations = WishList.objects.filter(user=request.user,
                                                                    object_type='inspiration').values_list('object_id')
                    #wishlist_situation = WishList.objects.filter(user=request.user,
                    #                                                object_type='situation').values_list('object_id')
                else:
                    sessionid = request.session.get('sessionid')
                    wishlist_products = WishList.objects.filter(sessionid=sessionid,
                                                                object_type='products').values_list('object_id')
                    wishlist_styleboards = WishList.objects.filter(sessionid=sessionid,
                                                                    object_type='styleboards').values_list('object_id')
                    wishlist_inspirations = WishList.objects.filter(sessionid=sessionid,
                                                                    object_type='inspiration').values_list('object_id')
                    #wishlist_situation = WishList.objects.filter(sessionid=sessionid,
                    #                                                object_type='situation').values_list('object_id')

                product_list = Product.objects.filter(is_deleted=False,
                                        is_active=True,
                                        id__in=wishlist_products)[product_offset:settings.PRODUCT_HOME_NUM_RECORDS+product_offset]
                styleboard_list = CustomerStyleBoard.objects.filter(id__in=wishlist_styleboards)[styleboard_offset:settings.STYLEBOARD_HOME_NUM_RECORDS+styleboard_offset]
                inspiration_list = HomeBanners.objects.filter(is_deleted=False, id__in=wishlist_inspirations)[inspiration_offset:settings.INSPIRATION_NUM_RECORDS+inspiration_offset]
                #situation_list = ProductAlternateImage.objects.filter(product__is_deleted=False, id__in=wishlist_situation)[situation_offset:settings.PRODUCT_SITUATION_NUM_RECORDS+situation_offset]
            elif celebrity_styleboards:
                product_list = []
                styleboard_list = CustomerStyleBoard.objects.filter(active=True)[styleboard_offset:settings.STYLEBOARD_HOME_NUM_RECORDS+styleboard_offset]
                inspiration_list = []
                #situation_list = []
            else:
                if keywords == '':
                    product_list = Product.objects.filter(is_deleted=False, 
                                                            is_active=True)[product_offset:settings.PRODUCT_HOME_NUM_RECORDS+product_offset]
                    styleboard_list = CustomerStyleBoard.objects.all()[styleboard_offset:settings.STYLEBOARD_HOME_NUM_RECORDS+styleboard_offset]
                    inspiration_list = HomeBanners.objects.filter(is_deleted=False)[inspiration_offset:settings.INSPIRATION_NUM_RECORDS+inspiration_offset]
                    #situation_list = ProductAlternateImage.objects.filter(product__is_deleted=False)[situation_offset:settings.PRODUCT_SITUATION_NUM_RECORDS+situation_offset]
                else:
                    product_list = Product.objects.filter(Q(is_deleted=False), 
                                                            Q(is_active=True),
                                                            (Q(name__icontains=keywords) | Q(description__icontains=keywords)))[product_offset:settings.PRODUCT_HOME_NUM_RECORDS+product_offset]                 
                    styleboard_list = CustomerStyleBoard.objects.filter(Q(styleboard_item__deleted=False),
                                                                        (Q(styleboard_item__name__icontains=keywords) | Q(styleboard_item__description__icontains=keywords))
                                                                    )[styleboard_offset:settings.STYLEBOARD_HOME_NUM_RECORDS+styleboard_offset]
                    hbi_list = HomeBannerImages.objects.filter(Q(name__icontains=keywords) | Q(description__icontains=keywords)).values_list('home_banner_id')
                    inspiration_list = HomeBanners.objects.filter(Q(is_deleted=False), Q(id__in=hbi_list))[inspiration_offset:settings.INSPIRATION_NUM_RECORDS+inspiration_offset]
                    #situation_list = ProductAlternateImage.objects.filter(Q(product__is_deleted=False), Q(product__name__icontains=keywords))[situation_offset:settings.PRODUCT_SITUATION_NUM_RECORDS+situation_offset]
                    
        else:
            if wishlist:
                pass
            if celebrity_styleboards:
                pass
            else:
                product_list = Product.objects.filter(is_deleted=False, 
                                                        is_active=True)[:settings.PRODUCT_HOME_NUM_RECORDS]
                styleboard_list = CustomerStyleBoard.objects.filter()[:settings.STYLEBOARD_HOME_NUM_RECORDS]            

        #products = list(product_list) + list(styleboard_list) + list(inspiration_list) + list(situation_list)
        products = list(product_list) + list(styleboard_list) + list(inspiration_list)
        random.shuffle(products)

        html_items = render_to_string('interface/home_items.html', {'products': products} ,RequestContext(request))

    return HttpResponse(html_items)


def getProductPrice(product):
    price = ProductPrice.objects.get(product=product)
    return price._unit_price


@csrf_exempt
def styleboard(request, cat_id=None):   
    """
    check if category is exist
    """
    if cat_id:
        if not get_cat(cat_id):
            return redirect('styleboard')

    sessionid = request.session.get('cartsession',None)
    if not sessionid: 
        session_id = generate_unique_id()
        request.session['cartsession'] = session_id

    info = {}

    idecorateSettings = IdecorateSettings.objects.get(pk=1)
    info['global_default_quantity'] = idecorateSettings.global_default_quantity
    info['global_guest_table'] = idecorateSettings.global_table 

    info['mode'] = 'styleboard'
    search = request.POST.get('search',None)
    if search:
        info['keyword'] = search
        info['keyword_cat'] = 0
        search_result_cat = search_category(search)
        if search_result_cat:
            cat_id = search_result_cat.id
            info['keyword_cat'] = cat_id
        info['mode'] = 'search' 
        info['category_count'] = 0
    else:
        categories = get_categories(cat_id)
        if categories.count() > 0:
            info['categories'] = categories

        info['category_count'] = categories.count()

    if not cat_id:
        cat_id = 0
    info['cat_id'] = cat_id

    product_positions = request.session.get('product_positions', None)

    if product_positions:
        info['product_positions'] = mark_safe(str(product_positions))
        #del request.session['product_positions']
    else:
        info['product_positions'] = mark_safe("''")

    info['max_emb_size'] = settings.MAX_UPLOAD_EMBELLISHMENT_IMAGE_SIZE
    info['text_items'] = TextFonts.objects.filter(is_active=True, is_deleted=False)

    """
    save styleboard personalize or modify
    
    try:
        del request.session['customer_styleboard']
    except:
        pass
    
    try:
        del request.session['cartsession']
    except:
        pass
    """

    sms = st_man(request)

    if sms['sbid']:

        request.session['sbid'] = sms['sbid']

    info.update(sms)
    
    template_view = request.GET.get('template')

    if template_view :

        info['view_template'] = template_view

    return render_to_response('interface/styleboard2.html', info,RequestContext(request))

def st_man(request, needToClear=True):
    info = {}
    sbid = request.GET.get('sbid',None)

    info['sbid'] = 0

    if not sbid:
        if request.method == "POST":
            sbid = request.POST.get('sid', None)

    if sbid:

        if not get_user_styleboard(None, sbid):
            
            raise Http404

        info['sbid'] = sbid

        session_sbid = request.session.get('sbid', None)

        if session_sbid != sbid :

            personalize_styleboard = get_user_styleboard(None, sbid)

            if personalize_styleboard:

                if personalize_styleboard.user.id:

                    if needToClear:
                        clear_styleboard_session(request)

                    info['save_styleboard']         = personalize_styleboard
                    info['personalize_item']        = mark_safe(personalize_styleboard.styleboard_item.item.replace("'","\\'"))
                    info['global_default_quantity'] = personalize_styleboard.styleboard_item.item_guest
                    info['global_guest_table']      = personalize_styleboard.styleboard_item.item_tables            
                    
                    if request.user.is_authenticated():

                        if int(personalize_styleboard.user.id) == int(request.user.id):
                            
                            try:
                                del request.session['personalize_id']
                            except:
                                pass

                            request.session['customer_styleboard'] = personalize_styleboard

                        else:

                            try:
                                del request.session['customer_styleboard']
                            except:
                                pass
                                
                            request.session['personalize_id'] = personalize_styleboard.id

                    else:
                        
                        request.session['personalize_id_logged_out']    = personalize_styleboard.id
                        request.session['personalize_styleboard']       = personalize_styleboard                    

    return info

def get_product_price(product):
        product_details = ProductPrice.objects.get(product=product)
        return product_details._unit_price

def print_styleboard_view(request,is_pdf):

    info = {}

    is_pdf = bool(int(is_pdf))

    data = ''

    sessionid = request.session.get('cartsession',None)

    info['cart_list'] = ''
    info['default_multiplier'] = 0

    if sessionid:
        try:
            info['cart_list'] = CartTemp.objects.filter(sessionid=sessionid)
            info['default_multiplier'] = GuestTableTemp.objects.get(sessionid=sessionid)
            info['total_price'] = mark_safe("%.2f" % (sum((get_product_price(item.product) * item.quantity) for item in info['cart_list'])))

            jsonize = StyleboardJsonize.objects.get(sessionid=sessionid)
            data = jsonize.data

        except Exception as e:
            print e

    if is_pdf :

        filename = print_styleboard(data, 850, 538, True)
        styleboard = '%sstyleboards/%s' % (settings.MEDIA_URL,filename)
        info['styleboard'] = styleboard

        result = render_to_pdf_response('interface/styleboard_pdf.html', info, 'styleboard_%s.pdf' % ( str(time.time()).replace('.','_') ))

        path = "%s%s%s" % (settings.MEDIA_ROOT, "styleboards/", filename)
        os.unlink(path)

    else:

        styleboard = '/styleboard/generate_printable_styleboard/850/538/?get=%s' % ( str(time.time()).replace('.','_') )
        info['styleboard'] = styleboard

        result = render_to_response('interface/styleboard_print.html', info,RequestContext(request))

    return result


def styleboard_email(request):

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

            is_sent = send_styleboard_email(request, mailto_list, str(name))

            if is_sent:
                info['styleboard_email_sent'] = "Email sent"
            else:
                info['styleboard_email_sent'] = "Sending email failed. Please try again."

    else:

        if request.user.is_authenticated():

            info['name_post'] =  '%s %s' % (request.user.first_name, request.user.last_name)

    return render_to_response('interface/iframe/styleboard_email.html', info,RequestContext(request))


def send_styleboard_email(request,mailto_list, sender):

    info = {}

    data = ''

    sessionid = request.session.get('cartsession',None)

    info['cart_list'] = ''
    info['default_multiplier'] = 0

    if sessionid:
        try:
            info['cart_list'] = CartTemp.objects.filter(sessionid=sessionid)
            info['default_multiplier'] = GuestTableTemp.objects.get(sessionid=sessionid)
            info['total_price'] = mark_safe("%.2f" % (sum((get_product_price(item.product) * item.quantity) for item in info['cart_list'])))

            jsonize = StyleboardJsonize.objects.get(sessionid=sessionid)
            data = jsonize.data

        except Exception as e:
            print e

    filename = print_styleboard(data, 560, 335, True)
    styleboard = "%s%s%s" % (settings.MEDIA_ROOT, "styleboards/", filename)

    info['media_root'] = '%s/%s' % (settings.IDECORATE_HOST,settings.MEDIA_URL )
    info['sender'] = sender.title()

    html = render_to_string('interface/styleboard_email.html', info)

    # top level container, defines plain text version

    email = EmailMultiAlternatives(subject="Styleboard iDecorateWeddings.com", body="this email is generated by www.idecorateweddings.com", from_email="noreply@idecorateweddings.com", to=mailto_list)
    
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

    path = "%s%s%s" % (settings.MEDIA_ROOT, "styleboards/", filename)
    os.unlink(path)

    return is_sent
    

def styleboard_product_ajax(request):
    if request.method == "POST":
        cat_id = request.POST.get('cat_id',None)

        product_list = Product.objects.filter(categories__id=cat_id, is_active=True, is_deleted=False)
        product_list = product_list.order_by('ordering')        
        product_counts = product_list.count()       
        offset = request.GET.get('offset',25)

        if offset == 'Infinity':
            offset = 25

        paginator = Paginator(product_list, offset)
        page = request.GET.get('page')
        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)

        reponse_data = {}

        json_data = serializers.serialize("json", products, fields=('id','name','original_image_thumbnail','sku'))
        reponse_data['data'] = json_data
        reponse_data['page_number'] = products.number
        reponse_data['num_pages'] = products.paginator.num_pages
        reponse_data['product_counts'] = product_counts

        return HttpResponse(simplejson.dumps(reponse_data), mimetype="application/json")
    return HttpResponseNotFound()

def styleboard_ajax(request):
    if request.method == "POST":
        cat_id = request.POST.get('cat_id',None)
        if cat_id == '':
            cat_id = None
        items = None
        categories = get_categories(cat_id)     
        reponse_data = {}
        if categories.count() > 0:
            categories = categories.order_by('order')
            reponse_data['data'] = serializers.serialize("json", categories, fields=('id','name','thumbnail'))
        else:
            product_list = Product.objects.filter(categories__id=cat_id, is_active=True)
            product_counts = product_list.count()
            product_list = product_list.order_by('ordering')
            offset = request.GET.get('offset',25)

            if offset == 'Infinity':
                offset = 25

            paginator = Paginator(product_list, offset)
            page = request.GET.get('page')
            try:
                products = paginator.page(page)
            except PageNotAnInteger:
                products = paginator.page(1)
            except EmptyPage:
                products = paginator.page(paginator.num_pages)
                
            json_data = serializers.serialize("json", products, fields=('id','name','original_image_thumbnail','sku'))
            reponse_data['data'] = json_data
            reponse_data['page_number'] = products.number
            reponse_data['num_pages'] = products.paginator.num_pages
            reponse_data['product_counts'] = product_counts

        return HttpResponse(simplejson.dumps(reponse_data), mimetype="application/json")
    else:
        return HttpResponseNotFound()

def get_category_tree_ajax(request):
    if request.method == "POST":
        cat_id = request.POST.get('cat_id',None)
        if cat_id == '':
            cat_id = None
        cat_tree = category_tree_crumb(cat_id)
        return HttpResponse(cat_tree)
    else:
        return HttpResponseNotFound()

@csrf_exempt
def get_product_original_image(request):    
    if request.method == "POST":

        ret = {}

        product_id = request.POST.get('product_id')

        product = Product.objects.get(id=int(product_id))
        ret['original_image'] = product.original_image
        ret['no_background'] = product.no_background
        ret['default_quantity'] = product.default_quantity
        ret['guest_table'] = product.guest_table.name

        img = Image.open("%s%s%s" % (settings.MEDIA_ROOT, "products/", product.original_image))
        

        width, height = img.size

        ret['original_image_w'] = width
        ret['original_image_h'] = height

        img = Image.open("%s%s%s" % (settings.MEDIA_ROOT, "products/", product.no_background))
        width, height = img.size

        ret['no_background_w'] = width
        ret['no_background_h'] = height
        return HttpResponse(simplejson.dumps(ret), mimetype="application/json")

def crop(request, id):
    info = {}

    info['filename'] = "%s?filename=%s" % (reverse('crop_view'), re.sub(r'\?[0-9].*','', str(id)).replace('/',''))
    info['file_only'] = re.sub(r'\?[0-9].*','', str(id)).replace('/','')

    task = request.GET.get('task',None)
    otherdata = request.GET.get('otherdata',None)
    dimensions = request.GET.get('dimensions', None)

    info['pre_task'] = task if task else ''
    info['pre_otherdata'] = otherdata if otherdata else ''
    info['pre_dimensions'] = dimensions if dimensions else ''

    return render_to_response('interface/iframe/crop.html', info,RequestContext(request))

def get_product_details(request):
    if request.method == 'POST':
        product_id                                  = request.POST.get('prod_id')
        product                                     = get_product(product_id)
        product_detail                              = get_product_detail(product_id)
        description_raw                             = product.product.description;
        desc_striped_tags                           = strip_tags(description_raw);      
        reponse_data                                = {}
        reponse_data['id']                          = product.product.id
        reponse_data['original_image_thumbnail']    = product.product.original_image_thumbnail
        reponse_data['sku']                         = product.product.sku
        reponse_data['name']                        = product.product.name
        reponse_data['description']                 = description_raw
        reponse_data['size']                        = product_detail.size
        reponse_data['default_quantity']            = product.product.default_quantity
        reponse_data['price']                       = product._unit_price
        reponse_data['currency']                    = product.currency
        reponse_data['original_image']              = product.product.original_image
        guest_table = 'Table'
        try:
            guest_table = product.product.guest_table.name
        except:
            pass
        reponse_data['guest_table'] = guest_table

        return HttpResponse(simplejson.dumps(reponse_data), mimetype="application/json")
    else:
        return HttpResponseNotFound()

# @transaction.commit_manually
@csrf_exempt
def set_product_positions(request):
    ret = ""

    if request.method == 'POST':

        try:

            obj_counter             = request.POST.get('obj_counter','')
            unique_identifier       = request.POST.get('unique_identifier','')
            changes_counter         = request.POST.get('changes_counter','')
            product_objects         = request.POST.get('product_objects','')
            embellishment_objects   = request.POST.get('embellishment_objects','')
            template_objects        = request.POST.get('template_objects','')
            action_url              = request.POST.get('action_url','')
            total                   = request.POST.get('total','')
            quantity                = request.POST.get('quantity','')
            selected_prev_prod_qty  = request.POST.get('selected_prev_prod_qty','')
            buy_table_html          = request.POST.get('buy_table_html','')
            tables                  = request.POST.get('tables','')
            guests                  = request.POST.get('guests','')
            styleboard_json         = request.POST.get('styleboard_json', '')

            request.session['product_positions'] = {
                'obj_counter':str(obj_counter),
                'unique_identifier': str(unique_identifier),
                'changes_counter': str(changes_counter),
                'product_objects':str(product_objects),
                'embellishment_objects': str(embellishment_objects),
                'template_objects': str(template_objects),
                'action_url': str(action_url),
                'total': str(total),
                'quantity': str(quantity),
                'selected_prev_prod_qty': str(selected_prev_prod_qty),
                'buy_table_html': str(buy_table_html),
                'tables': str(tables),
                'guests': str(guests)
            }

        except Exception as e:
            
            print e

        sessionid = request.session.get('cartsession', None)

        try:
            jsonize = StyleboardJsonize.objects.get(sessionid=sessionid)

        except :
            jsonize = StyleboardJsonize()

        jsonize.data = styleboard_json
        jsonize.sessionid = sessionid
        jsonize.save()
        
        ret = obj_counter
        
    return HttpResponse(ret)
    
def styleboard2(request, cat_id=None):

    """
    check if category is exist
    """
    if cat_id:
        if not get_cat(cat_id):
            return redirect('styleboard')

    sessionid = request.session.get('cartsession',None)
    if not sessionid: 
        session_id = generate_unique_id()
        request.session['cartsession'] = session_id

    info = {}

    idecorateSettings = IdecorateSettings.objects.get(pk=1)
    info['global_default_quantity'] = idecorateSettings.global_default_quantity
    info['global_guest_table'] = idecorateSettings.global_table 

    info['mode'] = 'styleboard'
    search = request.POST.get('search',None)
    if search:
        info['keyword'] = search
        info['keyword_cat'] = 0
        search_result_cat = search_category(search)
        if search_result_cat:
            cat_id = search_result_cat.id
            info['keyword_cat'] = cat_id
        info['mode'] = 'search' 
        info['category_count'] = 0
    else:
        categories = get_categories(cat_id)
        if categories.count() > 0:
            info['categories'] = categories

        info['category_count'] = categories.count()

    if not cat_id:
        cat_id = 0
    info['cat_id'] = cat_id

    product_positions = request.session.get('product_positions', None)

    if product_positions:
        info['product_positions'] = mark_safe(str(product_positions))
        #del request.session['product_positions']
    else:
        info['product_positions'] = mark_safe("''")

    return render_to_response('interface/styleboard2.html', info,RequestContext(request))

def crop_view(request):

    filename = request.GET.get('filename','')

    img = Image.open("%s%s%s" % (settings.MEDIA_ROOT, "products/", filename))
    imgBackground = Image.new('RGBA', (400,400), (255, 255, 255, 0))
    imgBackground.paste(img, ((400 - img.size[0]) / 2, (400 - img.size[1]) /2 ))
    #newImg = imgBackground.crop(((400 - img.size[0]) / 2, (400 - img.size[1]) /2 , ((400 - img.size[0]) / 2) + img.size[0], ((400 - img.size[1]) / 2) + img.size[1]))

    response = HttpResponse(mimetype="image/png")
    #newImg.save(response, "PNG")
    imgBackground.save(response, "PNG")
    return response


def cropped(request):

    filename = request.GET.get('filename')

    img = Image.open("%s%s%s" % (settings.MEDIA_ROOT, "products/", filename))
    back = Image.new('RGBA', (400,400), (255, 255, 255, 0))
    back.paste(img, ((400 - img.size[0]) / 2, (400 - img.size[1]) /2 ))

    poly = Image.new('RGBA', (settings.PRODUCT_WIDTH,settings.PRODUCT_HEIGHT), (255, 255, 255, 0))
    pdraw = ImageDraw.Draw(poly)

    dimensionList = []
    splittedPosts = request.GET.get('dimensions').split(',')

    if request.GET.get('task') == 'poly':
        for splittedPost in splittedPosts:
            spl = splittedPost.split(':')
            dimensionList.append((float(spl[0]),float(spl[1])))

        pdraw.polygon(dimensionList,fill=(255,255,255,255),outline=(255,255,255,255))

    elif request.GET.get('task') == 'rect':
        for splittedPost in splittedPosts:
            dimensionList.append(float(splittedPost))
        pdraw.rectangle(dimensionList,fill=(255,255,255,255),outline=(255,255,255,255))


    poly.paste(back,mask=poly)
    response = HttpResponse(mimetype="image/png")

    newImg = poly.crop(((400 - img.size[0]) / 2, (400 - img.size[1]) /2 , ((400 - img.size[0]) / 2) + img.size[0], ((400 - img.size[1]) / 2) + img.size[1]))
    
    """ 
    splittedName = getExtensionAndFileName(filename)

    if splittedName[1] == '.jpg':
        newImg.save(response, "JPEG")
    else:   
        newImg.save(response, "PNG")
    """
    newImg.save(response, "PNG")
    return response

def search_suggestions(request):
    if request.is_ajax():
        keyword = request.GET.get('term',None)
        if keyword:
            products = Product.objects.filter(Q(name__icontains=keyword) | Q(description__icontains=keyword), is_active=True, is_deleted=False).order_by('-id')[:7]         
            categories = Categories.objects.filter(name__icontains=keyword, deleted=False).order_by('-created')[:7]

            results = []

            for prod in products:
                prod_json = {}
                prod_json['id'] = prod.id
                prod_json['label'] = prod.name
                prod_json['category'] = "Products"
                results.append(prod_json)

            for cat in categories:
                cat_json = {}
                cat_json['id'] = cat.id
                cat_json['label'] = cat.name
                cat_json['category'] = "Category"
                results.append(cat_json)

            return HttpResponse(simplejson.dumps(results), mimetype="application/json")     
    else:
        return HttpResponseNotFound()

def search_products(request):
    if request.method == "POST":
        cat_id = request.POST.get('cat_id',None)
        search_keyword = request.POST.get('search_keyword',None)

        if cat_id != '0':
            cat_ids = get_cat_ids(cat_id)
            product_list = Product.objects.filter(categories__id__in=cat_ids, is_active=True, is_deleted=False, categories__deleted=0)
            product_list = product_list.order_by('ordering').distinct().order_by('sku')
        else:
            """
            keywords = search_keyword.split(' ')

            q = None
            for k in keywords:

                if k.strip() != "":
                    if q is not None:
                        q.add(Q(name__icontains=k), Q.OR)
                    else:
                        q = Q(name__icontains=k)

            for l in keywords:
                if l.strip() != "":
                    if q is not None:
                        q.add(Q(description__icontains=l), Q.OR)
                    else:
                        q = Q(description__icontains=l)
            """
            if search_keyword.strip():
                q = Q(name__icontains=search_keyword.strip())
                #q.add(Q(description__icontains=search_keyword.strip()), Q.OR)

            cats_ids = []
            categories = Categories.objects.filter(name__icontains=search_keyword, deleted=False)
            if categories.count() > 0:
                for cat in categories:
                    cats_ids += get_cat_ids(cat.id)
                q.add(Q(categories__id__in=cats_ids), Q.OR)

            product_list = Product.objects.filter(q).distinct()
            product_list = product_list.filter(categories__deleted=0, is_active=True, is_deleted=False)
            product_list = product_list.distinct().order_by('sku')
        product_counts = product_list.count()       
        offset = request.GET.get('offset',25)

        if offset == 'Infinity':
            offset = 25

        paginator = Paginator(product_list, offset)
        page = request.GET.get('page')
        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)

        reponse_data = {}

        json_data = serializers.serialize("json", products, fields=('id','name','original_image_thumbnail','sku'))
        reponse_data['data'] = json_data
        reponse_data['page_number'] = products.number
        reponse_data['num_pages'] = products.paginator.num_pages
        reponse_data['product_counts'] = product_counts

        return HttpResponse(simplejson.dumps(reponse_data), mimetype="application/json")
    return HttpResponseNotFound()

def generate_text(request):
    #parameters
    font_size = request.GET.get('font_size','')
    image_text = request.GET.get('font_text','')
    font_color = request.GET.get('font_color','')
    font_thumbnail = request.GET.get('font_thumbnail','0')
    font_id = request.GET.get('font_id','')

    try:
        fontObj = TextFonts.objects.get(id=int(font_id))

        font_color = (int(font_color[0:3]), int(font_color[3:6]), int(font_color[6:9]))
        #load font with size
        font = ImageFont.truetype("%s%s%s" % (settings.MEDIA_ROOT, "fonts/", fontObj.font), int(font_size))
        
        image_text = image_text.replace("\r", "")

        splittedTexts = image_text.split("\n")
        totalHeight = 0
        upperWidth = 0
        heightList = [0]


        #compute the final width and height first
        for splittedText in splittedTexts:
            textSize = font.getsize(splittedText)
            totalHeight += textSize[1]
            heightList.append(totalHeight)

            if upperWidth == 0:
                upperWidth = textSize[0]
            else:
                if textSize[0] > upperWidth:
                    upperWidth = textSize[0]

        #image with background transparent
        img = Image.new("RGBA", (upperWidth, totalHeight), (255,255,255, 0))

        #create draw object 
        draw = ImageDraw.Draw(img)

        #draw the text
        ctr = 0

        for splittedText in splittedTexts:
            #draw text
            draw.text((0,heightList[ctr]), splittedText, font_color, font=font)
            ctr += 1

        if font_thumbnail == "0":
            #not thumbnail
            response = HttpResponse(mimetype="image/png")
            img.save(response, "PNG")
        else:
            #create thumbnail 
            img.thumbnail((int(font_size),int(font_size)),Image.ANTIALIAS)
            bgImg = Image.new('RGBA', (int(font_size),int(font_size)), (255, 255, 255, 0))
            bgImg.paste(img,((int(font_size) - img.size[0]) / 2, (int(font_size) - img.size[1]) / 2))

            response = HttpResponse(mimetype="image/jpg")
            bgImg.save(response, "JPEG")
    except:
        img = Image.open("%s%s" % (settings.MEDIA_ROOT, "images/error_logo.jpg")).convert("RGBA")
        if font_thumbnail == "0":
            response = HttpResponse(mimetype="image/png")
            img.save(response, "PNG")
        else:
            response = HttpResponse(mimetype="image/jpg")
            img.thumbnail((settings.EMBELLISHMENT_THUMBNAIL_WIDTH, settings.EMBELLISHMENT_THUMBNAIL_HEIGHT), Image.ANTIALIAS)
            img.save(response, "JPEG")


    return response

def generate_embellishment(request):

    embellishment_id = request.GET.get('embellishment_id',0)
    embellishment_color = request.GET.get('embellishment_color','')
    embellishment_thumbnail = request.GET.get('embellishment_thumbnail','0')
    embellishment_size = request.GET.get('embellishment_size','')

    response = HttpResponse(mimetype="image/png")

    directory = ""
    retImage = None

    try:

        embellishment_color = (int(embellishment_color[0:3]), int(embellishment_color[3:6]), int(embellishment_color[6:9]))

        embObj = Embellishments.objects.get(id=int(embellishment_id))

        if embObj.e_type.id == 1:
            directory = "images"
        elif embObj.e_type.id == 2:
            directory = "textures"
        elif embObj.e_type.id == 3:
            directory = "patterns"
        elif embObj.e_type.id == 4:
            directory = "shapes"
        elif embObj.e_type.id == 5:
            directory = "borders"

        img = Image.open("%s%s%s" % (settings.MEDIA_ROOT, "embellishments/%s/" % directory, embObj.image)).convert("RGBA")
        newImg = Image.new("RGBA", img.size, embellishment_color)
        r, g, b, alpha = img.split()

        if embObj.e_type.id == 1 or embObj.e_type.id == 5:
            retImage = img
        elif embObj.e_type.id == 3:
            newImg.paste(img, mask=b)
            retImage = newImg
        elif embObj.e_type.id == 2 or embObj.e_type.id == 4:
            img.paste(newImg, mask=alpha)
            retImage = img 

        if embellishment_thumbnail == "0":
            #not thumbnail
            retImage.save(response, "PNG")
        else:
            #return thumbnail
            retImage.thumbnail((int(embellishment_size),int(embellishment_size)),Image.ANTIALIAS)
            bgImg = Image.new('RGBA', (int(embellishment_size),int(embellishment_size)), (255, 255, 255, 0))
            bgImg.paste(retImage,((int(embellishment_size) - retImage.size[0]) / 2, (int(embellishment_size) - retImage.size[1]) / 2))
            bgImg.save(response, "PNG")

    except Exception as e:
        print "Error generating image: %s" % e
        img = Image.open("%s%s" % (settings.MEDIA_ROOT, "images/error_logo.jpg")).convert("RGBA")
        if embellishment_thumbnail == "0":
        
            img.save(response, "PNG")
        else:
            img.thumbnail((settings.EMBELLISHMENT_THUMBNAIL_WIDTH, settings.EMBELLISHMENT_THUMBNAIL_HEIGHT), Image.ANTIALIAS)
            img.save(response, "PNG")

    return response

def clear_styleboard_session(request):
    try:
        del request.session['customer_styleboard']
    except:
        pass

    try:        
        clear_cart_temp(request.session['cartsession'])
        del request.session['cartsession']
    except:
        pass

    try:
        del request.session['product_positions']
    except:
        pass

    try:
        del request.session['personalize_id']
    except:
        pass

    try:
        del request.session['style_board_in_session']
    except:
        pass

    try:
        del request.session['personalize_id_logged_out']
    except:
        pass

    try:        
        del request.session['sbid']
    except:
        pass
    try:        
        del request.session['save_template']
    except:
        pass

def new_styleboard(request):
    clear_styleboard_session(request)
    return redirect('styleboard')

@csrf_exempt
def get_embellishment_items(request):
    if request.is_ajax():
        typ = request.POST['type']
        offset = request.GET.get('offset',25)       
        if offset == 'Infinity':
            offset = 25
        page = request.GET.get('page')
        if typ != 'text':
            embellishment_items = Embellishments.objects.filter(e_type__id=typ, is_active=True, is_deleted=False)

            item_counts = embellishment_items.count()
            paginator = Paginator(embellishment_items, offset)          
            try:
                embellishments = paginator.page(page)
            except PageNotAnInteger:
                embellishments = paginator.page(1)
            except EmptyPage:
                embellishments = paginator.page(paginator.num_pages)

            json_embellishments = serializers.serialize("json", embellishments, fields=('id','description'))
            response_data = {}
            response_data['data'] = json_embellishments
            response_data['page_number'] = embellishments.number
            response_data['num_pages'] = embellishments.paginator.num_pages
            response_data['product_counts'] = item_counts
            response_data['type'] = EmbellishmentsType.objects.get(id=typ).name
        else:
            text_items = TextFonts.objects.filter(is_active=True, is_deleted=False)
            text_counts = text_items.count()
            paginator = Paginator(text_items, offset)
            page = request.GET.get('page')
            try:
                texts = paginator.page(page)
            except PageNotAnInteger:
                texts = paginator.page(1)
            except EmptyPage:
                texts = paginator.page(paginator.num_pages)

            json_data = serializers.serialize("json", texts, fields=('id','description'))
            response_data = {}
            response_data['data'] = json_data
            response_data['page_number'] = texts.number
            response_data['num_pages'] = texts.paginator.num_pages
            response_data['product_counts'] = text_counts
            response_data['type'] = 'Text'

        return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")

    else:
        return HttpResponseNotFound()

@csrf_exempt
def get_personalize_cart_items(request):
    if request.is_ajax():
        id = request.GET.get('id',None)
        cart_items = get_styleboard_cart_item(None,id)
        sessionid = request.session.get('cartsession',None)
        if not sessionid:
            sessionid = generate_unique_id()
            request.session['cartsession'] = sessionid
        
        responsedata = []
        for cart in cart_items:
            datas = {}
            product = get_product(cart.product.id)
            data = {}
            data['product'] = product.product
            data['sessionid'] = sessionid
            data['quantity'] = cart.quantity
            data['guests'] = cart.styleboard_item.item_guest
            data['tables'] = cart.styleboard_item.item_tables
            data['wedding'] = 1
            add_to_cart(data)
            datas['price'] = product._unit_price
            datas['quatity'] = cart.quantity
            datas['sub_total'] = product._unit_price*cart.quantity
            datas['name'] = product.product.name
            datas['original_image_thumbnail'] = product.product.original_image_thumbnail
            datas['default_quantity'] = product.product.default_quantity
            datas['currency'] = product.currency
            datas['id'] = product.product.id
            try:
                guest_table = product.product.guest_table.name
            except:
                pass
            datas['guest_table'] = guest_table
            responsedata.append(datas)

        return HttpResponse(simplejson.dumps(responsedata), mimetype="application/json")        
    else:
        return HttpResponseNotFound()

def set_password_user(request, param):
    info = {}
    form = SetPasswordForm()

    prof = None

    try:
        prof = CustomerProfile.objects.get(hash_set_password=param)

    except:
        pass

    if not prof:
        raise Http404


    if request.method == "POST":
        form = SetPasswordForm(request.POST)

        if form.is_valid():

            prof.user.username = prof.user.email
            prof.user.set_password(form.cleaned_data['password'])
            prof.user.save()

            prof.hash_set_password = ""
            prof.save()

            return redirect('home')

    info['form'] = form
    return render_to_response('interface/set_password.html', info,RequestContext(request))

@csrf_exempt
def get_template_details(request):
    if request.method == "POST":
        id = request.POST['id']
        try:
            template_details = StyleboardTemplateItems.objects.get(id=id)
            return HttpResponse(template_details.item)
        except:
            return HttpResponse('0')
    else:
        return HttpResponseNotFound()

def checkout_login(request):
    if request.method == 'POST':
        user = authenticate(username=request.POST.get('checkout_email',''), password=request.POST.get('checkout_password',''))
        if user is not None:
            if user.is_active:
                login(request, user)
            else:
                #disabled user
                request.session['checkout_login_error'] = 'Sorry this account is disabled.'
        else:
            #invalid login
            request.session['checkout_login_error'] = 'Sorry we could not verify your username and password.'

        return redirect('plata_shop_checkout')
    else:
        return redirect('home')

def invite_friends(request):
    info = {}
    associated = False
    fb_auth_error = ''
    user_fb = None
    fb_friends = []
    page_fb = 0
    per_page_fb = settings.FACEBOOK_INVITE_FRIENDS_PER_PAGE
    search_form_fb = SearchFriendsForm()
    friend_name = ''
    access_token = ''

    if 'fb_auth_error' in request.session:
        fb_auth_error = request.session.get('fb_auth_error')
        del request.session['fb_auth_error']

    try:
        user_fb = UserSocialAuth.objects.get(user__id=request.user.id, provider='facebook')
        associated = True
    except:
        pass
        #CustomerFacebookFriends.objects.filter(user__id=request.user.id).delete()

    if request.method == 'POST':
        search_form_fb = SearchFriendsForm(request.POST)

        if search_form_fb.is_valid() and user_fb:
            friend_name = search_form_fb.cleaned_data['search_name']

    if user_fb:
        access_token = user_fb.tokens['access_token']
        fb_api = get_facebook_friends(access_token, friend_name, per_page_fb, page_fb)

        if 'data' in fb_api:
            fb_friends = fb_api['data']

    info['page_fb'] = page_fb
    info['per_page_fb'] = per_page_fb
    info['friend_name'] = friend_name
    info['search_form_fb'] = search_form_fb
    info['fb_friends'] = fb_friends
    info['friends_count'] = len(fb_friends)
    info['associated'] = associated
    info['fb_auth_error'] = fb_auth_error
    
    return render_to_response('customer/invite_friends.html', info,RequestContext(request))

@csrf_exempt
def invite_friends_content(request):
    info = {}
    fb_friends = []
    access_token = ''
    user_fb = None

    if request.method == "POST":
        page = request.POST.get('page','0')
        per_page = request.POST.get('per_page',str(settings.FACEBOOK_INVITE_FRIENDS_PER_PAGE))
        friend_name = request.POST.get('friend_name','')

        try:
            user_fb = UserSocialAuth.objects.get(user__id=request.user.id, provider='facebook')

            if user_fb:
                access_token = user_fb.tokens['access_token']
                fb_api = get_facebook_friends(access_token, friend_name, per_page, page)

                if 'data' in fb_api:
                    fb_friends = fb_api['data']

        except:
            
            pass
        

        """
        fb_friends = CustomerFacebookFriends.objects.filter(user__id=request.user.id, friend_name__icontains=friend_name)
        paginator = Paginator(fb_friends, 15)

        try:
            fb_friends = paginator.page(page)
        except PageNotAnInteger:
            fb_friends = paginator.page(1)
        except EmptyPage:
            fb_friends = paginator.page(paginator.num_pages)
        """

    info['fb_friends'] = fb_friends
    return render_to_response('customer/invite_friends_content.html', info,RequestContext(request))

def ideas(request):
    info = {}
    styleboards = CustomerStyleBoard.objects.filter(active=True).order_by('-created')

    paginator = Paginator(styleboards, 10)
    page = request.GET.get('page','')

    try:
        styleboards = paginator.page(page)
    except PageNotAnInteger:
        styleboards = paginator.page(1)
    except EmptyPage:
        styleboards = paginator.page(paginator.num_pages)

    info['styleboards'] = styleboards

    return render_to_response('interface/ideas.html', info,RequestContext(request))

@csrf_exempt
def save_styleboard_to_session(request):

    if request.method == "POST":
        
        djsn    = request.POST.get('djsn','')
        guest   = request.POST.get('guest','')
        table   = request.POST.get('table','')
        wedding = request.POST.get('wedding','')
        bwsr    = request.POST.get('bwsr','')

        style_board_in_session = {
            'djsn':djsn,
            'guest':guest,
            'table':table,
            'wedding':wedding,
            'bwsr':bwsr
        }

        request.session['style_board_in_session'] = style_board_in_session

        json_value = simplejson.dumps(style_board_in_session)

    return HttpResponse(json_value)

@csrf_exempt
def clear_session_sbid(request):

    if request.method == 'POST':

        try:        
            del request.session['sbid']
        except:
            pass

        return HttpResponse(request.session.get('sbid'))

    else:
        sbid = request.GET.get('sbid', None)

        try:        
            del request.session['sbid']
        except:
            pass

        return redirect("%s%s" % (reverse('styleboard'), "?sbid=%s" % sbid))

@csrf_exempt
def get_user_email(request):
    
    if request.method == 'POST':

        user_id = request.POST.get('user')

        if user_id or str(hbid).isdigit():

            user = User.objects.get(id=int(user_id))

            if user :

                return HttpResponse(user.email)

        else:

            return HttpResponse('false')

@csrf_exempt
def instruction_tag(request):

    if request.method == 'POST':

        user_id = int(request.POST.get('user'))

        # session_instruction = request.session.get('instruction_tag')

        instruction_cookie = request.COOKIES.get('instruction_cookie') 

        instruction_in_cookie = ""

        if instruction_cookie :
            
            try:
                instruction_in_cookie = StyleboardInstructionCookie.objects.get(id=int(instruction_cookie))
            except:

                pass


        if user_id and user_id != 0:

            if instruction_in_cookie and instruction_in_cookie != "":

                data = simplejson.loads(instruction_in_cookie.data)

                try:
                    user = User.objects.get(id=user_id)

                    user_instruction = StyleboardInstruction.objects.get(user=user)

                    for instruction, value in data.iteritems():

                        if not getattr(user_instruction, instruction):
                            
                            setattr(user_instruction,instruction,value)

                    user_instruction.save()

                except:

                    user = User.objects.get(id=user_id)

                    user_instruction = StyleboardInstruction()

                    user_instruction.user = user

                    for instruction, value in data.iteritems():

                        setattr(user_instruction,instruction,value)

                    user_instruction.save()

            try:
                user = User.objects.get(id=user_id);

                user_instruction = StyleboardInstruction.objects.get(user=user)

                instruction_raw = {
                    'styleboard':user_instruction.styleboard,
                    'product':user_instruction.product,
                    'order':user_instruction.order,
                    'how_to_purchase':user_instruction.how_to_purchase
                }

                json_value = simplejson.dumps(instruction_raw)

                return HttpResponse(json_value)

            except:
                return HttpResponse('false')


        elif user_id == 0:

            """
            if session_instruction :

                instruction_raw = {
                    'styleboard':session_instruction['styleboard'],
                    'product':session_instruction['product'],
                    'order':session_instruction['order']
                }

                json_value = simplejson.dumps(instruction_raw)

                return HttpResponse(json_value)

            else:

                return HttpResponse('false')
            """

            if instruction_in_cookie and instruction_in_cookie != "" :

                return HttpResponse(instruction_in_cookie.data)

            else:

                return HttpResponse('false')

        else:

            return HttpResponse('error')


@csrf_exempt
def tag_instruction(request):
    
    if request.method == 'POST':

        user_id = int(request.POST.get('user'))
        value   = request.POST.get('value')

        if user_id and user_id != 0:

            try:

                user = User.objects.get(id=user_id);

                user_instruction = StyleboardInstruction.objects.get(user=user)

                setattr(user_instruction,value,True)

                user_instruction.save()

                return HttpResponse(value)

            except:

                user_instruction = StyleboardInstruction()

                user_instruction.user = user

                setattr(user_instruction,value,True)

                user_instruction.save()

                return HttpResponse(value)

        else:

            """
            instruction_raw = {
                'styleboard':False,
                'product':False,
                'order':False
            }

            instruction = request.session.get('instruction_tag')

            if instruction:
                instruction_raw['styleboard'] = instruction['styleboard']
                instruction_raw['product'] = instruction['product']
                instruction_raw['order'] = instruction['order']


            instruction_raw[value] = True

            request.session['instruction_tag'] = instruction_raw

            return HttpResponse(value)
            """
            instruction_raw = {
                'styleboard':False,
                'product':False,
                'order':False,
                'how_to_purchase':False
            }

            instruction_id = 0

            # instruction = request.session.get('instruction_tag')

            instruction = request.COOKIES.get('instruction_cookie') 
                
            try:

                instruction_in_cookie = StyleboardInstructionCookie.objects.get(id=instruction)

                data = simplejson.loads(instruction_in_cookie.data)
                
                instruction_raw['styleboard'] = data['styleboard']
                instruction_raw['product'] = data['product']
                instruction_raw['order'] = data['order']
                instruction_raw['how_to_purchase'] = data['how_to_purchase']

                instruction_raw[value] = True

                instruction_in_cookie.data = simplejson.dumps(instruction_raw)

                instruction_in_cookie.save()

                instruction_id = instruction_in_cookie.id
            
            except:

                instruction_in_cookie = StyleboardInstructionCookie()

                instruction_raw[value] = True

                instruction_in_cookie.data = simplejson.dumps(instruction_raw)

                instruction_in_cookie.save()

                instruction_id = instruction_in_cookie.id

            # request.session['instruction_tag'] = instruction_raw

            instruction_in_cookie = StyleboardInstructionCookie()

            response = HttpResponse(value)

            set_cookie(response, 'instruction_cookie', instruction_id)

            return response

@csrf_exempt
def save_template_session(request):

    if request.method == 'POST':

        template = request.POST.get('template')

        template_session = request.session['save_template'] = int(template)

        return HttpResponse(template_session)

@csrf_exempt
def set_save_template(request):

    template = request.session.get('save_template')

    if template :

        return HttpResponse(template)

    else:

        return HttpResponse(0)


@csrf_exempt
def add_wishlist_ajax(request):    
    response = ''
    if request.method == 'POST':        
        
        object_type = request.POST.get('object_type')
        object_id   = request.POST.get('object_id')
        sessionid   = request.session.get('sessionid')

        wishlist = WishList()
        wishlist.object_type = object_type
        wishlist.object_id = int(object_id)
        wishlist.sessionid = sessionid

        tmp_list = None

        if request.user.is_authenticated():

            wishlist.user = request.user

            tmp_list = WishList.objects.filter(user=request.user,
                                                object_type=object_type,
                                                object_id=object_id)

        else:

            tmp_list = WishList.objects.filter(sessionid=sessionid,
                                                object_type=object_type,
                                                object_id=object_id)

            # if user logs in he/she will be given a new session id
            # to save the wishlist items added before logging in
            # use this session key to query these items
            wishlist_session = request.session.get('wishlist_session', False)
            if not wishlist_session:
                request.session['wishlist_session'] = sessionid

        if tmp_list.count():
            response = _('Item already exist in your wishlist')
        else:
            wishlist.save()
            response = _('Item added to your wishlist')

    return HttpResponse(unicode(response))


@csrf_exempt
def get_suggested_products_ajax(request):
    html = ''
    if request.method == 'POST':
        pk = request.POST.get('id', False)
        if pk:
            product = Product.objects.get(pk=int(pk))
            suggested_products = product.suggestedproduct_set.all()
            for suggested_product in suggested_products:
                html += '%s' % suggested_product.suggested_product.name

    return HttpResponse(html)



@csrf_exempt
def subscribe_newsletter_ajax(request):

    data_response = {}
    data_response['response'] = 'failed'

    if request.method == 'POST':

        form = NewsletterSubscriberForm(request.POST)

        if form.is_valid():

            form.save()
            data_response['response'] = 'success'
            messages.success(request, _('You are now subscribed to our email newsletter.'))
            
    data_response['messages'] = render_to_string('messages_ajax_response.html', {'form':form}, RequestContext(request))

    return render_to_json(request, data_response)


@csrf_exempt
def send_product_to_styleboard(request):

    if request.method == 'POST':
        sessionid = request.session.get('cartsession',None)
        if not sessionid:
            sessionid = generate_unique_id()
            request.session['cartsession'] = sessionid

        _add_to_cart(request.POST, sessionid)
        
        _set_styleboard_jsonize(request.POST, sessionid)
        
        _set_send_to_styleboard_product_positions(request, request.POST, sessionid)
        
        return HttpResponse('ok')
    else:
        return HttpResponseNotFound()
    

@csrf_exempt
def send_styleboard_to_styleboard(request):

    if request.method == 'POST':
        sessionid = request.session.get('cartsession',None)
        if not sessionid:
            sessionid = generate_unique_id()
            request.session['cartsession'] = sessionid
        sbid = request.POST.get('sbid')
        styleboard_items = StyleboardItems.objects.get(pk=int(sbid))

        _add_styleboard_items_to_cart(styleboard_items, sessionid)

        _add_styleboard_items_positions(request, styleboard_items, sessionid)

    return HttpResponse('ok')


def _add_styleboard_items_to_cart(obj, sessionid):
    """
    for send styleboard item to styleboard on homepage
    """

    for cart_item in obj.styleboardcartitems_set.all():
        data = {
            'product' : cart_item.product,
            'sessionid' : sessionid,
            'quantity' : int(cart_item.quantity),
            'guests' : 1,
            'tables' : 1,
            'wedding' : 1,
        }
        add_to_cart(data)    


def _add_styleboard_items_positions(request, obj, sessionid):
    """
    for send styleboard item to styleboard on homepage
    """
    obj_counter = 0
    unique_identifier = 1
    changes_counter = 0
    product_objects = ''
    embellishment_objects = ''
    template_objects = ''
    action_url = '/cart/add/'
    total = ''
    quantity = ''
    selected_prev_prod_qty = ''
    buy_table_html = ''
    tables = ''
    guests = ''

    try:
        jsonize = StyleboardJsonize.objects.get(sessionid=sessionid)
    except StyleboardJsonize.DoesNotExist:
        jsonize = StyleboardJsonize(sessionid=sessionid)

    if jsonize.data:
        json_objs = simplejson.loads(jsonize.data)
        obj_counter = len(json_objs)

    product_positions = request.session.get('product_positions', None)

    if not product_positions:
        request.session['product_positions'] = {}
    else:
        unique_identifier = product_positions.get('unique_identifier')
        changes_counter += 1
        product_objects = product_positions.get('product_objects')
        embellishment_objects = product_positions.get('embellishment_objects')
        template_objects = product_positions.get('template_objects')
        action_url = product_positions.get('action_url')
        total = product_positions.get('total')
        quantity = product_positions.get('quatity')
        selected_prev_prod_qty = product_positions.get('selected_prev_prod_qty')
        buy_table_html = product_positions.get('buy_table_html')
        tables = product_positions.get('tables')
        guests = product_positions.get('guests')

    try:
        jsonize = StyleboardJsonize.objects.get(sessionid=sessionid)
    except StyleboardJsonize.DoesNotExist:
        jsonize = StyleboardJsonize()

    if jsonize.data:
        json_objs = simplejson.loads(jsonize.data)
    else:
        json_objs = simplejson.loads('[]')

    items = simplejson.loads(obj.item)
    for item in items:
        t = get_template('interface/styleboard_items.html')
        obj_counter += 1
        item['object_id'] = obj_counter
        item['src'] = item['img'][0]['src']
        item['nb'] = item['img'][0]['nb']
        item['wb'] = item['img'][0]['wb']
        item['img_style'] = item['img'][0]['style']
        item['matrix'] = simplejson.dumps(item['matrix'][0])

        json_objs.append(item)

        html = t.render(Context(item))

        if item['_type'] == 'product':
            product_objects += html

    jsonize.data = simplejson.dumps(json_objs)
    jsonize.save()

    request.session['product_positions'] = {
        'obj_counter' : str(obj_counter),
        'unique_identifier' : str(unique_identifier),
        'changes_counter' : str(changes_counter),
        'product_objects' : str(product_objects),
        'embellishment_objects' : str(embellishment_objects),
        'template_objects' : str(template_objects),
        'action_url' : str(action_url),
        'total' : str(total),
        'quantity' : str(quantity),
        'selected_prev_prod_qty' : str(selected_prev_prod_qty),
        'buy_table_html' : str(buy_table_html),
        'tables' : str(tables),
        'guests' : str(guests),
    }

    return True


def _add_to_cart(obj, sessionid):
    """
    for send product to styleboard on homepage
    """
    product_id = obj.get('prod_id')
    product = get_product(product_id)

    data = {}
    data['product'] = product.product
    data['sessionid'] = sessionid
    data['quantity'] = obj.get('quantity',1)
    data['guests'] = obj.get('guests', 1)
    data['tables'] = obj.get('tables', 1)
    data['wedding'] = obj.get('wedding', 1)

    add_to_cart(data)

    return True


def _set_styleboard_jsonize(obj, sessionid):
    """
    for send product to styleboard on homepage
    """
    prod_id = obj.get('prod_id')
    product = Product.objects.get(pk=int(prod_id))

    alt_id = obj.get('alt_id', None)
    if not alt_id:
        original_image = product.original_image
        no_background_image = product.no_background

        alternate =  product.productalternateimage_set.filter(is_default_image=True)
        if alternate.count():
            original_image = alternate[0].original_image
            no_background_image = alternate[0].no_background
    else:
        alternate = ProductAlternateImage.objects.get(pk=int(alt_id))
        original_image = alternate.original_image
        no_background_image = alternate.no_background


    img = {
        'src' : '/media/products/' + original_image,
        'nb' : no_background_image,
        'wb' : original_image,
        'style': 'display: inline; width: 100%; height: auto;'
    }

    styleboard_json = simplejson.loads(obj.get('styleboard_json'))
    styleboard_json['img'] = [img]
    print '1', styleboard_json
    product_image = Image.open("%s%s%s" % (settings.MEDIA_ROOT, "products/", product.no_background))
    width, height = product_image.size
    styleboard_json['style'] = 'width: %spx; height: %spx; top: 0px; left: 0px; z-index: 1;' % (str(width), str(height))
    print '2', styleboard_json

    try:
        jsonize = StyleboardJsonize.objects.get(sessionid=sessionid)
    except StyleboardJsonize.DoesNotExist:
        jsonize = StyleboardJsonize()

    if jsonize.data:
        json_objs = simplejson.loads(jsonize.data)
    else:
        json_objs = simplejson.loads('[]')

    if len(json_objs):
        json_objs.append(styleboard_json)
    else:
        json_objs = [styleboard_json]

    jsonize.data = simplejson.dumps(json_objs)
    jsonize.sessionid = sessionid
    jsonize.save()

    return True


def _set_send_to_styleboard_product_positions(request, obj, sessionid):
    """
    for send product to styleboard on homepage
    """
    prod_id = obj.get('prod_id')
    product = Product.objects.get(pk=int(prod_id))

    alt_id = obj.get('alt_id', None)
    if not alt_id:
        original_image = product.original_image
        no_background_image = product.no_background

        alternate =  product.productalternateimage_set.filter(is_default_image=True)
        if alternate.count():
            original_image = alternate[0].original_image
            no_background_image = alternate[0].no_background
    else:
        alternate = ProductAlternateImage.objects.get(pk=int(alt_id))
        original_image = alternate.original_image
        no_background_image = alternate.no_background

    obj_counter = 0
    unique_identifier = 1
    changes_counter = 0
    product_objects = ''
    embellishment_objects = ''
    template_objects = ''
    action_url = '/cart/add/'
    total = ''
    quantity = ''
    selected_prev_prod_qty = ''
    buy_table_html = ''
    tables = ''
    guests = ''

    try:
        jsonize = StyleboardJsonize.objects.get(sessionid=sessionid)
    except StyleboardJsonize.DoesNotExist:
        jsonize = StyleboardJsonize(sessionid=sessionid)

    if jsonize.data:
        json_objs = simplejson.loads(jsonize.data)
        obj_counter = len(json_objs)

    product_positions = request.session.get('product_positions', None)

    if not product_positions:        
        request.session['product_positions'] = {}
    else:
        unique_identifier = int(product_positions.get('unique_identifier', 0)) + 1
        changes_counter += 1
        product_objects = product_positions.get('product_objects')
        embellishment_objects = product_positions.get('embellishment_objects')
        template_objects = product_positions.get('template_objects')
        action_url = product_positions.get('action_url')
        total = product_positions.get('total')
        quantity = product_positions.get('quatity')
        selected_prev_prod_qty = product_positions.get('selected_prev_prod_qty')
        buy_table_html = product_positions.get('buy_table_html')
        tables = product_positions.get('tables')
        guests = product_positions.get('guests')

    t = get_template('interface/product_object.html')

    img = Image.open("%s%s%s" % (settings.MEDIA_ROOT, "products/", original_image))
    width, height = img.size

    context = {
        'uid' : prod_id, 
        'original_image' : original_image, 
        'no_background_image' : no_background_image,
        'object_id' : unique_identifier,
        'width' : width,
        'height' : height,
    }

    html = t.render(Context(context))
    product_objects += html

    request.session['product_positions'] = {
        'obj_counter' : str(obj_counter),
        'unique_identifier' : str(unique_identifier),
        'changes_counter' : str(changes_counter),
        'product_objects' : str(product_objects),
        'embellishment_objects' : str(embellishment_objects),
        'template_objects' : str(template_objects),
        'action_url' : str(action_url),
        'total' : str(total),
        'quantity' : str(quantity),
        'selected_prev_prod_qty' : str(selected_prev_prod_qty),
        'buy_table_html' : str(buy_table_html),
        'tables' : str(tables),
        'guests' : str(guests),
    }

    return True


