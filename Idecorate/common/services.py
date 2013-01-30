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
    Welcome to iDecorate Weddings!
    <br /><br />
    If you would like to use this email address to login to iDecorate Weddings, you need to set your password by clicking on this link - http://%s/set_password_user/%s.
    <br /><br />
    Thank you for using iDecorate Weddings!
    <br /><br />
    iDecorate Weddings Team
    """ % (settings.IDECORATE_HOST, u.hash_set_password)
    print "SENDING EMAIL...."
    if not settings.SKIPPING_MODE:
        IdecorateEmail.send_mail(mail_from=settings.IDECORATE_MAIL,mail_to=u.user.email,subject='Welcome To iDecorate Weddings',body=messageHTML,isHTML=True)
