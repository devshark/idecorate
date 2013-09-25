from django import template
from django.utils.safestring import mark_safe
from menu.models import FooterCopyright, InfoMenu, SiteMenu, FooterMenu, FatFooterMenu, ItemMenu
from category.services import get_categories, category_tree_crumb, get_cat
from django.core.urlresolvers import reverse
from idecorate_settings.models import IdecorateSettings
from django.contrib.humanize.templatetags.humanize import intcomma
from cart.services import get_product

from customer.services import customer_profile, get_save_styleboard_total
from cart.models import ProductPrice, Contact, OrderStyleboard
from admin.models import Embellishments, TextFonts, EmbellishmentsType, HomeBannerImages
from django.conf import settings
import math
import re
from interface.views import clear_styleboard_session

register = template.Library()

@register.filter
def get_interface_info(infoType):

    if infoType == "footer":

        copyright = FooterCopyright.objects.get(id=1)
        return mark_safe(copyright.copyright)

    elif infoType == "footer_menu":

        element = '<ul>'
        footer_menus = FooterMenu.objects.filter(parent=None,deleted=False).order_by('order')
        link = ""

        for menu in footer_menus:

                if menu.link == "":
                    link = menu.name
                else:
                    link = '<a href="%s">%s</a>' % (menu.link, menu.name)

                element += '<li>%s</li>' % link

        element += '</ul>'
        return mark_safe(element)

    elif infoType == 'fat_footer':
        element = '<ul>'

        footer_menus = FatFooterMenu.objects.filter(deleted=False).order_by('order')
        link = ""

        for menu in footer_menus:

            if menu.link == "":
                link = menu.name
            else:
                link = '<a href="%s">%s</a>' % (menu.link, menu.name)

            element += '<li>%s</li>' % link

        element += '</ul>'
        return mark_safe(element)


@register.filter
def get_parent_category(value):

        parent_category = get_categories(None)
        parent_category = parent_category.order_by('order')
        tags = "<ul>"

        for cat in parent_category:
            
            tags += '<li><a href="%s">%s</a></li>' % (reverse('styleboard_cat', args=[cat.id]), cat.name)
                
        tags += '</ul>'
        return mark_safe(tags)


@register.filter
def get_category_nav(value):

        parent_category = get_categories(None)
        parent_category = parent_category.order_by('order')
        item_menu = ItemMenu.objects.filter(deleted=0,parent=None).order_by('order')
        tags = menuItemInterface(item_menu)

        tags += '<ul class="dd">'

        for cat in parent_category:

                tags += '<li><a href="%s">%s</a>'% (reverse('styleboard_cat', args=[cat.id]), cat.name)
                sub_cat = get_categories(cat.id)

                if sub_cat.count() > 0:

                    tags += '<ul>'
                    for scat in sub_cat:

                        tags += '<li><a href="%s">%s</a></li>' % (reverse('styleboard_cat', args=[scat.id]), scat.name)
                    
                    tags += '</ul>'

                tags += '</li>'
                
        tags += '</ul>'
        return mark_safe(tags)


@register.filter
def get_breadcrumb(parent_id):

    if parent_id:

        cat_tree = category_tree_crumb(parent_id)
        tags = '<ul class="breadcrumb">'
        tags += '<li><a href="#">All</a></li>'
        arr = cat_tree.split('|')
        i = len(arr)

        while i != 0:

            cc = arr[i-1].split(':')

            if i==1:

                tags += '<li> <span>></span> </li><li class="active"><span>%s</span></li>' % (cc[1])
            else:

                tags += '<li> <span>></span> </li><li><a rel="%s" href="#">%s</a></li>' % (cc[0], cc[1])
            
            i = i-1

        tags += '</ul>'
        return mark_safe(tags)

    return ''


@register.filter
def generate_product_order_list2(obj,objMain):

    products = obj.filter().order_by('-id')
    ret = ""

    for product in products:

        ret += """
            <tr>
                <td style="text-align:center;width:60px;">%s x </td>
                <td stysle="text-align:left;">%s/%s</td>
                <td>%s%s</td>
                <td>%s%s</td>
            </tr>
        """ % (product.quantity, product.product.sku, product.product.name, "$", intcomma("%.2f" % product.unit_price), "$", intcomma("%.2f" % product.discounted_subtotal))

    return mark_safe(ret)


@register.filter
def generate_product_order_list(obj,objMain):

    products = obj.filter().order_by('-id')
    ret = ""

    for product in products:

        ret += """
            <tr>
                <td>
                    <img src="/media/products/%s" align="left" />
                    <span>%s/%s</span>
                </td>
                <td valign="middle" class="productPricing">%s%s</td>
                <td valign="middle" class="productPricing">%s</td>
                <td valign="middle" class="productPricing">%s%s</td>
            </tr>
        """ % (product.product.original_image_thumbnail, product.product.sku, product.product.name, "$", intcomma("%.2f" % product.unit_price), product.quantity, "$", intcomma("%.2f" % product.discounted_subtotal))

    return mark_safe(ret)


@register.filter
def get_checkout_page_info(inf):

    idecorate_settings = IdecorateSettings.objects.get(pk=1)
    info ={
        "delivery_date_note" : idecorate_settings.delivery_date_note,
        "any_question" : idecorate_settings.any_question,
        "t_and_c" : idecorate_settings.t_and_c
    }

    return mark_safe(info.get(inf, "")) 


@register.filter
def get_nickname(user):

    try:
        
        nickname = user.first_name if str(user.first_name).strip() != "" else user.username
        
    except:
    
        nickname = ""

    return nickname


@register.filter
def get_emb_save_total(styleboard_item_id):  

    return mark_safe("%.2f" % get_save_styleboard_total(styleboard_item_id))
        

@register.filter
def get_product_price(product):

    product_details = ProductPrice.objects.get(product=product)
    return mark_safe("%.2f" % product_details._unit_price)


@register.filter
def get_sub_total(price,quantity):

    return mark_safe("%.2f" % (float(quantity)*float(price)))

@register.filter
def set_last_page_idecorate(request):

    try:

        request.session['last_page_idecorate'] = request.get_full_path()

    except:

        pass

    return ""


def replace_space_rec(val):

    if '  ' in val:

        val = val.replace('  ','&nbsp;&nbsp;')

        if ' ' in val:

            val = replace_space_rec(val)
    
    return val


@register.filter
def replace_space(val):

    return mark_safe(replace_space_rec(val))


@register.filter
def interface_paginate(object_list,page_of_page=False):

    total_pages     = object_list.paginator.num_pages
    current_page    = object_list.number
    item_perpage    = object_list.paginator.per_page
    max_link        = 3
    pagination = """
        <div class="pagination">
            <ul>"""
    
    if page_of_page: #show page of pages

        pagination += """
            <li>
                <span class="pageofpage">Page %s of %s.</span>
            </li>""" % (object_list.number,object_list.paginator.num_pages)
    
    if object_list.has_previous():

        pagination += """
            <li>
                <a class="prev" href="?page=%s">Previous</a>
            </li>""" % (object_list.previous_page_number())

    if object_list.paginator.page_range and len(object_list.paginator.page_range) > 1:
            
        for page in object_list.paginator.page_range:

            if page == current_page:

                pagination += """
                    <li>
                        <span class="current">%s</span>
                    </li>""" % (page)

            else:

                pagination += """
                    <li>
                        <a href="?page=%s">%s</a>
                    </li>""" % (page,page)
    
    if object_list.has_next():
            
            pagination += """
                <li>
                    <a class="next" href="?page=%s">Next</a>
                </li>""" % (object_list.next_page_number())
    
    pagination += """</ul></div>"""

    return mark_safe(pagination)


@register.filter
def convert_unicode_to_entity(val):

    return mark_safe(val.decode('unicode-escape').encode('ascii','xmlcharrefreplace'))


@register.filter
def clear_styleboard_session_tag(request):

    clear_styleboard_session(request)
    return None


@register.filter
def get_session_by_key(request, key):
        
    return request.session.get(key, '')


@register.filter
def add_http_prefix(url):

    if not re.search('^http:\/\/',str(url).strip()):

        url = "%s%s" % ('http://', str(url).strip())

    return mark_safe(url)


@register.filter
def get_ordered_styleboard(order, data):

    try:

        order_styleboard = OrderStyleboard.objects.get(order=order)
        return getattr(order_styleboard, data)

    except Exception as e:

        return None




@register.filter
def linebreak(txt):

    return mark_safe(txt.replace("\n", '<br />'))


@register.filter
def get_url(request):

    return request.build_absolute_uri()


@register.filter
def get_host(request):

    return request.get_host()


def menuItemInterface(item_menu,is_sub=False):

        menus = ''

        if is_sub:

            menus += '<ul>'

        else:

            menus += '<ul class="dd">'

        for menu in item_menu:

                menus += '<li><a href="%s">%s</a>' % (menu.link, menu.name)
                sub_menus = ItemMenu.objects.filter(parent=menu.id,deleted=0)

                if sub_menus.count() > 0:

                        menus += menuItemInterface(sub_menus,True)

                menus += '</li>'

        menus += '</ul>'

        return menus


def menuInterfaceRecursion(menus, activate_url, isLoggedIn):

        element = ""
        link = ""
        needToOpen = True

        for menu in menus:

            if menu.parent is None:

                if needToOpen:

                    element += '<ul class="menu %s %s">' % ('iDdropdown' if menu.__class__.__name__ != "FooterMenu" else '', menu.__class__.__name__)
                    needToOpen = False
            else:

                if needToOpen:

                    element += '<ul>'
                    needToOpen = False

            active = "active" if str(menu.link) == str(activate_url) else "inActive"

            link = '<a class="%s" href="%s">%s</a>' % (active, menu.link, menu.name) #if menu.link else '<a href="#">%s</a>' % menu.name
            
            if menu.__class__.__name__ == "FooterMenu" and menu.parent is None:
                
                link = '<a class="btn %s" href="%s">%s</a>' % (active, menu.link, menu.name) #if menu.link else '<a href="#">%s</a>' % menu.name
           
            element += '<li>%s' % (link)
            sub_menus = menu.__class__.objects.filter(parent__id=menu.id,deleted=False).order_by('order')
            element += menuInterfaceRecursion(sub_menus,activate_url, isLoggedIn)
            element +='</li>'

        if needToOpen == False:

            if menu.parent is None:

                myAccountMenu = ""

                if isLoggedIn:

                    myAccountMenu = '<ul class="myAccountMenu">'
                    myAccountMenu += '<li><a class="%s" href="%s">saved styleboard</a>' % ("active" if reverse('profile') == str(activate_url) else "inActive" , reverse('profile'))
                    # myAccountMenu += '<li><a class="%s" href="%s">saved images</a>' % ("active" if reverse('saved_images') == str(activate_url) else "inActive", reverse('saved_images'))
                    myAccountMenu += '<li><a class="%s" href="%s">orders</a>' % ("active" if reverse('orders') == str(activate_url) else "inActive", reverse('orders'))
                    myAccountMenu += '<li><a class="%s" href="%s">invite friends</a>' % ("active" if reverse('invite_friends') == str(activate_url) else "inActive", reverse('invite_friends'))
                    myAccountMenu += '<li><a class="%s" href="%s">edit profile</a>' % ("active" if reverse('edit_profile') == str(activate_url) else "inActive", reverse('edit_profile'))
                    myAccountMenu += '<li><a href="%s">logout</a>' % reverse('logout')
                    myAccountMenu += '</ul>'

                if menu.__class__.__name__ == "SiteMenu":

                    element+= '<li><a id="%s_account_header" href="%s">my account</a>%s</li>' % ('login' if not isLoggedIn else 'my', reverse('profile'), myAccountMenu)
                    element+= '<li><a id="my_order" href="%s">my order</a><div id="cart_frame"></div></li>' % reverse('cart')
                
                if menu.__class__.__name__ == "FooterMenu":

                    element+= '<li><a id="%s_account_footer" class="btn" href="%s">my account</a>%s</li>' % ('login' if not isLoggedIn else 'my', reverse('profile'), myAccountMenu)

            element += '</ul>'

        return mark_safe(element)


@register.filter
def getInterfaceMenus(menuType, request):

    current_url = request.path
    isLoggedIn = request.user.is_authenticated()

    menuTypes = {
        'info' : InfoMenu,
        'site' : SiteMenu,
        'footer': FooterMenu
    }

    modelMenu = menuTypes[menuType]
    menus = modelMenu.objects.filter(parent=None,deleted=False).order_by('order')

    return menuInterfaceRecursion(menus,current_url, isLoggedIn)


@register.filter
def getEmbellishmentThumbnail(id):

    ret = ''
    embellishment = Embellishments.objects.filter(e_type__id=int(id))
    embellishment = embellishment.latest('id')
    ret = '<img src="/generate_embellishment/?embellishment_id=%s&amp;embellishment_color=000000000&amp;embellishment_thumbnail=1&amp;embellishment_size=100">' % embellishment.id
    
    return mark_safe(ret)


@register.filter
def getEmbellishmentTitle(id):

    ret = ''

    try:

        ret = EmbellishmentsType.objects.get(id=int(id)).title

    except:

        pass

    return ret


@register.filter
def getTextThumbnail(dummy):

    ret = ''
    text = TextFonts.objects.latest('id')
    ret = '<img src="/generate_text/?font_size=100&amp;font_text=Abc&amp;font_color=000000000&amp;font_id=%s&amp;font_thumbnail=1">' % text.id

    return mark_safe(ret)


@register.filter
def truncateDescription(desc,length=50):

    if(len(desc) > length):

        return "%s%s" % (desc[0:length], "...")

    else:

        return desc


@register.filter
def getImagePaymentMethod(met):

    info ={
        "PayPal" : '<img src="/media/images/paypal.jpg" align="bottom" />',
        "Visa" : '<img src="/media/images/visa.jpg" align="bottom" />',
        "Mastercard" : '<img src="/media/images/mastercard.jpg" />',
        "American_Express": '<img src="/media/images/american_express.jpg" />'
    }

    return mark_safe(info.get(met, ""))


@register.filter
# def getPmethodBlah(request):
def getPaymentMethod(request):

    met = request.session.get('order-payment_method')
    info ={
        "PayPal" : 'PayPal',
        "Visa" : 'Visa',
        "Mastercard" : 'Master Card',
        "American_Express": 'American Express'
    }

    return mark_safe(info.get(met, ""))


@register.filter
def get_css_obj_classname(obj):
    
    ret = ''
    object_classname = obj._meta.object_name
    if object_classname == 'Product':
        ret = 'products'
    elif object_classname == 'CustomerStyleBoard':
        ret = 'styleboards'
    elif object_classname == 'HomeBanners':
        ret = 'inspiration'
    elif object_classname == 'ProductAlternateImage':
        ret = 'situation'
    return ret


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_inspiration_link(id):
    obj = HomeBannerImages.objects.get(home_banner__id=int(id))
    return obj.link
