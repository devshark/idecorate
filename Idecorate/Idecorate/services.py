from django.contrib.sites.models import Site
from django.conf import settings

def get_media_url():	
	site = Site.objects.get_current()
	site.domain
	url = '%s%s' % (site.domain, settings.MEDIA_URL)
	return url