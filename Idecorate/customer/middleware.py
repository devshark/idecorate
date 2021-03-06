from social_auth.middleware import SocialAuthExceptionMiddleware
from django.conf import settings
from social_auth.exceptions import AuthAlreadyAssociated, AuthFailed, AuthCanceled, \
AuthUnknownError, AuthTokenError, AuthMissingParameter
from pipeline import AuthEmailTaken
#from django.contrib import messages

class IdecorateMiddleware(SocialAuthExceptionMiddleware):
    def raise_exception(self, request, exception):
        return False

    def get_redirect_uri(self, request, exception):
    	return settings.LOGIN_REDIRECT_URL

    def get_message(self, request, exception):
    	if isinstance(exception, AuthAlreadyAssociated):
    		request.session['fb_auth_error'] = 'That %s account is already associated with another iDecorate user.' % exception.backend.name.capitalize()
    	elif isinstance(exception, AuthEmailTaken):
    		request.session['fb_auth_error'] = 'Sorry, this email already has an iDecorate account.'
    	elif isinstance(exception, AuthFailed):
			pass
			#request.session['fb_auth_error'] = 'Authentication failed for some reason.'
    	elif isinstance(exception, AuthCanceled):
    		pass
    		#request.session['fb_auth_error'] = 'Authentication was canceled by the user.'
    	elif isinstance(exception, AuthUnknownError):
    		pass
    		#request.session['fb_auth_error'] = 'An unknown error stoped the authentication process.'
    	elif isinstance(exception, AuthTokenError):
    		pass
    		#request.session['fb_auth_error'] = 'Unauthorized or access token error, it was invalid, impossible to authenticate or user removed permissions to it.'
    	elif isinstance(exception, AuthMissingParameter):
    		pass
    		#request.session['fb_auth_error'] = 'A needed parameter to continue the process was missing.'

    	return super(IdecorateMiddleware, self).get_message(request, exception)