from django import template
from django.utils.safestring import mark_safe
from menu.models import FooterCopyright, InfoMenu, SiteMenu, FooterMenu
from category.services import get_categories, category_tree_crumb, get_cat
from django.core.urlresolvers import reverse
from idecorate_settings.models import IdecorateSettings
from django.contrib.humanize.templatetags.humanize import intcomma
from cart.services import get_product

from customer.services import customer_profile, get_save_styleboard_total
from cart.models import ProductPrice
from admin.models import Embellishments, TextFonts
from django.conf import settings

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
        tags = """
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

        if met == "Visa":
                ret = mark_safe('<img src="/media/images/visa.jpg" align="bottom" />')
        elif met == "Mastercard":
                ret = mark_safe('<img src="/media/images/mastercard.jpg" />')
        else:
                ret = mark_safe('<img src="/media/images/american_express.jpg" />')
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

@register.filter
def getEmbellishmentThumbnail(id):

        ret = ''
        e = Embellishments.objects.filter(e_type__id=int(id))
        e = e.latest('id')

        ret = '<img src="/generate_embellishment/?embellishment_id=%s&amp;embellishment_color=000000000&amp;embellishment_thumbnail=1&amp;embellishment_size=100">' % e.id
        return mark_safe(ret)

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
def truncateDescription(desc):

        if(len(desc) > 50):
                return mark_safe("%s%s" % (desc[0:50], "..."))
        else:
                return mark_safe(desc)

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
