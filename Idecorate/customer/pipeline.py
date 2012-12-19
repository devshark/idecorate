from social_auth.backends.twitter import TwitterBackend
from social_auth.backends.facebook import FacebookBackend
from customer.models import CustomerProfile
from django.contrib.auth.models import User
from common.services import IdecorateEmail
from uuid import uuid4
from django.conf import settings

def get_user_avatar(backend, details, response, social_user, uid, user, *args, **kwargs):

    url = None
    desc = None

    if backend.__class__ == FacebookBackend:
        desc = response.get('bio','')
        url = "http://graph.facebook.com/%s/picture?type=large" % response['id']

    elif backend.__class__ == TwitterBackend:
        desc = response.get('description','')
        url = response.get('profile_image_url', '').replace('_normal', '')

    prof = None

    try:
        prof = CustomerProfile.objects.get(user__id=user.id)

        if prof.picture != url:
            prof.picture =  url
            prof.save()

        if prof.description != desc:
            prof.description = desc
            prof.save()

    except:
        prof = CustomerProfile()
        prof.user = User.objects.get(id=user.id)
        prof.nickname = user.username
        prof.description = desc
        prof.picture = url
        prof.save()

    if User.objects.get(id=user.id).password == "!":
        u = CustomerProfile.objects.get(user__id=user.id)
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

        IdecorateEmail.send_mail(mail_from='noreply@idecorateweddings.com',mail_to=User.objects.get(id=user.id).email,subject='Welcome To iDecorate Weddings',body=messageHTML,isHTML=True)


    """
    if url:
        profile = user.get_profile()
        avatar = urlopen(url).read()
        fout = open(filepath, "wb")
        fout.write(avatar)
        fout.close()
        profile.photo = url_to_image
        profile.save()
    """