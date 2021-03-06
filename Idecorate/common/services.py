import subprocess
import hashlib
import logging
import requests
import urlparse
import urllib
import urllib2
import re
import datetime
import os
import time

from django.conf import settings
from django.template.loader import render_to_string
from uuid import uuid4
from customer.models import CustomerProfile
from cart.models import Contact, GuestTable, OrderStyleboard, ProductPrice
from cart.services import generate_unique_id
from django.utils.html import strip_tags
from customer.services import get_user_styleboard, save_styleboard_item, save_styleboard_as_image
from embellishments.models import StyleboardTemplateItems
from email.mime.image import MIMEImage
from django.contrib.auth.models import User
import cgi

from django.core.mail import EmailMultiAlternatives
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.core.validators import validate_email
from django.core.exceptions import ValidationError 
from django.utils import simplejson  
from django.shortcuts import HttpResponse

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

    @staticmethod
    def send_mail_with_attach(**kwargs):
        mail_from = kwargs.get('mail_from','')
        mail_to = kwargs.get('mail_to','')
        subject = kwargs.get('subject','')
        plain_text = kwargs.get('plain_text','')
        html = kwargs.get('html','')
        # attachement
        image_id =  kwargs.get('image_id','')
        path = kwargs.get('path','')
        filename = kwargs.get('filename','')
        
        sendMail = ["/usr/sbin/sendmail", "-f", mail_from, mail_to]
        sendMail = subprocess.Popen(sendMail, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        
        boundary_related = '===============%s==' %( str(time.time()).replace('.','') )
        boundary_alternative = '===============%s==' %( str(time.time() * 2).replace('.','') )

        email_headers = "Content-Type: multipart/related; boundary=\"%s\"\n" % ( boundary_related )
        email_headers += "MIME-Version: 1.0\n"
        email_headers += "Subject: %s\n" % (subject)
        email_headers += "From: %s\n" % (mail_from)
        email_headers += "To: %s\n" % (mail_to)

        email_headers += "--%s\n" % (boundary_related)

        email_headers += "Content-Type: multipart/alternative; boundary=\"%s\"\n" % (boundary_alternative)
        email_headers += "MIME-Version: 1.0\n"

        email_headers += "--%s\n" % (boundary_alternative)

        email_headers += "Content-Type: text/plain; charset=\"utf-8\"\n"
        email_headers += "MIME-Version: 1.0\n"
        email_headers += "Content-Transfer-Encoding: 7bit\n"
        email_headers += "%s\n" % (plain_text)

        email_headers += "--%s\n" % (boundary_alternative)
        
        email_headers += "Content-Type: text/html; charset=\"utf-8\"\n"
        email_headers += "MIME-Version: 1.0\n"
        email_headers += "Content-Transfer-Encoding: 7bit\n"
        email_headers += "%s\n" % (html)

        email_headers += "--%s\n" % (boundary_alternative)

        email_headers += "--%s\n" % (boundary_related)

        styleboard = "%s%s" % (path, filename)
        image_data = open(styleboard, "rb").read()
        image = MIMEImage(image_data)

        email_headers += "Content-Type: image/png\n"
        email_headers += "MIME-Version: 1.0\n"
        email_headers += "Content-Transfer-Encoding: base64\n"
        email_headers += "Content-ID: <%s>\n" %(image_id)
        email_headers += "Content-Disposition: inline\n"
        email_headers += "%s\n" % (image)
        
        email_headers += "--%s\n" % (boundary_related)

        cmd = "%sFrom: %s\nTo: %s\nSubject: %s\n\n%s\n.\n" % (email_headers,mail_from, mail_to, subject, plain_text)
        
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
    If you would like to use this email address to login to iDecorateweddings.com, you need to set your password by clicking on this link - %s/set_password_user/%s.
    <br /><br />
    Thank you for joining iDecorateweddings.com!
    <br /><br />
    From the iDecorateweddings.com Team
    """ % (settings.IDECORATE_HOST, u.hash_set_password)
    print "SENDING EMAIL...."
    if not settings.SKIPPING_MODE:
        IdecorateEmail.send_mail(mail_from=settings.IDECORATE_MAIL,mail_to=u.user.email,subject='Welcome To iDecorateweddings.com',body=messageHTML,isHTML=True)

def send_email_reset_password(user_id):
    
    customer = CustomerProfile.objects.get(user__id=int(user_id))
    customer.hash_set_password = str(uuid4())
    customer.save()

    messageHTML = """
    <h2 style="color:#666666;">Hi %s,</h2>
    <p style="color:#666666;">
        iDecorateWeddings.com has received a request to reset the password for your account (Username: %s).
    </p>
    <p style="color:#666666;">
        You can reset your password on the link below. If you did not request to reset your password, you can ignore this email.
    </p>
    <a style="color:#000000;" href="%s/set_password_user/%s" >
        <h5 style="display:inline-block;color:#000000;">RESET PASSWORD</h5>
    </a>
    """ % (customer.nickname, customer.user.username, settings.IDECORATE_HOST, customer.hash_set_password)
   
    email = EmailMultiAlternatives(subject="Reset your iDecorateWeddings.com password", body="this email is generated by www.idecorateweddings.com", from_email="noreply@idecorateweddings.com", to=[customer.user.email,])
    email.attach_alternative(messageHTML, "text/html")

    return email.send()

def send_email_order(order, user, comment, contact_number, shop):

    info = {}

    group = GuestTable.objects.get(order=order)
    products = order.items.filter().order_by('-id')
    contact = Contact.objects.get(user=user)
    styleboard = "%s/media/images/styleboard.jpg" % settings.IDECORATE_HOST
    
    try:
        order_styleboard = OrderStyleboard.objects.get(order=order)
        styleboard = "%s/media/styleboards/%s" % (settings.IDECORATE_HOST, order_styleboard.styleboard)
    except:
        pass

    info['styleboard'] = styleboard
    info['order'] = order
    info['user'] = user
    info['contact'] = contact
    info['products'] = products
    info['idecorate_host'] = settings.IDECORATE_HOST
    info['group'] = group

    if comment :

        info['comment'] = unicode(comment).encode('ascii','xmlcharrefreplace')

    if contact_number:
        
        info['contact_number'] = contact_number


    messageHTML = render_to_string('plata/shop_order_email.html', info)

    mail_to = []
    mail_to.append(user.email)

    admins = User.objects.filter(is_superuser = True, is_active= True)
    for admin in admins:
        mail_to.append(admin.email)
        
    email = EmailMultiAlternatives(subject="Order Confirmation", body="this email is generated by www.idecorateweddings.com", from_email="noreply@idecorateweddings.com", to=mail_to)
    email.attach_alternative(messageHTML, "text/html")
    
    return email.send()

def st_save_helper(request,order):

    going_to_save = {}
    going_to_save['personalize_total'] = None

    if 'customer_styleboard' in request.session or 'style_board_in_session' in request.session or 'personalize_id' in request.session or 'personalize_id_logged_out' in request.session:
        
        style_board_in_session = request.session.get('style_board_in_session', None)

        customer_styleboard = request.session.get('customer_styleboard',None)
        
        personalize_styleboard = None

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

            going_to_save={
            'name':customer_styleboard.styleboard_item.name,
            'description':customer_styleboard.styleboard_item.description
            }


        else:

            going_to_save={
                'name':order.order_id,
                'description':order.order_id
            }

        if customer_styleboard:

            going_to_save['browser'] = customer_styleboard.styleboard_item.browser
            going_to_save['item'] = customer_styleboard.styleboard_item.item
            going_to_save['guest'] = customer_styleboard.styleboard_item.item_guest
            going_to_save['tables'] = customer_styleboard.styleboard_item.item_tables
            going_to_save['personalize_total'] = customer_styleboard.total_price

        elif personalize_styleboard:

            going_to_save['browser'] = personalize_styleboard.styleboard_item.browser
            going_to_save['item'] = personalize_styleboard.styleboard_item.item
            going_to_save['guest'] = personalize_styleboard.styleboard_item.item_guest
            going_to_save['tables'] = personalize_styleboard.styleboard_item.item_tables
            going_to_save['personalize_total'] = personalize_styleboard.total_price

        else : 

            going_to_save['browser'] = style_board_in_session['bwsr']
            going_to_save['item'] = style_board_in_session['djsn']
            going_to_save['guest'] = style_board_in_session['guest']
            going_to_save['tables'] = style_board_in_session['table']

        
        going_to_save['user'] = request.user
        going_to_save['customer_styleboard'] = customer_styleboard
        going_to_save['sessionid'] = request.session.get('cartsession',generate_unique_id())
        going_to_save['description'] = strip_tags(going_to_save['description'])
        going_to_save['session_in_request'] = request.session  

        result = save_styleboard_item(going_to_save)

        if result:
            # print result.styleboard_item
            styleboard_img = save_styleboard_as_image(result.styleboard_item.id)

            try:
                order_styleboard = OrderStyleboard.objects.get(order=order)
                
                path = '%sstyleboards/%s' % (settings.MEDIA_ROOT, order_styleboard.styleboard)
                os.unlink(path)
                
                order_styleboard.order = order
                order_styleboard.styleboard_name = result.styleboard_item.name
                order_styleboard.styleboard = styleboard_img
                order_styleboard.save()

            except :

                order_styleboard = OrderStyleboard()
                order_styleboard.order = order
                order_styleboard.styleboard_name = result.styleboard_item.name
                order_styleboard.styleboard = styleboard_img
                order_styleboard.save()

        if request.session.get('save_template'):

            try :
                
                template = StyleboardTemplateItems.objects.get(id=int(request.session.get('save_template')))
                template.is_used = True
                template.save()
            
            except Exception as e:
                
                print e

        request.session['customer_styleboard'] = result

    return going_to_save

def set_cookie(response, key, value, days_expire = 7):
    if days_expire is None:
        max_age = 365 * 24 * 60 * 60  #one year
    else:
        max_age = days_expire * 24 * 60 * 60 
        expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
        response.set_cookie(key, value, max_age=max_age, expires=expires, domain=settings.SESSION_COOKIE_DOMAIN, secure=settings.SESSION_COOKIE_SECURE or None)


def render_to_json(request, data):

    return HttpResponse(simplejson.dumps(data, ensure_ascii=False),  mimetype=request.is_ajax() and "application/json" or "text/html" )


