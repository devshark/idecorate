from social_auth.middleware import SocialAuthExceptionMiddleware
from django.conf import settings
from social_auth.exceptions import AuthAlreadyAssociated
from pipeline import AuthEmailTaken
#from django.contrib import messages

class IdecorateMiddleware(SocialAuthExceptionMiddleware):
    def raise_exception(self, request, exception):
        return False

    def get_redirect_uri(self, request, exception):
    	return settings.LOGIN_REDIRECT_URL

    def get_message(self, request, exception):
    	if isinstance(exception, AuthAlreadyAssociated):
    		request.session['fb_auth_error'] = 'That Facebook account is already associated with another iDecorate user.'
    	elif isinstance(exception, AuthEmailTaken):
    		request.session['fb_auth_error'] = 'Sorry, this email already has an iDecorate account.'

    	return super(IdecorateMiddleware, self).get_message(request, exception)