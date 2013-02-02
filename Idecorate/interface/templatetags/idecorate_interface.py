from django import template
from django.utils.safestring import mark_safe
from menu.models import FooterCopyright, InfoMenu, SiteMenu, FooterMenu, FatFooterMenu, ItemMenu
from category.services import get_categories, category_tree_crumb, get_cat
from django.core.urlresolvers import reverse
from idecorate_settings.models import IdecorateSettings
from django.contrib.humanize.templatetags.humanize import intcomma
from cart.services import get_product

from customer.services import customer_profile, get_save_styleboard_total
from cart.models import ProductPrice, Contact
from admin.models import Embellishments, TextFonts, EmbellishmentsType
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
        tags = """
                <ul>                
        """
        for cat in parent_category:
                tags += """
                        <li><a href="%s">%s</a></li>
                """ % (reverse('styleboard_cat', args=[cat.id]), cat.name)
                
        tags += """
                </ul>
        """

        return mark_safe(tags)

@register.filter
def get_category_nav(value):
        parent_category = get_categories(None)

        parent_category = parent_category.order_by('order')
        item_menu = ItemMenu.objects.filter(deleted=0,parent=None).order_by('order')

        tags = menuItemInterface(item_menu)

        tags += """
                <ul class="dd">                
        """
        for cat in parent_category:
                tags += """
                        <li><a href="%s">%s</a>
                """ % (reverse('styleboard_cat', args=[cat.id]), cat.name)

                sub_cat = get_categories(cat.id)
                if sub_cat.count() > 0:
                        tags += '<ul>'
                        for scat in sub_cat:
                                tags += '<li><a href="%s">%s</a></li>' % (reverse('styleboard_cat', args=[scat.id]), scat.name)
                        tags += '</ul>'

                tags += """
                        </li>
                """
                
        tags += """
                </ul>
        """

        return mark_safe(tags)

def menuItemInterface(item_menu,is_sub=False):
        menus = ""

        if is_sub:
                menus += "<ul>"
        else:
                menus += "<ul class=\"dd\">"

        for menu in item_menu:
                menus += '<li><a href="%s">%s</a>' % (menu.link, menu.name)
                sub_menus = ItemMenu.objects.filter(parent=menu.id,deleted=0)
                if sub_menus.count() > 0:
                        menus += menuItemInterface(sub_menus,True)
                menus += '</li>'

        menus += "</ul>"

        return menus


def menuInterfaceRecursion(menus):

        element = ""
        needToOpen = True
        css_class = ""
        link = ""
        needSpan = False

        for menu in menus:
                if menu.parent is None:
                        if needToOpen:
                                element += '<ul class="dd">'
                                needToOpen = False

                else:
                        if needToOpen:
                                element += '<ul>'
                                needToOpen = False

                if menu.link == "":
                        needSpan = True
                        link = menu.name
                else:
                        needSpan = False
                        link = '<a href="%s">%s</a>' % (menu.link, menu.name)

                if needSpan:
                        element += '<li>%s%s%s' % ('<span>',link ,'</span>')
                else:
                        element += '<li>%s' % (link)

                if menus.model == type(InfoMenu()):

                        sub_menus = InfoMenu.objects.filter(parent__id=menu.id,deleted=False).order_by('order')
                        element += menuInterfaceRecursion(sub_menus)

                else:
                        sub_menus = SiteMenu.objects.filter(parent__id=menu.id,deleted=False).order_by('order')
                        element += menuInterfaceRecursion(sub_menus)

                element +='</li>'

        if needToOpen == False:
                element += '</ul>'

        return mark_safe(element)

@register.filter
def getInterfaceMenus(menuType):

        if menuType == "info":
                menus = InfoMenu.objects.filter(parent=None,deleted=False).order_by('order')
        else:
                menus = SiteMenu.objects.filter(parent=None,deleted=False).order_by('order')

        return menuInterfaceRecursion(menus)

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
                                                        <td>%sx %s</td>
                                                        <td>%s%s</td>
                                                        <td>%s%s</td>
                                                </tr>
                """ % (product.quantity, product.product.sku, "$", intcomma("%.2f" % product.unit_price), "$", intcomma("%.2f" % product.discounted_subtotal))

        return mark_safe(ret)


@register.filter
def generate_product_order_list(obj,objMain):
        products = obj.filter().order_by('-id')

        """
        for product in products:
                print str(product.id) + ' : ' + str(product.name) 
        """
        ret = ""

        for product in products:

                ret += """
                                                <tr>
                                                        <td>
                                                                <img src="/media/products/%s" align="left" />
                                                                <span>%s/%s</span>
                                                        </td>
                                                        <td valign="middle" class="productPricing">
                                                                %s%s
                                                        </td>
                                                        <td valign="middle" class="productPricing">
                                                                %s
                                                        </td>
                                                        <td valign="middle" class="productPricing">
                                                                %s%s
                                                        </td>
                                                </tr>
                """ % (product.product.original_image_thumbnail, product.product.sku, product.product.name, "$", intcomma("%.2f" % product.unit_price), product.quantity, "$", intcomma("%.2f" % product.discounted_subtotal))

        return mark_safe(ret)

@register.filter
def get_checkout_page_info(inf):

        idecorate_settings = IdecorateSettings.objects.get(pk=1)

        if inf == "delivery_date_note":
                return mark_safe(idecorate_settings.delivery_date_note)
        elif inf == "any_question":
                return mark_safe(idecorate_settings.any_question)
        elif inf == "t_and_c":
                return mark_safe(idecorate_settings.t_and_c)
        else:
                return ""

@register.filter
def getImagePaymentMethod(met):
        ret = ""

        if met == "PayPal":
                ret = mark_safe('<img src="/media/images/paypal.jpg" align="bottom" />')
        elif met == "Visa":
                ret = mark_safe('<img src="/media/images/visa.jpg" align="bottom" />')
        elif met == "Mastercard":
                ret = mark_safe('<img src="/media/images/mastercard.jpg" />')
        else:
                ret = mark_safe('<img src="/media/images/american_express.jpg" />')
        return ret

@register.filter
def getPmethodBlah(request):

        met = request.session.get('order-payment_method','')
        ret = ""

        if met == "PayPal":
                ret = mark_safe('PayPal')
        elif met == "Visa":
                ret = mark_safe('Visa')
        elif met == "Mastercard":
                ret = mark_safe('Master Card')
        else:
                ret = mark_safe('American Express')
        return ret

@register.filter
def get_nickname(user):
        try:
                profile = customer_profile(user)
                return profile['nickname']
        except:
                return ""

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
def linebreak(txt):
        return mark_safe(txt.replace("\n", '<br />'))
        #return txt.replace("\n", '<br />')

@register.filter
def getEmbellishmentThumbnail(id):

        ret = ''
        e = Embellishments.objects.filter(e_type__id=int(id))
        e = e.latest('id')

        ret = '<img src="/generate_embellishment/?embellishment_id=%s&amp;embellishment_color=000000000&amp;embellishment_thumbnail=1&amp;embellishment_size=100">' % e.id
        return mark_safe(ret)

@register.filter
def getEmbellishmentTitle(id):

        ret = ''

        try:
                ret = EmbellishmentsType.objects.get(id=int(id)).name
        except:
                pass

        return ret

@register.filter
def getTextThumbnail(dummy):

        ret = ''
        t = TextFonts.objects.latest('id')

        ret = '<img src="/generate_text/?font_size=100&amp;font_text=Abc&amp;font_color=000000000&amp;font_id=%s&amp;font_thumbnail=1">' % t.id

        return mark_safe(ret)

@register.filter
def get_url(request):
        return request.build_absolute_uri()

@register.filter
def get_host(request):
        return request.get_host()

@register.filter
def truncateDescription(desc,length=50):

        if(len(desc) > length):
                #return mark_safe("%s%s" % (desc[0:50], "..."))
                return "%s%s" % (desc[0:length], "...")
        else:
                #return mark_safe(desc)
                return desc

@register.filter
def set_last_page_idecorate(request):
        try:
                request.session['last_page_idecorate'] = request.get_full_path()
        except:
                pass

        #print request.get_full_path()

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

        pagination = """<div class="pagination"><ul>"""
        
        if page_of_page: #show page of pages
                pagination += """<li><span class="pageofpage">Page %s of %s.</span></li>""" % (object_list.number,object_list.paginator.num_pages)
        
        if object_list.has_previous():
                pagination += """<li><a class="prev" href="?page=%s">Previous</a></li>""" % (object_list.previous_page_number())

        if object_list.paginator.page_range and len(object_list.paginator.page_range) > 1:
                
                for page in object_list.paginator.page_range:
                        if page == current_page:
                                pagination += """<li><span class="current">%s</span></li>""" % (page)
                        else:
                                pagination += """<li><a href="?page=%s">%s</a></li>""" % (page,page)
        
        if object_list.has_next():
                pagination += """<li><a class="next" href="?page=%s">Next</a></li>""" % (object_list.next_page_number())
        
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

