from social_auth.backends.twitter import TwitterBackend
from social_auth.backends.facebook import FacebookBackend
from customer.models import CustomerProfile #, CustomerFacebookFriends
from django.contrib.auth.models import User
from common.services import IdecorateEmail, send_email_set_pass
from uuid import uuid4
from django.conf import settings
import urllib
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from social_auth.models import UserSocialAuth, SOCIAL_AUTH_MODELS_MODULE
from social_auth.exceptions import AuthException, AuthAlreadyAssociated
from django.utils.translation import ugettext
from social_auth.backends.pipeline.social import social_auth_user

class AuthEmailTaken(AuthException):
    pass

def associate_by_username(details, user=None, *args, **kwargs):   
    
    if user:
        return None
    email = details.get('email')
    if email:

        backend = kwargs['backend']
        uid = kwargs['uid']
        social_user = UserSocialAuth.get_social_auth(backend.name, uid)

        try:
            user = User.objects.get(username=email)
        except ObjectDoesNotExist:
            pass

        if not social_user:
            if user:

                try:
                    social = UserSocialAuth.objects.get(user=user, provider=backend.name)
                    msg = ugettext('This %(provider)s account is already in use.')
                    
                    raise AuthEmailTaken(backend, msg % {
                        'provider': backend.name
                    })

                except ObjectDoesNotExist:
                    pass

                try:
                    social_user = UserSocialAuth.create_social_auth(user, uid, backend.name)
                except Exception, e:
                    if not SOCIAL_AUTH_MODELS_MODULE.is_integrity_error(e):
                        raise
                    return social_auth_user(backend, uid, user, social_user=social_user,*args,**kwargs)
                else:
                    return {'social_user': social_user, 'user': social_user.user}

    return None

"""
def social_auth_user(backend, uid, user=None, *args, **kwargs):
    social_user = UserSocialAuth.get_social_auth(backend.name, uid)
    if social_user:
        if user and social_user.user != user:
            msg = ugettext('This %(provider)s account is already in use.')
            raise AuthAlreadyAssociated(backend, msg % {
                'provider': backend.name
            })
        elif not user:
            user = None

    return {'social_user': social_user, 'user': user}
"""

def get_user_avatar(backend, details, response, social_user, uid, user, *args, **kwargs):

    url = None
    desc = None

    if backend.__class__ == FacebookBackend:
        desc = response.get('bio','')
        url = "http://graph.facebook.com/%s/picture?type=large" % response['id']
        #url_friendlists = "https://graph.facebook.com/me/friendlists?%s" % urllib.urlencode({'access_token': response['access_token']})

    elif backend.__class__ == TwitterBackend:
        desc = response.get('description','')
        url = response.get('profile_image_url', '').replace('_normal', '')

    prof = None

    try:
        prof = CustomerProfile.objects.get(user__id=user.id)

        if str(prof.picture).strip() == "":
            prof.picture =  url
            prof.save()

        if backend.__class__ == FacebookBackend:
            if prof.picture != url:
                prof.picture = url
                prof.save()

        if str(prof.description).strip() == "":
            prof.description = desc
            prof.save()

    except:
        prof = CustomerProfile()
        prof.user = User.objects.get(id=user.id)
        prof.nickname = user.username
        prof.description = desc
        prof.picture = url
        prof.save()
        user.first_name = details['first_name']
        user.last_name = details['last_name']
        user.save()

    if User.objects.get(id=user.id).password == "!":

        if backend.__class__ == FacebookBackend:
            send_email_set_pass(user.id)