from django import forms
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import filesizeformat
from django.conf import settings

class LoginForm(forms.Form):	
	username = forms.EmailField(label=_("Enter Email"), error_messages={'required':_('Enter a valid email.')})
	password = forms.CharField( label=_("Enter Password"), widget=forms.PasswordInput, error_messages={'required':_('Enter a valid Password.')})