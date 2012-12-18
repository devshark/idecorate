import subprocess

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
        sendMail = subprocess.Popen(sendMail, stdin=None, stdout=None, stderr=None)
        
        htmlHeader = "MIME-Version: 1.0\nContent-type: text/html; charset=iso-8859-1\n" if isHTML else ""
        cmd = "%sFrom: %s\nTo: %s\nSubject: %s\n\n%s\n.\n" % (htmlHeader,mail_from, mail_to, subject, body)
        
        sendMail.communicate(cmd)