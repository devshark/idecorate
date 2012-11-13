from django import forms
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import filesizeformat
from django.conf import settings
from django.utils.datastructures import MultiValueDictKeyError
from services import is_registered

class LoginForm(forms.Form):	
	username = forms.EmailField(label=_("Enter Email"), error_messages={'required':_('Enter a valid e-mail address.')})
	password = forms.CharField( label=_("Enter Password"), widget=forms.PasswordInput, error_messages={'required':_('Enter a valid Password.')})

class SignupForm(forms.Form):
	nickname = forms.CharField( label=_("Enter Nickname"))
	username = forms.EmailField(label=_("Enter Email"), error_messages={'required':_('Enter a valid e-mail address.')})
	password = forms.CharField( label=_("Enter Password"), widget=forms.PasswordInput, error_messages={'required':_('Enter a valid Password.')})
	confirm_password = forms.CharField( label=_("Enter Password Again"), widget=forms.PasswordInput, error_messages={'required':_('Re-Enter Password.')})

	def clean_nickname(self):
		try:
			nickname = self.cleaned_data['nickname']
			if len(nickname)>80:
				raise forms.ValidationError(_("Nickname entered should be maximum of 80 chars."))
			return nickname
		except MultiValueDictKeyError as e:
			return ""

	def clean_password(self):
		try:
			password = self.cleaned_data['password']
			if len(password)<6:
				raise forms.ValidationError(_("Password entered should be minimum of 6 chars."))
			if len(password)>80:
				raise forms.ValidationError(_("Password entered should be maximum of 80 chars."))
			return password
		except MultiValueDictKeyError as e:
			return ""

	def clean_username(self):
		try:
			username = self.cleaned_data['username']
			if is_registered(username):
				raise forms.ValidationError(_("E-mail already taken."))
			if len(username)>80:
				raise forms.ValidationError(_("E-mail entered should be maximum of 80 chars."))
			return username
		except MultiValueDictKeyError as e:
			return ""

	def clean_confirm_password(self):
		try:
			password = self.data['password']
			confirm_password = self.cleaned_data['confirm_password']            
			if password:
				if password != confirm_password:
					raise forms.ValidationError(_("Confirm Password not match to Password."))
			return confirm_password
		except MultiValueDictKeyError as e:
			return ""
