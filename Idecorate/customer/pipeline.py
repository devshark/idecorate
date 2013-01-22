from social_auth.backends.twitter import TwitterBackend
from social_auth.backends.facebook import FacebookBackend
from customer.models import CustomerProfile, CustomerFacebookFriends
from django.contrib.auth.models import User
from common.services import IdecorateEmail
from uuid import uuid4
from django.conf import settings
import urllib2, urllib

def get_user_avatar(backend, details, response, social_user, uid, user, *args, **kwargs):

    url = None
    desc = None

    if backend.__class__ == FacebookBackend:
        desc = response.get('bio','')
        url = "http://graph.facebook.com/%s/picture?type=large" % response['id']
        url_friendlists = "https://graph.facebook.com/me/friendlists?%s" % urllib.urlencode({'access_token': response['access_token']})

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

    if backend.__class__ == FacebookBackend:
        try:
            #try to sync friends list

            fb_u = User.objects.get(id=user.id)

            if CustomerFacebookFriends.objects.filter(user=fb_u).count() == 0:

                connection = urllib2.urlopen(url_friendlists)
                returnString = connection.read()
                connection.close()

                friends_count = 0

                exec("friendlistsid=%s" % returnString)

                for d in friendlistsid['data']:

                    url_friendlists_all = "https://graph.facebook.com/%s/members?%s" % (d['id'], urllib.urlencode({'access_token': response['access_token']}))

                    connection = urllib2.urlopen(url_friendlists_all)
                    returnString = connection.read()
                    connection.close()

                    exec("friends=%s" % returnString)

                    for f in friends['data']:
                        if CustomerFacebookFriends.objects.filter(user=fb_u, friend_id=f['id']).count() == 0:
                            friends_count += 1
                            fb_friends = CustomerFacebookFriends()
                            fb_friends.user = fb_u
                            fb_friends.friend_id = f['id']
                            fb_friends.friend_name = f['name']
                            fb_friends.friend_image = "http://graph.facebook.com/%s/picture?type=small" % f['id']
                            fb_friends.save()

                if friends_count == 0:

                    url_friendlists_all = "https://graph.facebook.com/me/friends?%s" % urllib.urlencode({'access_token': response['access_token']})
                    connection = urllib2.urlopen(url_friendlists_all)
                    returnString = connection.read()
                    connection.close()

                    exec("friends=%s" % returnString)

                    for f in friends['data']:
                        if CustomerFacebookFriends.objects.filter(user=fb_u, friend_id=f['id']).count() == 0:
                            friends_count += 1
                            fb_friends = CustomerFacebookFriends()
                            fb_friends.user = fb_u
                            fb_friends.friend_id = f['id']
                            fb_friends.friend_name = f['name']
                            fb_friends.friend_image = "http://graph.facebook.com/%s/picture?type=small" % f['id']
                            fb_friends.save()


        except Exception as e:
            print "The error is: %s" % e

    if User.objects.get(id=user.id).password == "!":
        u = CustomerProfile.objects.get(user__id=user.id)
        u.hash_set_password = str(uuid4())
        u.save()

        if backend.__class__ == FacebookBackend:

            messageHTML = """
            Welcome to iDecorate Weddings!
            <br /><br />
            If you would like to use this email address to login to iDecorate Weddings, you need to set your password by clicking on this link - http://%s/set_password_user/%s.
            <br /><br />
            Thank you for using iDecorate Weddings!
            <br /><br />
            iDecorate Weddings Team
            """ % (settings.IDECORATE_HOST, u.hash_set_password)

            if not settings.SKIPPING_MODE:
                IdecorateEmail.send_mail(mail_from=settings.IDECORATE_MAIL,mail_to=User.objects.get(id=user.id).email,subject='Welcome To iDecorate Weddings',body=messageHTML,isHTML=True)


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