import subprocess
import hashlib
import logging
import requests
import urlparse
import urllib
import urllib2
import re

from django.conf import settings
from django.template.loader import render_to_string
from uuid import uuid4
from customer.models import CustomerProfile
from cart.models import Contact, GuestTable
from cart.services import generate_unique_id
from django.utils.html import strip_tags
from customer.services import get_user_styleboard, save_styleboard_item
import cgi

def ss_direct(params, url, secure=False):
    """
    API for Server Side Direct Connection.

    @params:
    @param url: PayDollar post url
    @param params: dictionary of parameters to be posted to PayDollar
    @param secure: Boolean, wether or not we should generate secure hash
    """

    if secure:
        params['secureHash'] = generate_secure_hash(
            params['merchantId'],
            params['orderRef'],
            params['currCode'],
            params['amount'],
            params['payType'],
            settings.PAYDOLLAR_SECURE_HASH_SECRET)

    #logger.debug("CC Payload: %s" % str(params))

    params = urllib.urlencode(params)
    headers = {"Content-type": "application/x-www-form-urlencoded"}

    result = {}
    try:
        response = requests.post(url, data=params, headers=headers, verify=True)
        result = flatten_response(urlparse.parse_qs(response.text))
        #print "The result is: %s" % result
    except requests.ConnectionError:
        #logger.debug("Connection Error: url=%s, result=%s" % (url, str(result)))
        print "Connection Error: url=%s, result=%s" % (url, str(result))
        
    if not 'successcode' in result:
        result['successcode'] = -1

    if not 'errMsg' in result:
        result['errMsg'] = 'error'
        
    return result

def generate_secure_hash(merchant_id, order_ref, curr, amount, pay_type,
    hash_secret):
    """
    Helper for generating secure hash.
    """
    param_str = '|'.join([
        merchant_id,
        order_ref,
        curr,
        amount,
        pay_type,
        hash_secret
    ])
    print param_str
    #logger.debug(param_str)
    return hashlib.sha1(param_str).hexdigest()

def verify_secure_hash(src, prc, success_code, ref, pay_ref, curr, amount,
    payer_auth, hash_secret, secure_hash):
    """
    Helper for verifying secure hash, should be called from datafeed.
    """
    param_str = '|'.join([
        src,
        prc,
        success_code,
        ref,
        pay_ref,
        curr,
        amount,
        payer_auth,
        hash_secret
    ])
    print param_str
    #logger.debug(param_str)
    return hashlib.sha1(param_str).hexdigest() == secure_hash


def flatten_response(response):
    """
    Convert single itemed-list to just the value itself.
    ie. 'Cur': [u'840'] => 'Cur': u'840'
    """
    for key, val in response.items():
        if isinstance(val, list) and len(val) == 1:
            response[key] = val[0]
    return response

"""
------------------------------------------------------
Usage:
------------------------------------------------------
from common.services import IdecorateEmail

IdecorateEmail.send_mail(mail_from='from@from.com',mail_to='to@to.com',subject='subject',body='body',isHTML=True) #if HTML

"""

class IdecorateEmail(object):
    
    @staticmethod
    def send_mail(**kwargs):
        mail_from = kwargs.get('mail_from','')
        mail_to = kwargs.get('mail_to','')
        subject = kwargs.get('subject','')
        body = kwargs.get('body','')
        isHTML = kwargs.get('isHTML',False)
        
        sendMail = ["/usr/sbin/sendmail", "-f", mail_from, mail_to]
        sendMail = subprocess.Popen(sendMail, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        
        htmlHeader = "MIME-Version: 1.0\nContent-type: text/html; charset=iso-8859-1\n" if isHTML else ""
        cmd = "%sFrom: %s\nTo: %s\nSubject: %s\n\n%s\n.\n" % (htmlHeader,mail_from, mail_to, subject, body)
        
        sendMail.communicate(cmd)

def tinyurl(url):
    
    if not re.search('^http:\/\/',str(url).strip()):
        url = "%s%s" % ('http://', str(url).strip())

    httpResponse = urllib2.urlopen('http://tinyurl.com/api-create.php?url=%s' % url)

    return str(httpResponse.read())

def send_email_set_pass(user_id):
    u = CustomerProfile.objects.get(user__id=int(user_id))
    u.hash_set_password = str(uuid4())
    u.save()

    messageHTML = """
    Welcome to iDecorateweddings.com!
    <br /><br />
    Where you can create and buy your dream wedding. online. 
    <br /><br />
    If you would like to use this email address to login to iDecorateweddings.com, you need to set your password by clicking on this link - http://%s/set_password_user/%s.
    <br /><br />
    Thank you for joining iDecorateweddings.com!
    <br /><br />
    From the iDecorateweddings.com Team
    """ % (settings.IDECORATE_HOST, u.hash_set_password)
    print "SENDING EMAIL...."
    if not settings.SKIPPING_MODE:
        IdecorateEmail.send_mail(mail_from=settings.IDECORATE_MAIL,mail_to=u.user.email,subject='Welcome To iDecorateweddings.com',body=messageHTML,isHTML=True)

def send_email_order(order, user, shop, sbid, comment):

    guest_table = GuestTable.objects.get(order=order)

    itemsHTML = ""
    board = "http://%s/media/images/styleboard.jpg" % settings.IDECORATE_HOST
    
    if sbid:
    	board = "http://%s/styleboard/generate_styleboard_view/%s/560/200/" % (settings.IDECORATE_HOST, sbid)

    c_block = ""
    if comment:
        c_block = """
    <tr>
    <td colspan="5" style="text-align:center; padding:10px 10px;  font-size:14px; ">SPECIAL REQUESTS AND COMMENTS</td>
    </tr>    
    <tr>
        <td colspan="5" style="vertical-align:top; font-size:23px; padding:0 10px;">
        <table width="580" border="0" cellpadding="0" cellspacing="0" style=" border:1px solid #bfbfbf; font-size:13px;" >
        <tr>
        <td colspan="3" style="padding:10px; font-size:12px;">
        %s
        </td>
       
        </tr>
        </table>
       </td>
    </tr>
        """ % unicode(comment).encode('ascii','xmlcharrefreplace')

    products = order.items.filter().order_by('-id')

    for product in products:
        itemsHTML += """
    <tr>
        <td style="font-size:13px; vertical-align:middle; padding:10px 0 10px 10px;">
            <span style="display:inline-block;"><img src="%s" width="51" height="50" alt="" style="vertical-align:middle;"></span>
            <span style="display:inline-block;"><font>%s</font></span>
        </td>   
        <td style="font-size:13px; vertical-align:middle; text-align:right; padding:10px 0 10px 0px;">
            %s</td>
        <td style="font-size:13px; vertical-align:middle; text-align:right; padding:10px 0 10px 0px;">
            %s</td>
        <td style="font-size:13px; vertical-align:middle; text-align:right; padding:10px 0 10px 0px;">
            %s</td>
        <td style="font-size:13px; vertical-align:middle; text-align:right; padding:10px 10px 10px 0px;">
            %s</td>
    </tr>
        """ % (
            "http://%s%s%s" % (settings.IDECORATE_HOST,"/media/products/", product.product.original_image_thumbnail),
            product.product.name,
            product.product.sku,
            "%s%.2f" % ("$",product.unit_price),
            product.quantity,
            "%s%.2f" % ("$", product.discounted_subtotal)
        )

    contact = Contact.objects.get(user=user)

    messageHTML = """
<html>
<head>
<title>Order Confirmation</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
</head>
<body bgcolor="#FFFFFF" leftmargin="0" topmargin="0" marginwidth="0" marginheight="0" style="font-family: Arial, Helvetica, sans-serif;">
<table id="Table_01" width="580" height="937" border="0" cellpadding="0" cellspacing="0" style="margin:0 auto;">
    <!--iDecorate Logo-->
    <tr>
        <td colspan="5" style="height:119px; text-align:center;">
            <img src="http://%s/media/images/header.jpg" width="580" height="119" alt=""></td>
    </tr>
    <!--Styleboard -->
    <tr>
        <td colspan="5" style="text-align:center; vertical-align:middle; padding:10px 5px;">
            <img src="%s" width="560" height="200" alt="" style="border:10px solid #f0ece5;" ></td>
    </tr>
    <!--Thank you message -->
    <tr>
        <td colspan="5" style="text-align:center; vertical-align:middle; padding:10px 5px; font-size:23px;">
            Thank you for your purchase!</td>
    </tr>
        </tr>
    <!--Personal Information -->
    <tr>
    <td colspan="5" style="text-align:center; padding:10px 10px;  font-size:16px; ">PERSONAL INFORMATION</td>
    </tr>    
    <tr>
        <td colspan="5" style="vertical-align:middle; font-size:23px; padding:0 10px;">
        <table width="580" border="0" cellpadding="0" cellspacing="0" style="vertical-align:middle; border:1px solid #bfbfbf; font-size:13px;" >
        <tr>
        <td colspan="3" style="padding:10px 0 0 150px;">Salutation</td>
        <td width="319" colspan="2" style="padding:10px 0 0 0;" >%s</td>
        </tr>
        <tr>
        <td colspan="3" style="padding:5px 0 0 150px;">First name</td>
        <td width="319" colspan="2" style="padding:5px 0 0 0;" >%s</td>
        </tr>
        <tr>
        <td colspan="3" style="padding:5px 0 0 150px;">Last name</td>
        <td width="319" colspan="2" style="padding:5px 0 0 0;" >%s</td>
        </tr>
                <tr>
        <td colspan="3" style="padding:5px 0 10px 150px;">Email</td>
        <td width="319" colspan="2" style="padding:5px 0 10px 0;;">%s</td>
        </tr>
        </table>
       </td>
    </tr>
    
     <tr>
        <td colspan="5" style="padding:0 10px;">
        <table width="580" border="0" cellpadding="0" cellspacing="0" style="vertical-align:middle;" >
        <tr>
        <!--Delivery Address -->
        <td colspan="3" style=" padding:20px 0 0 0;">
        DELIVERY ADDRESS
        <table width="285" border="0" cellpadding="0" cellspacing="0" style=" border:1px solid #bfbfbf; font-size:12px; margin:10px 0 0 0;" >
        <tr>
        <td colspan="3" style="padding:10px 0 0 10px;">Address 1</td>
        <td width="184" colspan="2" style="padding:10px 0 0 5px;" >%s</td>
        </tr>
        <tr>
        <td colspan="3" style="padding:5px 0 0 10px;">Address 2</td>
        <td width="184" colspan="2" style="padding:5px 0 0 5px;" >%s</td>
        </tr>
        <tr>
        <td colspan="3" style="padding:5px 0 0 10px;">City</td>
        <td width="184" colspan="2" style="padding:5px 0 0 5px;" >%s</td>
        </tr>
        <tr>
        <td colspan="3" style="padding:5px 0 0 10px;">State </td>
        <td width="184" colspan="2" style="padding:5px 0 0 5px;" >%s</td>
        </tr>
        <tr>
        <td colspan="3" style="padding:5px 0 0 10px;">Postal Code</td>
        <td width="184" colspan="2" style="padding:5px 0 0 5px;;">%s</td>
        </tr>
        <tr>
        <td colspan="3" style="padding:5px 0 10px 10px;">Country</td>
        <td width="184" colspan="2" style="padding:5px 0 10px 5px;">%s</td>
        </tr>
        </table>
        </td>
        <!--Billing Address -->
        <td width="319" colspan="2" style="padding:20px 0 0 10px;">
        BILLING ADDRESS
        <table width="285" border="0" cellpadding="0" cellspacing="0" style=" border:1px solid #bfbfbf; font-size:12px; margin:10px 0 0 0" >
        <tr>
        <td colspan="3" style="padding:10px 0 0 10px;">Address 1</td>
        <td width="184" colspan="2" style="padding:10px 0 0 5px;" >%s</td>
        </tr>
        <tr>
        <td colspan="3" style="padding:5px 0 0 10px;">Address 2</td>
        <td width="184" colspan="2" style="padding:5px 0 0 5px;" >%s</td>
        </tr>
        <tr>
        <td colspan="3" style="padding:5px 0 0 10px;">City</td>
        <td width="184" colspan="2" style="padding:5px 0 0 5px;" >%s</td>
        </tr>
        <tr>
        <td colspan="3" style="padding:5px 0 0 10px;">State </td>
        <td width="184" colspan="2" style="padding:5px 0 0 5px;" >%s</td>
        </tr>
        <tr>
        <td colspan="3" style="padding:5px 0 0 10px;">Postal Code</td>
        <td width="184" colspan="2" style="padding:5px 0 0 5px;">%s</td>
        </tr>
        <tr>
        <td colspan="3" style="padding:5px 0 10px 10px;">Country</td>
        <td width="184" colspan="2" style="padding:5px 0 10px 5px;">%s</td>
        </tr>
        </table>
        
        </td>
        </tr>       
        </table>
        </td>
 </tr>
    <tr>
    <!--Order Number-->
    <td colspan="3" style="text-align:left;  padding:20px 0 10px 10px; font-size:16px; ">Order # %s</td>
    <!--Date-->
    <td colspan="2" style="text-align:right; padding:20px 10px 10px 0; font-size:12px; ">Date : %s</td>
    </tr> 
    
    <tr >
        <td width="318" style="font-size:14px; vertical-align:middle; padding:10px 0 10px 10px;">
            Items</td>
        <td width="66" style="font-size:14px; vertical-align:middle; text-align:right; padding:10px 0 10px 0px;">
      Sku</td>
        <td width="82" style="font-size:14px; vertical-align:middle; text-align:right; padding:10px 0 10px 0;">
        Unit Cost
        </td>
        <td width="43" style="font-size:14px; vertical-align:middle; text-align:right; padding:10px 0 10px 0;">
            Qty</td>
        <td width="91" style="font-size:14px; vertical-align:middle; text-align:right; padding:10px 10px 10px 0;">
            Price</td>
    </tr>
    <tr>
        <td colspan="5"  style="padding-bottom:10px;">
            
            <img src="http://%s/media/images/line_1.jpg" width="600" height="1" alt=""></td>
    </tr>
    %s
    <tr>
        <td colspan="5" style="padding-top:10px; padding-bottom:20px;">
            <img src="http://%s/media/images/line_1.jpg" width="600" height="1" alt=""></td>
    </tr>
    <tr style="padding:10px 0 10px 0;">
        <!--Guests and Tables-->
        <td colspan="3" style="font-size:13px; font-weight:bold; padding-left:10px; padding-top:5px; vertical-align:top;">
        %s Guests / %s Tables
        </td>
        <!--Shipping Fee-->
        <td colspan="2" style="font-size:12px; text-align:right; padding-right:10px;">&nbsp; 
        <!--Total-->
        <div style="margin-top:10px; background-color:#f8e5e2; text-align:center; vertical-align:middle; padding:10px 0 10px 0; font-size:14px; font-weight:bold;">Total: %s</div>
        </td>
</tr>
    <tr>
        <td colspan="5" style="padding-top:20px; padding-bottom:10px;">
            
            <img src="http://%s/media/images/line_2.jpg" width="600" height="3" alt=""></td>
    </tr>
    <!--Footer-->
    %s
    <tr>
        <td colspan="5" style="height:55px; font-size:11px; text-align:center;">This is just an automated request. Please do not reply to this email.<br>
Follow this <a href="http://%s/">link</a> if you wish to get in touch with us. 


</td>
    </tr>
</table>

</body>
</html>
    """ % (
        settings.IDECORATE_HOST,
        board,
        contact.billing_salutation,
        user.first_name,
        user.last_name,
        user.email,
        contact.address,
        contact.shipping_address2,
        contact.city,
        contact.shipping_state,
        contact.zip_code,
        contact.countries,
        contact.address2,
        contact.billing_address2,
        contact.city2,
        contact.billing_state,
        contact.zip_code2,
        contact.countries2,
        order.order_id,
        order.created,
        settings.IDECORATE_HOST,
        itemsHTML,
        settings.IDECORATE_HOST,
        guest_table.guests,
        guest_table.tables,
        "$%.2f" % order.total,
        settings.IDECORATE_HOST,
        c_block,
        settings.IDECORATE_HOST
    )

    #messageHTML = messageHTML.decode('unicode-escape').encode('ascii','xmlcharrefreplace')
    print messageHTML
    if not settings.SKIPPING_MODE:
        IdecorateEmail.send_mail(mail_from=settings.IDECORATE_MAIL,mail_to=user.email,subject='iDecorateweddings.com Order Confirmation',body=messageHTML,isHTML=True)

def st_save_helper(request,order):

    going_to_save = {}
    going_to_save['personalize_total'] = None

    if 'style_board_in_session' in request.session or 'personalize_id' in request.session or 'personalize_id_logged_out' in request.session:

        style_board_in_session = request.session.get('style_board_in_session')

        customer_styleboard = request.session.get('customer_styleboard',None)
        if not customer_styleboard:
            sbid = request.session.get('personalize_id', None)

            if not sbid:
            	sbid = request.session.get('personalize_id_logged_out', None)

            if sbid:
                personalize_styleboard = get_user_styleboard(None, sbid)
                if personalize_styleboard:
                    if personalize_styleboard.user.id:              
                        if int(personalize_styleboard.user.id) == int(request.user.id):
                            customer_styleboard = personalize_styleboard

        if customer_styleboard:
            going_to_save={'name':customer_styleboard.styleboard_item.name,'description':customer_styleboard.styleboard_item.description}
        else:
            going_to_save={
                'name':order.order_id,
                'description':order.order_id
            }

        if style_board_in_session:
        	going_to_save['browser'] = style_board_in_session['bwsr']
        	going_to_save['item'] = style_board_in_session['djsn']
        	going_to_save['guest'] = style_board_in_session['guest']
        	going_to_save['tables'] = style_board_in_session['table']
        else:
        	going_to_save['browser'] = personalize_styleboard.styleboard_item.browser
        	going_to_save['item'] = personalize_styleboard.styleboard_item.item
        	going_to_save['guest'] = personalize_styleboard.styleboard_item.item_guest
        	going_to_save['tables'] = personalize_styleboard.styleboard_item.item_tables
        	going_to_save['personalize_total'] = personalize_styleboard.total_price
        
        going_to_save['user'] = request.user
        going_to_save['customer_styleboard'] = customer_styleboard
        going_to_save['sessionid'] = request.session.get('cartsession',generate_unique_id())
        going_to_save['description'] = strip_tags(going_to_save['description'])
        going_to_save['session_in_request'] = request.session       
        res = save_styleboard_item(going_to_save)
        request.session['customer_styleboard'] = res

    return going_to_save