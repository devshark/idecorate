from django.contrib.auth.decorators import login_required
from django.shortcuts import HttpResponse, redirect, render_to_response
from django.contrib.auth import authenticate, login, logout
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.template import RequestContext
from django.utils import simplejson
from django.http import HttpResponseNotFound, Http404
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.safestring import mark_safe
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.utils.translation import ugettext_lazy as _
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance
from models import StyleboardItems, CustomerProfile, StyleboardJsonize, KeepImages, CustomerStyleBoard, StyleBoardCartItems
from django.contrib.auth.models import User

from forms import LoginForm, SignupForm, SaveStyleboardForm, EditProfileForm, PassForm,ForgotPassForm
from services import register_user, customer_profile, get_client_ip, get_user_styleboard, save_styleboard_item,\
    get_customer_styleboard_item, manage_styleboard_cart_items, get_styleboard_cart_item, get_user_keep_images, dynamic_styleboard,\
    get_user_orders,get_user_order,get_order, print_styleboard
from admin.models import LoginLog, TextFonts, Embellishments, EmbellishmentsType
from django.conf import settings
import re
import math
from idecorate_settings.models import IdecorateSettings
from urllib import unquote
from common.services import send_email_reset_pass
from admin.services import getExtensionAndFileName
from admin.models import HomeBannerImages
from cart.services import generate_unique_id
from embellishments.models import StyleboardTemplateItems
from django.utils.html import strip_tags
from cart.models import Contact, ProductPrice
from social_auth.models import UserSocialAuth
from django.template.defaultfilters import filesizeformat
import shutil
from cart.views import shop
import time
import os
from django_xhtml2pdf.utils import generate_pdf, render_to_pdf_response

import logging
logr = logging.getLogger(__name__)

def login_signup(request):

    info = {}
    login_form = LoginForm()
    signup_form = SignupForm()
    info['action'] = 'login_signup'
    if request.method=="POST":
        action = request.POST['btnSubmit']
        if action=='Login':         
            login_form = LoginForm(request.POST)
            ip = get_client_ip(request)
            loginLog = LoginLog.objects.filter(created__gte=(datetime.now() - timedelta(minutes=5)), ip_address=ip)
            if loginLog.count() >= 5:
                messages.error(request, _('You have failed to login 5 consecutive times. Please try to login after 5 minutes'))
                return redirect('login_signup')

            if login_form.is_valid():
                user = authenticate(username=login_form.cleaned_data['username'], password=login_form.cleaned_data['password'])
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        profile = customer_profile(user)
                        info['username'] = profile['nickname']
                        info['idecorate_user'] = user
                        #Successfull login, delete all the log attempts
                        LoginLog.objects.filter(ip_address=ip).delete()

                        personalize_styleboard = request.session.get('personalize_styleboard',None)
                        if personalize_styleboard:
                            if personalize_styleboard.user.id == user.id:
                                request.session['customer_styleboard'] = personalize_styleboard
                                del request.session['personalize_styleboard']

                        customer_styleboard = request.session.get('customer_styleboard',None)
                        if customer_styleboard:
                            if customer_styleboard.user.id != request.user.id:
                                del request.session['customer_styleboard']
                        
                        return render_to_response('customer/iframe/success.html', info)
                    else:
                        messages.warning(request, _('Sorry we could not verify your e-mail address and password.'))
                else:
                    loginLog = LoginLog()
                    loginLog.created = datetime.now()
                    loginLog.ip_address = ip
                    loginLog.save()
                    messages.warning(request, _('Sorry we could not verify your e-mail address and password.'))
        else:
            signup_form = SignupForm(request.POST)
            if signup_form.is_valid():
                user = register_user(signup_form.cleaned_data)
                if user:
                    user = authenticate(username=signup_form.cleaned_data['username'], password=signup_form.cleaned_data['password'])
                    login(request, user)
                    profile = customer_profile(user)
                    info['username'] = profile['nickname']
                    info['idecorate_user'] = user
                    personalize_styleboard = request.session.get('personalize_styleboard',None)
                    if personalize_styleboard:
                        if personalize_styleboard.user.id == user.id:
                            request.session['customer_styleboard'] = save_styleboard
                            del request.session['personalize_styleboard']
                    customer_styleboard = request.session.get('customer_styleboard',None)
                    if customer_styleboard:
                        if customer_styleboard.user.id != request.user.id:
                            del request.session['customer_styleboard']
                    return render_to_response('customer/iframe/success.html', info)
                else:
                    messages.warning(request, _('Sorry you could not register at the moment. Please try again later.'))

    info['login_form'] = login_form
    info['signup_form'] = signup_form
    return render_to_response('customer/iframe/login_signup.html', info, RequestContext(request))

def customer_logout(request):
    if request.user.is_authenticated():
        logout(request)
    if request.is_ajax():
        return HttpResponse('ok')
    else:
        return redirect('home')

def forgot_password(request):
    info = {}
    forgot_password_form = ForgotPassForm()

    if request.method=="POST":

        forgot_password_form = ForgotPassForm(request.POST)
        
        if forgot_password_form.is_valid():

            user = forgot_password_form.cleaned_data.get('username')
            try:
                u = User.objects.get(email=user)

                send_email_reset_pass(u.id)
                
                info['email_sent'] = True
                                
            except Exception as e:

                print e

    info['forgot_password_form'] = forgot_password_form
    return render_to_response('customer/iframe/forgot_password.html', info, RequestContext(request))

def profile(request):

    user_id = request.GET.get('id',None)
    if user_id:
        try:
            user = User.objects.get(id=user_id)
        except:
            if request.user.is_authenticated():
                user = request.user
            else:
                return redirect('home')
    else:
        if request.user.is_authenticated():
            user = request.user
        else:
            return redirect('home')
    info = {}
    info['styleboard_user'] = user
    user_profile = customer_profile(user)
    info['user_profile'] = user_profile
    info['currentUrl'] = request.get_full_path()
    info['user_styleboard'] = get_user_styleboard(user) 

    idecorateSettings = IdecorateSettings.objects.get(pk=1)
    info['global_default_quantity'] = idecorateSettings.global_default_quantity
    info['global_guest_table'] = idecorateSettings.global_table

    return render_to_response('customer/profile.html', info, RequestContext(request))

def edit_profile(request):
    if not request.user.is_authenticated():
        return redirect('home')
    
    info = {}

    u = User.objects.get(id=request.user.id)

    try:
        u_prof = CustomerProfile.objects.get(user=u)
    except:
        u_prof = CustomerProfile()
        u_prof.nickname = u.email
        u_prof.user = u
        u_prof.save()

    try:
        u_contact = Contact.objects.get(user=u)
    except:
        u_contact = Contact()
        u_contact.user = u
        u_contact.currency = "USD"
        u_contact.save()
        #shop.contact_model(user=u)

    try:
        user_twitter = UserSocialAuth.objects.get(user=u, provider='twitter')
    except:
        user_twitter = None

    try:
        user_facebook = UserSocialAuth.objects.get(user=u, provider='facebook')
    except:
        user_facebook = None

    initial_form_data = {
        'firstname': u.first_name,
        'lastname': u.last_name,
        'salutation': u_contact.billing_salutation,
        'user_image': u_prof.picture,
        'about': u_prof.description,
        'username': u.username,
        'gender': u_prof.gender,
        'language': u_prof.language,
        'shipping_same_as_billing': u_contact.shipping_same_as_billing,
        'shipping_address': u_contact.address,
        'shipping_address2': u_contact.shipping_address2,
        'shipping_state':u_contact.shipping_state,
        'shipping_city': u_contact.city,
        'shipping_country': u_contact.countries,
        'shipping_zip_code':u_contact.zip_code,
        'billing_address': u_contact.address2,
        'billing_address2': u_contact.billing_address2,
        'billing_state':u_contact.billing_state,
        'billing_city': u_contact.city2,
        'billing_country': u_contact.countries2,
        'billing_zip_code':u_contact.zip_code2,
    }

    form = EditProfileForm(this_user=u, initial=initial_form_data, request=request)

    pass_form = PassForm(this_user=u)

    if request.method == "POST":

        task = request.POST.get('task','1')

        if int(task) == 1:
            initial_form_data = {}
            form = EditProfileForm(request.POST,this_user=u, request=request)

            if form.is_valid():
                c_data = form.cleaned_data
                u.first_name = c_data['firstname']
                u.last_name = c_data['lastname']
                u.email = c_data['username']
                u.username = c_data['username']
                u.save()

                u_prof.description = c_data['about']
                u_prof.gender = c_data['gender']
                u_prof.language = c_data['language']

                if c_data['user_image']:

                    if c_data['user_image'] != u_prof.picture:
                        if re.search('^http', c_data['user_image']):
                            u_prof.picture = c_data['user_image']
                        else:
                            shutil.move("%s%s" % (settings.MEDIA_ROOT, "profiles/temp/%s" % c_data['user_image']), "%s%s" % (settings.MEDIA_ROOT, "profiles/%s" % c_data['user_image']))
                            u_prof.picture = "/media/profiles/%s" % c_data['user_image']

                u_prof.save()

                u_contact.billing_salutation = c_data['salutation']
                u_contact.shipping_same_as_billing = c_data['shipping_same_as_billing']
                u_contact.address = c_data['shipping_address']
                u_contact.shipping_address2 = c_data['shipping_address2']
                u_contact.shipping_state = c_data['shipping_state']
                u_contact.city = c_data['shipping_city']
                u_contact.countries = c_data['shipping_country']
                u_contact.zip_code = c_data['shipping_zip_code']
                u_contact.address2 = c_data['billing_address']
                u_contact.billing_address2 = c_data['billing_address2']
                u_contact.billing_state = c_data['billing_state']
                u_contact.city2 = c_data['billing_city']
                u_contact.countries2 = c_data['billing_country']
                u_contact.zip_code2 = c_data['billing_zip_code']
                u_contact.first_name = c_data['firstname']
                u_contact.last_name = c_data['lastname']
                u_contact.save()

                messages.success(request, _('Profile saved.'))
                return redirect('edit_profile')
        else:
            pass_form = PassForm(request.POST,this_user=u)

            if pass_form.is_valid():
                u.set_password(pass_form.cleaned_data['password'])
                u.save()

                messages.success(request, _('Password changed.'))
                return redirect('edit_profile')

    info['idecorate_user'] = u
    info['idecorate_profile'] = u_prof
    info['idecorate_contact'] = u_contact
    info['user_twitter'] = user_twitter
    info['user_facebook'] = user_facebook
    info['form'] = form
    info['pass_form'] = pass_form
    info['initial_form_data'] = initial_form_data

    return render_to_response('customer/edit_profile.html', info, RequestContext(request))

def orders(request):

    user_id = request.GET.get('id',None)
    if user_id:
        try:
            user = User.objects.get(id=user_id)
        except:
            if request.user.is_authenticated():
                user = request.user
            else:
                return redirect('home')
    else:
        if request.user.is_authenticated():
            user = request.user
        else:
            return redirect('home')

    user_orders = get_user_orders(user)

    paginator = Paginator(user_orders, 20)
    page = request.GET.get('page','')
    try:
        user_orders = paginator.page(page)
    except PageNotAnInteger:
        user_orders = paginator.page(1)
    except EmptyPage:
        user_orders = paginator.page(paginator.num_pages)


    info = {}

    info['orders'] = user_orders

    if request.GET.get('page'):
        info['page'] = int(request.GET.get('page'))
    else:
        info['page'] = 0

    return render_to_response('customer/orders.html', info, RequestContext(request))

def view_order(request):

    user_id = request.GET.get('id',None)
    if user_id:
        try:
            user = User.objects.get(id=user_id)
        except:
            if request.user.is_authenticated():
                user = request.user
            else:
                return redirect('home')
    else:
        if request.user.is_authenticated():
            user = request.user
        else:
            return redirect('home')

    info = {}

    order_id            = int(request.GET.get('order'))
    user_order          = get_user_order(order_id,user)
    
    if user_order:

        info['order']       = user_order['order']
        info['order_items'] = user_order['order_items']

    else:
        return redirect('home')
    
    if request.GET.get('p'):
        info['page'] = int(request.GET.get('p'))
    else:
        info['page'] = 0

    return render_to_response('customer/view_order.html', info, RequestContext(request))

def hard_copy_order(request, is_pdf, order_id):

    info = {}

    order_id = int(order_id)
    order = get_order(order_id)

    info['order']       = order['order']
    info['order_items'] = order['order_items']

    is_pdf = bool(int(is_pdf))

    if is_pdf :

        result = render_to_pdf_response('view_order_pdf.html', info, 'view_order_%s.pdf' % ( str(time.time()).replace('.','_') ))

    else:

        result = render_to_response('view_order_print.html', info,RequestContext(request))

    return result

@csrf_exempt
def customer_upload_image(request):

    if request.method == "POST":

        uploaded = request.FILES['image']
        content_type = uploaded.content_type.split('/')[0]

        if content_type in settings.CONTENT_TYPES:
            if int(uploaded.size) > int(settings.MAX_UPLOAD_PROFILE_PIC):
                return HttpResponse(_('notok:Please keep filesize under %s. Current filesize %s').encode('utf-8') % (filesizeformat(settings.MAX_UPLOAD_PROFILE_PIC), filesizeformat(uploaded.size)))
            else:
                splittedName = getExtensionAndFileName(uploaded.name)
                newFileName = "%s-%s%s" % (splittedName[0],datetime.now().strftime('%b-%d-%I%M%s%p-%G'),splittedName[1])

                destination = open("%s%s%s" % (settings.MEDIA_ROOT, "profiles/temp/", newFileName), 'wb+')
                for chunk in uploaded.chunks():
                    destination.write(chunk)

                destination.close()

                return HttpResponse('ok:%s' % newFileName)
        else:
            return HttpResponse(_('notok:File type is not supported').encode('utf-8'))

def save_styleboard(request):
    if not request.user.is_authenticated():
        return redirect('styleboard')
    info = {}   
    customer_styleboard = request.session.get('customer_styleboard',None)
    if not customer_styleboard:
        sbid = request.GET.get('sbid',None)
        if sbid:
            personalize_styleboard = get_user_styleboard(None, sbid)
            if personalize_styleboard:
                if personalize_styleboard.user.id:              
                    if int(personalize_styleboard.user.id) == int(request.user.id):
                        customer_styleboard = personalize_styleboard

    if customer_styleboard:

        form = SaveStyleboardForm(initial={'name':customer_styleboard.styleboard_item.name,'description':customer_styleboard.styleboard_item.description})
    else:
        form = SaveStyleboardForm()

    if request.method == "POST":

        if request.session.get('save_template'):

            try :
                
                template = StyleboardTemplateItems.objects.get(id=int(request.session.get('save_template')))
                template.is_used = True
                template.save()
            
            except Exception as e:
                
                print e
            

        form = SaveStyleboardForm(request.POST) 

        if form.is_valid():

            cleaned_datas                           = form.cleaned_data
            cleaned_datas['user']                   = request.user
            cleaned_datas['customer_styleboard']    = customer_styleboard
            cleaned_datas['sessionid']              = request.session.get('cartsession',generate_unique_id())
            cleaned_datas['description']            = cleaned_datas['description']
            cleaned_datas['session_in_request']     = request.session

            res                                     = save_styleboard_item(cleaned_datas)

            request.session['customer_styleboard']  = res

            info['action']                          = 'save_styleboard'
            info['msg']                             = _('Style board saved.')

            return render_to_response('customer/iframe/success.html', info)

    info['form'] = form

    return render_to_response('customer/iframe/save_styleboard.html', info, RequestContext(request))

def styleboard_view(request,sid=None):
    if not sid:
        # return redirect('home')
        raise Http404
    info = {}
    styleboard = get_user_styleboard(None, sid)
    if not styleboard:
        # return redirect('home')
        raise Http404

    """
    manage add to cart
    """
    if request.method=="POST":
        styleboard_item_id = request.POST['sid']
        styleboard = get_user_styleboard(None,styleboard_item_id)
        cart_items = get_styleboard_cart_item(styleboard)

    user_profile = customer_profile(styleboard.user)
    info['styleboard_user'] = styleboard.user
    info['user_profile'] = user_profile
    info['styleboard'] = get_user_styleboard(None, sid)
    info['cart_items'] = get_styleboard_cart_item(styleboard.styleboard_item)
    info['styleboard_id'] = sid
    return render_to_response('customer/styleboard_view.html', info, RequestContext(request))

def get_product_price(product):
        product_details = ProductPrice.objects.get(product=product)
        return product_details._unit_price

def print_customer_sb(request, is_pdf, sbid):
    info = {}

    is_pdf = bool(int(is_pdf))

    data = ''

    styleboard_id = int(sbid)

    info['cart_list'] = ''
    info['default_multiplier'] = 0

    if styleboard_id:
        try:
            StyleboardItem = StyleboardItems.objects.get(id=styleboard_id)
            info['styleboard_item'] = StyleboardItem
            info['cart_list'] = StyleBoardCartItems.objects.filter(styleboard_item=styleboard_id)
            info['default_multiplier_list'] = ['%s Guests /' % (StyleboardItem.item_guest),'%s Tables' % (StyleboardItem.item_tables)]
            info['total_price'] = mark_safe("%.2f" % (sum((get_product_price(item.product) * item.quantity) for item in info['cart_list'])))
            
            data = StyleboardItem.item

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

        styleboard = '/styleboard/generate_printable_styleboard/850/538/%s/?get=%s' % ( styleboard_id, str(time.time()).replace('.','_') )
        info['styleboard'] = styleboard

        result = render_to_response('interface/styleboard_print.html', info,RequestContext(request))

    return result

def generate_styleboard_view(request, id, w, h):
    
    image = dynamic_styleboard(id, w, h)

    response = HttpResponse(mimetype="image/png")
    
    image.save(response, 'PNG')

    return response

def generate_printable_styleboard(request, w, h, sbid=None):

    if sbid is None:

        sessionid = request.session.get('cartsession', None)
        data = ''
        try: 
            jsonize = StyleboardJsonize.objects.get(sessionid=sessionid)
            data = jsonize.data
        except Exception as e:
            print e

    else:

        data = ''
        try: 
            StyleboardItem = StyleboardItems.objects.get(id=int(sbid))
            data = StyleboardItem.item
        except Exception as e:
            print e

       
    image = print_styleboard(data, w, h)

    response = HttpResponse(mimetype="image/jpg")
    
    image.save(response, 'JPEG')

    return response

def social_redirect(request):

    if 'fb_auth_error' in request.session:
        if "last_page_idecorate" in request.session:
            if re.search('edit_profile', request.session['last_page_idecorate']):
                return redirect('edit_profile')
            else:
                return redirect('invite_friends')
    else:

        if "last_page_idecorate" in request.session:
            #print request.session['last_page_idecorate']
            return redirect(request.session.get('last_page_idecorate'))
        else:
            return redirect('/')


def generate_styleboard_template_view(request, id, w, h):
    
    styleboardItem = StyleboardTemplateItems.objects.get(id=id)
    itemString = str(styleboardItem.item).replace('null,','')
    itemList = []
    
    imageWidth = int(w)
    imageHeight = int(h)

    lowestTop = None
    highestTop = None
    lowestLeft = None
    highestLeft = None

    finalHeight = 0
    finalWidth = 0
    widthIndex = 0
    heightIndex = 0
    true = True
    false = False

    exec('itemList=%s' % itemString)

    for iList in itemList:

        if re.search('/media/products/',iList['img'][0]['src']):

            imgFile = iList['img'][0]['src'].split('/')
            imgFile = imgFile[len(imgFile) - 1].split('?')[0]
            imgFile = "%s%s%s" % (settings.MEDIA_ROOT, 'products/', unquote(imgFile))

        elif re.search('/generate_embellishment/', iList['img'][0]['src']):
            eProperties = iList['img'][0]['src'].split("?")[1].split('&')

            directory = ""

            embObj = Embellishments.objects.get(id=int(eProperties[0].split('=')[1]))

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

            imgFile = "%s%s%s" % (settings.MEDIA_ROOT, "embellishments/%s/" % directory, embObj.image)
        elif re.search('/media/embellishments/',iList['img'][0]['src']):

            imgFile = iList['img'][0]['src'].split('/')
            imgFile = imgFile[len(imgFile) - 1]
            imgFile = "%s%s%s" % (settings.MEDIA_ROOT, 'embellishments/images/', unquote(imgFile))

        elif re.search('/generate_text/',iList['img'][0]['src']):
            eProperties = iList['img'][0]['src'].split("?")[1].split('&')

            fontObj = TextFonts.objects.get(id=int(eProperties[3].split('=')[1]))
            imgFile = "%s%s%s" % (settings.MEDIA_ROOT, "fonts/", fontObj.font)
            font_size = int(eProperties[0].split('=')[1])
            font_color = eProperties[2].split('=')[1]
            font_color = (int(font_color[0:3]), int(font_color[3:6]), int(font_color[6:9]))
            image_text = unquote(eProperties[1].split('=')[1])
        elif re.search('/cropped/',iList['img'][0]['src']):
            eProperties = iList['img'][0]['src'].split("?")[1].split('&')

            imgFile = "%s%s%s" % (settings.MEDIA_ROOT, "products/", unquote(eProperties[3].split('=')[1]))
            task = eProperties[1].split('=')[1]

            splittedPosts = unquote(eProperties[2].split('=')[1]).split(',')
        elif re.search('/media/admin/img/fake_BG.png',iList['img'][0]['src']):
            imgFile = "%s%s" % (settings.MEDIA_ROOT, "products/white_background.png")


        style = iList['style']
        splittedStyle = style.split(';')

        #find width and height index
        ctr = 0
        for item in splittedStyle:
            if re.search('width', item):
                widthIndex = ctr
            if re.search('height', item):
                heightIndex = ctr
            ctr += 1

        w = int(float(str(splittedStyle[widthIndex].split(':')[1]).strip().replace('px','')))
        h = int(float(str(splittedStyle[heightIndex].split(':')[1]).strip().replace('px','')))

        try:
            if re.search('/generate_text/',iList['img'][0]['src']):

                font = ImageFont.truetype(imgFile, font_size)
                
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

                imgObj = img
                #imgObj.thumbnail((w,h),Image.ANTIALIAS)
                imgObj = imgObj.resize((w,h), Image.ANTIALIAS)
                imgObj = imgObj.rotate(float(iList['angle']), expand=1)
                w, h = imgObj.size
            elif re.search('/cropped/',iList['img'][0]['src']):

                img = Image.open(imgFile)
                back = Image.new('RGBA', (400,400), (255, 255, 255, 0))
                back.paste(img, ((400 - img.size[0]) / 2, (400 - img.size[1]) /2 ))

                poly = Image.new('RGBA', (settings.PRODUCT_WIDTH,settings.PRODUCT_HEIGHT), (255, 255, 255, 0))
                pdraw = ImageDraw.Draw(poly)

                dimensionList = []

                if task == 'poly':
                    for splittedPost in splittedPosts:
                        spl = splittedPost.split(':')
                        dimensionList.append((float(spl[0]),float(spl[1])))

                    pdraw.polygon(dimensionList,fill=(255,255,255,255),outline=(255,255,255,255))

                elif task == 'rect':
                    for splittedPost in splittedPosts:
                        dimensionList.append(float(splittedPost))
                    pdraw.rectangle(dimensionList,fill=(255,255,255,255),outline=(255,255,255,255))


                poly.paste(back,mask=poly)

                newImg = poly.crop(((400 - img.size[0]) / 2, (400 - img.size[1]) /2 , ((400 - img.size[0]) / 2) + img.size[0], ((400 - img.size[1]) / 2) + img.size[1]))
                imgObj = newImg
                imgObj = imgObj.resize((w,h), Image.ANTIALIAS)
                imgObj = imgObj.rotate(float(iList['angle']), expand=1)
                w, h = imgObj.size
            else:
                imgObj = Image.open(imgFile).convert('RGBA')
                #imgObj.thumbnail((w,h),Image.ANTIALIAS)
                imgObj = imgObj.resize((w,h), Image.ANTIALIAS)
                imgObj = imgObj.rotate(float(iList['angle']), expand=1)
                w, h = imgObj.size
        except:
            pass

        if lowestTop is None:
            lowestTop = int(float(iList['top']))
        else:
            if int(float(iList['top'])) < lowestTop:
                lowestTop = int(float(iList['top']))

        if highestTop is None:
            highestTop = int(float(iList['top'])) + h
        else:
            if (int(float(iList['top'])) + h) > highestTop:
                highestTop = int(float(iList['top'])) + h

        if lowestLeft is None:
            lowestLeft = int(float(iList['left']))
        else:
            if int(float(iList['left'])) < lowestLeft:
                lowestLeft = int(float(iList['left']))

        if highestLeft is None:
            highestLeft = int(float(iList['left'])) + w
        else:
            if (int(float(iList['left'])) + w) > highestLeft:
                highestLeft = int(float(iList['left'])) + w

    finalWidth = highestLeft - lowestLeft
    finalHeight = highestTop - lowestTop

    #create main image
    mainImage = Image.new('RGBA', (finalWidth, finalHeight), (255, 255, 255, 0))


    for iList in itemList:

        if re.search('/media/products/',iList['img'][0]['src']):

            imgFile = iList['img'][0]['src'].split('/')
            imgFile = imgFile[len(imgFile) - 1].split('?')[0]
            imgFile = "%s%s%s" % (settings.MEDIA_ROOT, 'products/', unquote(imgFile))
        elif re.search('/generate_embellishment/', iList['img'][0]['src']):
            eProperties = iList['img'][0]['src'].split("?")[1].split('&')

            directory = ""

            embObj = Embellishments.objects.get(id=int(eProperties[0].split('=')[1]))

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

            imgFile = "%s%s%s" % (settings.MEDIA_ROOT, "embellishments/%s/" % directory, embObj.image)
        elif re.search('/media/embellishments/',iList['img'][0]['src']):

            imgFile = iList['img'][0]['src'].split('/')
            imgFile = imgFile[len(imgFile) - 1]
            imgFile = "%s%s%s" % (settings.MEDIA_ROOT, 'embellishments/images/', unquote(imgFile))
        elif re.search('/generate_text/',iList['img'][0]['src']):
            eProperties = iList['img'][0]['src'].split("?")[1].split('&')

            fontObj = TextFonts.objects.get(id=int(eProperties[3].split('=')[1]))
            imgFile = "%s%s%s" % (settings.MEDIA_ROOT, "fonts/", fontObj.font)
            font_size = int(eProperties[0].split('=')[1])
            font_color = eProperties[2].split('=')[1]
            font_color = (int(font_color[0:3]), int(font_color[3:6]), int(font_color[6:9]))
            image_text = unquote(eProperties[1].split('=')[1])
            #print "The text is: %s" % image_text
        elif re.search('/cropped/',iList['img'][0]['src']):
            eProperties = iList['img'][0]['src'].split("?")[1].split('&')

            imgFile = "%s%s%s" % (settings.MEDIA_ROOT, "products/", unquote(eProperties[3].split('=')[1]))
            task = eProperties[1].split('=')[1]

            splittedPosts = unquote(eProperties[2].split('=')[1]).split(',')
        elif re.search('/media/admin/img/fake_BG.png',iList['img'][0]['src']):
            imgFile = "%s%s" % (settings.MEDIA_ROOT, "products/white_background.png")

        style = iList['style']
        splittedStyle = style.split(';')

        #find width and height index
        ctr = 0
        for item in splittedStyle:
            if re.search('width', item):
                widthIndex = ctr
            if re.search('height', item):
                heightIndex = ctr
            ctr += 1

        w = int(float(str(splittedStyle[widthIndex].split(':')[1]).strip().replace('px','')))
        h = int(float(str(splittedStyle[heightIndex].split(':')[1]).strip().replace('px','')))


        if re.search('/generate_text/',iList['img'][0]['src']):

            font = ImageFont.truetype(imgFile, font_size)
            
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

            imgObj = img
        elif re.search('/cropped/',iList['img'][0]['src']):

            img = Image.open(imgFile)
            back = Image.new('RGBA', (400,400), (255, 255, 255, 0))
            back.paste(img, ((400 - img.size[0]) / 2, (400 - img.size[1]) /2 ))

            poly = Image.new('RGBA', (settings.PRODUCT_WIDTH,settings.PRODUCT_HEIGHT), (255, 255, 255, 0))
            pdraw = ImageDraw.Draw(poly)

            dimensionList = []

            if task == 'poly':
                for splittedPost in splittedPosts:
                    spl = splittedPost.split(':')
                    dimensionList.append((float(spl[0]),float(spl[1])))

                pdraw.polygon(dimensionList,fill=(255,255,255,255),outline=(255,255,255,255))

            elif task == 'rect':
                for splittedPost in splittedPosts:
                    dimensionList.append(float(splittedPost))
                pdraw.rectangle(dimensionList,fill=(255,255,255,255),outline=(255,255,255,255))

            poly.paste(back,mask=poly)

            newImg = poly.crop(((400 - img.size[0]) / 2, (400 - img.size[1]) /2 , ((400 - img.size[0]) / 2) + img.size[0], ((400 - img.size[1]) / 2) + img.size[1]))

            """
            splittedName = getExtensionAndFileName(imgFile)
            if splittedName[1] == '.jpg':
                img2 = Image.open("%s%s" % (settings.MEDIA_ROOT, "products/white_background.png"))
                img2 = img2.resize((newImg.size[0],newImg.size[1]), Image.ANTIALIAS)
                img2 = img2.convert('RGBA')             
                #img2 = Image.blend(img2, newImg, 0.0)
                img2.paste(newImg, mask=newImg)
                newImg = img2
            """
            imgObj = newImg
        else:

            imgObj = Image.open(imgFile).convert('RGBA')

        if re.search('/generate_embellishment/', iList['img'][0]['src']):
            embellishment_color = eProperties[1].split('=')[1]
            embellishment_color = (int(embellishment_color[0:3]), int(embellishment_color[3:6]), int(embellishment_color[6:9]))
            newImg = Image.new("RGBA", imgObj.size, embellishment_color)
            r, g, b, alpha = imgObj.split()

            if embObj.e_type.id == 3:
                newImg.paste(imgObj, mask=b)
                imgObj = newImg
            elif embObj.e_type.id == 2 or embObj.e_type.id == 4:
                imgObj.paste(newImg, mask=alpha)


        if re.search('/media/admin/img/fake_BG.png',iList['img'][0]['src']):

            alpha = imgObj.split()[3]
            alpha = ImageEnhance.Brightness(alpha).enhance(0.50)
            imgObj.putalpha(alpha)

            borderImage = ImageOps.expand(imgObj, border=5, fill='black')
            imgObj = borderImage

        #apply opacity
        if int(iList['opacity']) != 100:
            #adjust opacity
            floatOpacity = float(float(iList['opacity']) / float(100))
            alpha = imgObj.split()[3]
            alpha = ImageEnhance.Brightness(alpha).enhance(floatOpacity)
            imgObj.putalpha(alpha)

        #try to rotate
        try:
            #imgObj.thumbnail((w,h),Image.ANTIALIAS)
            imgObj = imgObj.resize((w,h), Image.ANTIALIAS)
            imgObj = imgObj.rotate(float(iList['angle']), expand=1,resample=Image.BICUBIC)
            """
            print "The width is: %s, and height is: %s" % (w,h)
            print "The new width is: %s, and the new height is: %s" % imgObj.size
            
            aW = int((w / 2) * math.cos(float(iList['angle']))) + int((h / 2) * math.cos(90 - float(iList['angle'])))
            aH = int((w / 2) * math.sin(float(iList['angle']))) + int((h / 2) * math.sin(90 - float(iList['angle'])))
            
            
            imgObj.thumbnail((w,h),Image.ANTIALIAS)
            """
        except:
            #imgObj.thumbnail((w,h),Image.ANTIALIAS)
            imgObj = imgObj.resize((w,h), Image.ANTIALIAS)
            

        #flip and flap
        exec('matrix=%s' % iList['matrix'])

        if matrix[0]['e']:
            #flip
            imgObj = imgObj.transpose(Image.FLIP_TOP_BOTTOM)

        if matrix[0]['f']:
            #flap
            imgObj = imgObj.transpose(Image.FLIP_LEFT_RIGHT)
        
        """
        try:

            if splittedName[1] == '.jpg':
                mainImage.paste(imgObj,(int(float(iList['left'])) - lowestLeft,int(float(iList['top'])) - lowestTop))
            else:   
                mainImage.paste(imgObj,(int(float(iList['left'])) - lowestLeft,int(float(iList['top'])) - lowestTop), mask=imgObj)
        except:

            mainImage.paste(imgObj,(int(float(iList['left'])) - lowestLeft,int(float(iList['top'])) - lowestTop), mask=imgObj)
        """
        mainImage.paste(imgObj,(int(float(iList['left'])) - lowestLeft,int(float(iList['top'])) - lowestTop), mask=imgObj)
        #paste image
        #mainImage.paste(imgObj, (highestWidth - (w + int(iList['left'])), highestHeight - (h + int(iList['top']))))

    response = HttpResponse(mimetype="image/png")
    
    mainImage.thumbnail((imageWidth,imageHeight), Image.ANTIALIAS)
    bgImg = Image.new('RGBA', (imageWidth, imageHeight), (255, 255, 255, 0))
    bgImg.paste(mainImage,((imageWidth - mainImage.size[0]) / 2, (imageHeight - mainImage.size[1]) / 2))
    bgImg.save(response, "PNG")
    """
    mainImage.save(response, "PNG")
    """
    return response

@csrf_exempt
def keep_home_image(request):

    ret = "failed"


    if request.method == "POST":

        if request.POST['image_id'] : 

            image_id = int(request.POST['image_id'])

        if request.POST['user_id'] : 

            user_id = int(request.POST['user_id'])

        try:

            keep_image = KeepImages.objects.get(image__id=image_id, user__id=user_id)

            ret = "duplicate"
        
        except:
        
            keep_image          = KeepImages()
            keep_image.image    = HomeBannerImages.objects.get(id=image_id)
            keep_image.user     = User.objects.get(id=user_id)
            keep_image.save()

            if keep_image.pk : 

                ret = "success"

    return HttpResponse(ret)

def saved_images(request):

    user_id = request.GET.get('id',None)

    if user_id:

        try:

            user = User.objects.get(id=user_id)

        except:

            if request.user.is_authenticated():

                user = request.user

            else:

                return redirect('home')
    else:

        if request.user.is_authenticated():

            user = request.user

        else:

            return redirect('home')

    info = {}

    user_profile                = customer_profile(user)
    info['user_profile']        = user_profile
    user_keeped_images          = get_user_keep_images(user)
    info['user_keeped_images']  = user_keeped_images

    return render_to_response('customer/saved_images.html', info, RequestContext(request))

def delete_styleboard(request, sb_id):

    if request.user.is_authenticated():
        user = request.user

        try:
            styleboard = CustomerStyleBoard.objects.get(user=user, styleboard_item__id=int(sb_id))
            styleboardItem = StyleboardItems.objects.get(id=styleboard.styleboard_item.id)
            styleboardItem.deleted = True
            styleboardItem.save()

            messages.success(request, _('Styleboard %s successfully deleted.' % (styleboardItem.name) ))
        except Exception as e: 

            messages.warning(request, _('Deleting styleboard failed.'))
            logr.error(e)
    
    return redirect('profile')