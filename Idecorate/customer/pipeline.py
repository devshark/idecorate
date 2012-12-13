from social_auth.backends.twitter import TwitterBackend
from social_auth.backends.facebook import FacebookBackend
from customer.models import CustomerProfile
from django.contrib.auth.models import User

def get_user_avatar(backend, details, response, social_user, uid, user, *args, **kwargs):

    url = None

    if backend.__class__ == FacebookBackend:
        url = "http://graph.facebook.com/%s/picture?type=large" % response['id']

    elif backend.__class__ == TwitterBackend:
        url = response.get('profile_image_url', '').replace('_normal', '')


    prof = None

    try:
        prof = CustomerProfile.objects.get(user__id=user.id)

        if prof.picture != url:
            prof.picture =  url
            prof.save()

    except:
        prof = CustomerProfile()
        prof.user = User.objects.get(id=user.id)
        prof.nickname = user.username
        prof.picture = url
        prof.save()

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