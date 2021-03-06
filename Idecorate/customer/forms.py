from django import forms
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import filesizeformat
from django.conf import settings
from django.utils.datastructures import MultiValueDictKeyError
from services import is_registered
from common.models import Countries

class LoginForm(forms.Form):	
	username = forms.EmailField(label=_("Email"), error_messages={'required':_('Username field is required.')})
	password = forms.CharField( label=_("Password"), widget=forms.PasswordInput, error_messages={'required':_('Password field is required.')})

class SignupForm(forms.Form):
	firstname = forms.CharField(max_length=100, label=_("First Name"), required=True, error_messages={'required':_('First name field is required.')})
	lastname = forms.CharField(max_length=100, label=_("Last Name"), required=True, error_messages={'required':_('Last name field is required.')})
	#nickname = forms.CharField( label=_("Nickname"), error_messages={'required':_('your nickname.')})
	username = forms.EmailField(label=_("Email"), error_messages={'required':_('a valid e-mail address.')})
	password = forms.CharField( label=_("Password"), widget=forms.PasswordInput, error_messages={'required':_('Password field is required..')})
	confirm_password = forms.CharField( label=_("Confirm Pass"), widget=forms.PasswordInput, error_messages={'required':_('Confirm password field is required.')})

	"""
	def clean_nickname(self):
		try:
			nickname = self.cleaned_data['nickname']
			if len(nickname)>80:
				raise forms.ValidationError(_("Nickname entered should be maximum of 80 chars."))
			return nickname
		except MultiValueDictKeyError as e:
			return ""
	"""

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
				raise forms.ValidationError(_("E-mail address already taken."))
			if len(username)>80:
				raise forms.ValidationError(_("E-mail address entered should be maximum of 80 chars."))
			return username
		except MultiValueDictKeyError as e:
			return ""

	def clean_confirm_password(self):
		try:
			password = self.data['password']
			confirm_password = self.cleaned_data['confirm_password']            
			if password:
				if password != confirm_password:
					raise forms.ValidationError(_("Confirm password not match to password."))
			return confirm_password
		except MultiValueDictKeyError as e:
			return ""

class SaveStyleboardForm(forms.Form):
	name 		= forms.CharField( label=_("Name your style board."), error_messages={'required':_('Enter styleboard name.')})
	description = forms.CharField( label=_("Name your style board."), widget=forms.Textarea, error_messages={'required':_('Enter a short description of your styleboard.')})
	browser 	= forms.CharField(widget=forms.HiddenInput())
	item 		= forms.CharField(widget=forms.HiddenInput())
	guest 		= forms.CharField(widget=forms.HiddenInput())
	tables 		= forms.CharField(widget=forms.HiddenInput())
	wedding 	= forms.CharField(widget=forms.HiddenInput(), initial=1, required=False)

class EditProfileForm(forms.Form):
	firstname = forms.CharField(max_length=100, label=_("First Name"), required=True, error_messages={'required':_('First Name is a required field.')})
	lastname = forms.CharField(max_length=100, label=_("Last Name"), required=True, error_messages={'required':_('Last Name is a required field.')})
	username = forms.EmailField(label=_("Enter Email"), error_messages={'required':_('Enter a valid e-mail address.')})
	
	salutation = forms.ChoiceField(label=_("Salutation"), choices=(('Mr','Mr'), ('Ms','Ms'), ('Mrs','Mrs')), required=False,widget=forms.Select, error_messages={'required':_('Salutation is a required field.')})
	user_image = forms.CharField(label=_("Image"), widget=forms.HiddenInput, required=False)
	about = forms.CharField(label=_("About"), widget=forms.Textarea(attrs={'rows':4, 'cols':15}), required=False, error_messages={'required':_('About is a required field.')})
	gender = forms.ChoiceField(label=_("Gender"), choices=(('Male','Male'),('Female','Female'),), required=False,widget=forms.RadioSelect, error_messages={'required':_('Gender is a required field.')})
	language = forms.ChoiceField(label=_("Language"), choices=(('English','English'),), required=False,widget=forms.Select, error_messages={'required':_('Language is a required field.')})

	def __init__(self, *args, **kwargs):

		country_choices = [('','--Select--')]
		c = Countries.objects.filter()

		for cc in c:
			country_choices.append((cc.name,cc.name))

		country_choices = tuple(country_choices)

		self.this_user = kwargs.pop('this_user')
		self.request = kwargs.pop('request')

		super(EditProfileForm, self).__init__(*args,**kwargs)

		self.fields['shipping_address2'] = forms.CharField(max_length=200, label=_("Shipping Address2"), required=False)
		self.fields['shipping_address'] = forms.CharField(max_length=200, label=_("Shipping Address"), required=False, error_messages={'required':_('Delivery Address is a required field.')})
		self.fields['shipping_state'] = forms.CharField(max_length=150,label=_("Shipping State"),required=False, error_messages={'required':_('Shipping State is a required field.')})
		self.fields['shipping_city'] = forms.CharField(max_length=150,label=_("ChoiceFielding City"), required=False, error_messages={'required':_('Shipping City is a required field.')})
		self.fields['shipping_same_as_billing'] = forms.BooleanField(initial=True,label=_("Same as Billing"),required=False)
		self.fields['shipping_zip_code'] = forms.CharField(label=_("Shipping Zip Code"), required=False, error_messages={'required':_('Delivery Zip Code is a required field.')})        
		self.fields['shipping_country'] = forms.ChoiceField(choices=country_choices,label=_("Shipping Country"), required=False, error_messages={'required':_('Shipping Country is a required field.')})

		if self.request.method == "POST":
			shipping_same_as_billing = self.request.POST.get('shipping_same_as_billing')
		else:
			shipping_same_as_billing = self.initial['shipping_same_as_billing']

		if shipping_same_as_billing:
			self.fields['billing_zip_code'] = forms.CharField(label=_("Billing Zip Code"), required=False, error_messages={'required':_('Billing Zip Code is a required field.')})
			self.fields['billing_address'] = forms.CharField(max_length=200, label=_("Billing Address"), required=False, error_messages={'required':_('Billing Address is a required field.')})
			self.fields['billing_address2'] = forms.CharField(max_length=200, label=_("Billing Address2"), required=False)
			self.fields['billing_state'] = forms.CharField(max_length=150,label=_("Billing State"), required=False)
			self.fields['billing_city'] = forms.CharField(max_length=150,label=_("Billing City"), required=False)
			self.fields['billing_country'] = forms.ChoiceField(choices=country_choices,label=_("Billing Country"), required=False, error_messages={'required':_('Billing Country is a required field.')})
		else:
			self.fields['billing_zip_code'] = forms.CharField(label=_("Billing Zip Code"), required=False, error_messages={'required':_('Billing Zip Code is a required field.')})
			self.fields['billing_address'] = forms.CharField(max_length=200, label=_("Billing Address"), required=False, error_messages={'required':_('Billing Address is a required field.')})
			self.fields['billing_address2'] = forms.CharField(max_length=200, label=_("Billing Address2"), required=False)
			self.fields['billing_state'] = forms.CharField(max_length=150,label=_("Billing State"), required=False, error_messages={'required':_('Billing State is a required field.')})
			self.fields['billing_city'] = forms.CharField(max_length=150,label=_("Billing City"), required=False, error_messages={'required':_('Billing City is a required field.')})
			self.fields['billing_country'] = forms.ChoiceField(choices=country_choices,label=_("Billing Country"), required=False, error_messages={'required':_('Billing Country is a required field.')})

	def clean_username(self):
		try:
			username = self.cleaned_data['username']

			if username != self.this_user.username and username != self.this_user.email:
				if is_registered(username):
					raise forms.ValidationError(_("E-mail address already taken."))
			if len(username)>80:
				raise forms.ValidationError(_("E-mail address entered should be maximum of 80 chars."))
			return username
		except MultiValueDictKeyError as e:
			return ""

class PassForm(forms.Form):
	current_password = forms.CharField( label=_("Current Password"), widget=forms.PasswordInput, error_messages={'required':_('Enter your current password.')})
	password = forms.CharField( label=_("Enter Password"), widget=forms.PasswordInput, error_messages={'required':_('Enter a valid password.')})
	confirm_password = forms.CharField( label=_("Enter Password Again"), widget=forms.PasswordInput, error_messages={'required':_('Re-enter password.')})

	def __init__(self, *args, **kwargs):
		self.this_user = kwargs.pop('this_user')

		super(PassForm, self).__init__(*args,**kwargs)
		
		if self.this_user.password == "!":
			self.fields['current_password'] = forms.CharField(required=False,label=_("Current Password"), widget=forms.PasswordInput)

	def clean_current_password(self):
		current_password = self.cleaned_data['current_password']
		if self.this_user.password != "!":
			if not self.this_user.check_password(current_password):
				raise forms.ValidationError(_('Current password did not match.'))

		return current_password

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

	def clean_confirm_password(self):
		try:
			password = self.data['password']
			confirm_password = self.cleaned_data['confirm_password']            
			if password:
				if password != confirm_password:
					raise forms.ValidationError(_("Confirm password did not match."))
			return confirm_password
		except MultiValueDictKeyError as e:
			return ""

class ForgotPassForm(forms.Form):
	
	username = forms.EmailField(label=_("Enter Email"), error_messages={'required':_('Enter a valid e-mail address.')})
	
	def clean_username(self):

		username = self.cleaned_data['username']

		if not is_registered(username):

			raise forms.ValidationError(_("E-mail address entered is not associated with www.idecorateweddings.com"))

		if len(username) > 80:

			raise forms.ValidationError(_("E-mail address entered should be maximum of 80 chars."))

		return username