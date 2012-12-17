from social_auth.middleware import SocialAuthExceptionMiddleware
from django.conf import settings

class IdecorateMiddleware(SocialAuthExceptionMiddleware):
    def raise_exception(self, request, exception):
        return False

    def get_redirect_uri(self, request, exception):
    	return settings.LOGIN_REDIRECT_URL