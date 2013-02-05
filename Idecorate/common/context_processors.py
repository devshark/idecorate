from django.conf import settings

def social_network_settings(request):

	info = {}

	info['TWITTER_CONSUMER_KEY'] = settings.TWITTER_CONSUMER_KEY
	info['TWITTER_CONSUMER_SECRET'] = settings.TWITTER_CONSUMER_SECRET
	info['FACEBOOK_APP_ID'] = settings.FACEBOOK_APP_ID
	info['FACEBOOK_API_SECRET'] = settings.FACEBOOK_API_SECRET

	return info