
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import filesizeformat
from django.conf import settings
from django.utils.safestring import mark_safe
from cart.models import Product
from django.utils.html import strip_tags
import re
from django.contrib.auth.models import User
from django.utils.datastructures import MultiValueDictKeyError
from common.models import Countries

class MenuAddForm(forms.Form):
	menu_type = forms.CharField(label=_("Menu Type"), widget=forms.HiddenInput, required=False)
	name = forms.CharField(label=_("Name"), required=True, error_messages={'required':_('Name is a required field.')})
	link = forms.CharField(label=_("Link"), required=False, error_messages={'required':_('Link is a required field.')})

class FooterCopyRightForm(forms.Form):
	copyright = forms.CharField(label=_("Footer Copyright"), required=True, error_messages={'required':_('Footer Copyright is a required field.')})
	task = forms.CharField(label=_("Task"), widget=forms.HiddenInput, required=False)
	menu_type = forms.CharField(label=_("Menu Type"), widget=forms.HiddenInput, required=False)

class AddProductForm(forms.Form):

	product_status = forms.ChoiceField(label=_("Product Status"), choices=(('1','Active'),('0','Inactive'),), required=True,widget=forms.RadioSelect, error_messages={'required':_('Product Status is a required field.')})
	product_sku = forms.CharField(max_length=100,label=_("Product SKU"), required=True, help_text=_(mark_safe('Supply a unique identifier for this product using letters, numbers, hyphens, and underscores. <br />Commas may not be used.')), error_messages={'required':_('Product SKU is a required field.')})
	product_name = forms.CharField(max_length=100,label=_("Product Name"), required=True, help_text=_('Enter the name of this product to be displayed on the product lists on the Front-end and CMS. It is recommended you keep the name short. Max 60 chars.'), error_messages={'required':_('Product Name is a required field.')})
	price = forms.DecimalField(label=_("Price"), max_digits=19, decimal_places=2, required=True, help_text=_('Enter product price per unit using only numbers and periods. Up to 2 decimal points will be accepted. Decimals will be automatically added to whole numbers upon saving the product.'), error_messages={'max_decimal_places':_('Ensure that there are no more than %s decimal places in Price.'),'required':_('Price is a required field.'),'invalid':_('Price must be a number.')})
	product_description = forms.CharField(label=_("Product Description"), required=False,widget=forms.Textarea, help_text=_('Enter the product description to be displayed on the product information window on the front-end. Web page addresses and e-mail addresses turn into links automatically. Max 500 characters.'), error_messages={'required':_('Product Description is a required field.')})
	original_image = forms.CharField(label=_("Original Image"), widget=forms.HiddenInput, required=True, error_messages={'required':_('Original Image is a required field.')})
	no_background = forms.CharField(label=_("No Background Image"), widget=forms.HiddenInput, required=True, error_messages={'required':_('No Background Image is a required field.')})
	categories = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, error_messages={'required':_('Product Category is a required field.')})
	default_quantity = forms.IntegerField(min_value=1,label=_("Default Quantity"),required=False,initial=1,error_messages={'invalid':_('Enter a whole number in Default Quantity field.'),'min_value':_('Ensure that Default Quantity is greater than or equal to %(limit_value)s.')})
	guest_table = forms.ChoiceField(label=_("Guest Table"), choices=(('3','Wedding'),('1','Table'),('2','Guest'),), required=False,widget=forms.Select) # edited added weding option -ryan -02152013

	comment = forms.CharField(label=_("Comment"), required=False, widget=forms.Textarea)
	size = forms.CharField(label=_("Size"), required=False)
	color = forms.CharField(label=_("Color"), required=False)
	unit_price = forms.DecimalField(label='Unit Price', max_digits=19, decimal_places=2, required=False,error_messages={'max_decimal_places':_('Ensure that there are no more than %s decimal places in Unit Price.'), 'invalid':_('Unit price must be a number.')})
	pieces_carton = forms.IntegerField(label='Pieces/Carton', required=False, max_value=999999, min_value=1, error_messages={'invalid':_('Enter a whole number in Pieces/Carton field.'),'min_value':_('Ensure that Pieces/Carton is greater than or equal to %(limit_value)s.')})
	min_order_qty_carton = forms.IntegerField(label='Minimum Order Quantity/Carton', required=False, max_value=999999, min_value=1, error_messages={'invalid':_('Enter a whole number in Minimum Order Quantity/Carton field.'),'min_value':_('Ensure that Minimum Order Quantity/Carton is greater than or equal to %(limit_value)s.')})

	def clean_product_sku(self):

		sku = self.cleaned_data['product_sku']

		try:
			product = Product.objects.get(sku=sku)
		except Exception as e:
			product = None

		if product:
			raise forms.ValidationError(_("Product SKU must be unique."))

		if not re.search("(^[a-zA-z0-9_-]{1,}$)",sku,re.IGNORECASE):
			raise forms.ValidationError(_("Invalid Product SKU format."))			

		return sku

	def clean_product_description(self):

		description = self.cleaned_data['product_description']

		if len(strip_tags(description)) > 500:
			raise forms.ValidationError(_("Product Description must be no more than 500 characters."))

		return description

	def clean_product_name(self):

		name = self.cleaned_data['product_name']

		if len(name) > 60:
			raise forms.ValidationError(_("Product Name must be no more than 60 characters."))			

		return name

class SearchProductForm(forms.Form):

	categories = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, required=False)
	product_sku = forms.CharField(max_length=100,label=_("SKU"), required=False)
	product_name = forms.CharField(max_length=100,label=_("Product Name"), required=False)
	product_status = forms.ChoiceField(label=_("Status"),widget=forms.Select, required=False, choices=(('any','Any'),('1','Active'),('0','Inactive'),))


class EditProductForm(forms.Form):

	product_status = forms.ChoiceField(label=_("Product Status"), choices=(('1','Active'),('0','Inactive'),), required=True,widget=forms.RadioSelect, error_messages={'required':_('Product Status is a required field.')})
	product_sku = forms.CharField(max_length=100,label=_("Product SKU"), required=True, help_text=_(mark_safe('Supply a unique identifier for this product using letters, numbers, hyphens, and underscores. <br />Commas may not be used.')), error_messages={'required':_('Product SKU is a required field.')})
	product_name = forms.CharField(max_length=100,label=_("Product Name"), required=True, help_text=_('Enter the name of this product to be displayed on the product lists on the Front-end and CMS. It is recommended you keep the name short. Max 60 chars.'), error_messages={'required':_('Product Name is a required field.')})
	price = forms.DecimalField(label=_("Price"), max_digits=19, decimal_places=2, required=True, help_text=_('Enter product price per unit using only numbers and periods. Up to 2 decimal points will be accepted. Decimals will be automatically added to whole numbers upon saving the product.'), error_messages={'max_decimal_places':_('Ensure that there are no more than %s decimal places in Price.'),'required':_('Price is a required field.'),'invalid':_('Price must be a number.')})
	product_description = forms.CharField(label=_("Product Description"), required=False,widget=forms.Textarea, help_text=_('Enter the product description to be displayed on the product information window on the front-end. Web page addresses and e-mail addresses turn into links automatically. Max 500 characters.'), error_messages={'required':_('Product Description is a required field.')})
	original_image = forms.CharField(label=_("Original Image"), widget=forms.HiddenInput, required=True, error_messages={'required':_('Original Image is a required field.')})
	no_background = forms.CharField(label=_("No Background Image"), widget=forms.HiddenInput, required=True, error_messages={'required':_('No Background Image is a required field.')})
	categories = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, error_messages={'required':_('Product Category is a required field.')})
	default_quantity = forms.IntegerField(min_value=1,label=_("Default Quantity"),required=False,initial=1,error_messages={'invalid':_('Enter a whole number in Default Quantity field.'),'min_value':_('Ensure that Default Quantity is greater than or equal to %(limit_value)s.')})
	guest_table = forms.ChoiceField(label=_("Guest Table"), choices=(('3','Wedding'),('1','Table'),('2','Guest'),), required=False,widget=forms.Select)# edited added weding option -ryan -02152013

	comment = forms.CharField(label=_("Comment"), required=False, widget=forms.Textarea)
	size = forms.CharField(label=_("Size"), required=False)
	color = forms.CharField(label=_("Color"), required=False)
	unit_price = forms.DecimalField(label='Unit Price', max_digits=19, decimal_places=2, required=False,error_messages={'max_decimal_places':_('Ensure that there are no more than %s decimal places in Unit Price.'), 'invalid':_('Unit price must be a number.')})
	pieces_carton = forms.IntegerField(label='Pieces/Carton', required=False, max_value=999999, min_value=1, error_messages={'invalid':_('Enter a whole number in Pieces/Carton field.'),'min_value':_('Ensure that Pieces/Carton is greater than or equal to %(limit_value)s.')})
	min_order_qty_carton = forms.IntegerField(label='Minimum Order Quantity/Carton', required=False, max_value=999999, min_value=1, error_messages={'invalid':_('Enter a whole number in Minimum Order Quantity/Carton field.'),'min_value':_('Ensure that Minimum Order Quantity/Carton is greater than or equal to %(limit_value)s.')})

	def __init__(self, *args, **kwargs):
		self.product_id = kwargs.pop('product_id',None)
		super(forms.Form, self).__init__(*args, **kwargs)

	def clean_product_sku(self):

		sku = self.cleaned_data['product_sku']
		current_product = Product.objects.get(id=self.product_id)

		if current_product.sku != sku:

			try:
				product = Product.objects.get(sku=sku)
			except Exception as e:
				product = None

			if product:
				raise forms.ValidationError(_("Product SKU must be unique."))

		if not re.search("(^[a-zA-z0-9_-]{1,}$)",sku,re.IGNORECASE):
			raise forms.ValidationError(_("Invalid Product SKU format."))			

		return sku

	def clean_product_description(self):

		description = self.cleaned_data['product_description']

		if len(strip_tags(description)) > 500:
			raise forms.ValidationError(_("Product Description must be no more than 500 characters."))

		return description

	def clean_product_name(self):

		name = self.cleaned_data['product_name']

		if len(name) > 60:
			raise forms.ValidationError(_("Product Name must be no more than 60 characters."))			

		return name

class EditGuestTableForm(forms.Form):

	guests = forms.IntegerField(min_value=1,label=_("Guests"),required=True,initial=1,error_messages={'invalid':_('Enter a whole number in Guests field.'),'min_value':_('Ensure that Guests is greater than or equal to %(limit_value)s.'), 'required':_('Guests is a required field.')})
	tables = forms.IntegerField(min_value=1,label=_("Tables"),required=True,initial=1,error_messages={'invalid':_('Enter a whole number in Tables field.'),'min_value':_('Ensure that Tables is greater than or equal to %(limit_value)s.'), 'required':_('Tables is a required field.')})

class EditCheckoutPage(forms.Form):

	delivery_text = forms.CharField(label=_("Delivery Help Text"), required=True,widget=forms.Textarea, help_text="", error_messages={'required':_('Delivery Help Text is a required field.')})
	any_question_text = forms.CharField(label=_("Any Question Text"), required=True,widget=forms.Textarea, help_text="", error_messages={'required':_('Any Question Text is a required field.')})
	tc_text = forms.CharField(label=_("T&C Help Text"), required=True,widget=forms.Textarea, help_text="", error_messages={'required':_('T&C Help Text is a required field.')})

class UploadEmbellishmentForm(forms.Form):

	embellishment_status = forms.ChoiceField(label=_("Status"), choices=(('1','Active'),('0','Inactive'),), required=True,widget=forms.RadioSelect, error_messages={'required':_('Status is a required field.')})
	embellishment_description = forms.CharField(max_length=100,label=_("Description"), required=True, help_text=_(mark_safe('Enter a short or long description of this embellishment.')), error_messages={'required':_('Description is a required field.')})
	embellishment_image = forms.CharField(label=_("Image"), widget=forms.HiddenInput, required=True, error_messages={'required':_('Image is a required field.')})	

	def __init__(self, *args, **kwargs):

		emb_types = kwargs.pop('emb_types')
		super(UploadEmbellishmentForm, self).__init__(*args, **kwargs)
		ch = ()

		if emb_types:
			ch = []
			for emb_type in emb_types:
				ch.append((str(emb_type.id),emb_type.title))

			ch = tuple(ch)

			self.fields['embellishment_type'] = forms.ChoiceField(label=_("Type"), choices=ch, required=True,widget=forms.Select, error_messages={'required':_('Type is a required field.')})

		self.fields['embellishment_type'] = forms.ChoiceField(label=_("Type"), choices=ch, required=True,widget=forms.Select, error_messages={'required':_('Type is a required field.')})

class UploadFontForm(forms.Form):

	font_status = forms.ChoiceField(label=_("Status"), choices=(('1','Active'),('0','Inactive'),), required=True,widget=forms.RadioSelect, error_messages={'required':_('Status is a required field.')})
	font_description = forms.CharField(max_length=100,label=_("Description"), required=True, help_text=_(mark_safe('Enter a short or long description of this embellishment.')), error_messages={'required':_('Description is a required field.')})
	font_file = forms.CharField(label=_("Image"), widget=forms.HiddenInput, required=True, error_messages={'required':_('Font is a required field.')})


class SearchEmbellishmentForm(forms.Form):

	embellishment_status = forms.ChoiceField(label=_("Status"),widget=forms.Select, required=False, choices=(('any','Any'),('1','Active'),('0','Inactive'),))
	embellishment_description = forms.CharField(max_length=100,label=_("Description"), required=False)
	embellishment_type = forms.ChoiceField(label=_("Type"), choices=(('any','Any'),('1','Image'),('2','Texture'),('3','Pattern'),('4','Shape'),('5','Border'),), required=False,widget=forms.Select)

	def __init__(self, *args, **kwargs):

		emb_types = kwargs.pop('emb_types')
		super(SearchEmbellishmentForm, self).__init__(*args, **kwargs)

		ch = ()

		if emb_types:
			ch = [('any','Any')]
			for emb_type in emb_types:
				ch.append((str(emb_type.id),emb_type.title))

			ch = tuple(ch)

			self.fields['embellishment_type'] = forms.ChoiceField(label=_("Type"), choices=ch, required=False,widget=forms.Select)

class EditEmbellishmentForm(UploadEmbellishmentForm):
	pass

class SearchFontForm(forms.Form):

	font_status = forms.ChoiceField(label=_("Status"), choices=(('any','Any'),('1','Active'),('0','Inactive'),), required=False,widget=forms.Select)
	font_description = forms.CharField(max_length=100,label=_("Description"), required=False)

class EditFontForm(UploadFontForm):
	pass

class SearchUsersForm(forms.Form):

	nickname = forms.CharField(max_length=100,label=_("Nickname"), required=False)
	email = forms.CharField(max_length=100,label=_("Email"), required=False)
	u_type = forms.ChoiceField(label=_("Type"), choices=(('any','Any'),('1','Admin'),('2','Store Manager'),('0','Member'),), required=False,widget=forms.Select)
	status = forms.ChoiceField(label=_("Status"), choices=(('any','Any'),('1','Active'),('0','Inactive'),), required=False,widget=forms.Select)

class EditUsersForm(forms.Form):

	u_id = forms.CharField(label=_("ID"), widget=forms.HiddenInput, required=True, error_messages={'required':_('User ID is a required field.')})
	#nickname = forms.CharField(max_length=80,label=_("Nickname"), required=True, error_messages={'required':_('Nickname is a required field.')})
	first_name = forms.CharField(max_length=80,label=_("First Name"), required=False)
	last_name = forms.CharField(max_length=80,label=_("Last Name"), required=False)
	password = forms.CharField(max_length=80,label=_("Password"), required=False, widget=forms.PasswordInput)
	confirm_password = forms.CharField(max_length=80,label=_("Confirm Password"), required=False, widget=forms.PasswordInput)
	email = forms.EmailField(max_length=80,label=_("Email"), required=True, error_messages={'invalid':_('Enter a valid Email.'),'required':_('Email is a required field.')})
	u_type = forms.ChoiceField(label=_("Type"), choices=(('1','Admin'),('2','Store Manager'),('0','Member'),), required=True,widget=forms.Select, error_messages={'required':_('Type is a required field.')})
	status = forms.ChoiceField(label=_("Status"), choices=(('1','Active'),('0','Inactive'),), required=True,widget=forms.Select, error_messages={'required':_('Status is a required field.')})

	def __init__(self, *args, **kwargs):
		self.user_id = kwargs.pop('user_id',None)
		super(EditUsersForm, self).__init__(*args, **kwargs)

	def clean_email(self):

		email = self.cleaned_data['email']
		current_user = User.objects.get(id=self.user_id)

		if current_user.username != email:

			try:
				user = User.objects.get(username=email)
			except Exception as e:
				user = None

			if user:
				raise forms.ValidationError(_("Email must be unique."))			

		return email

	def clean_password(self):
		try:
			password = self.cleaned_data['password']

			if password != "":

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
					raise forms.ValidationError(_("Confirm password not match to password."))
			return confirm_password
		except MultiValueDictKeyError as e:
			return ""

class AddUsersForm(forms.Form):
	first_name = forms.CharField(max_length=80,label=_("First Name"), required=False)
	last_name = forms.CharField(max_length=80,label=_("Last Name"), required=False)
	password = forms.CharField(max_length=80,label=_("Password"), required=True, widget=forms.PasswordInput,error_messages={'required':_('Password is a required field.')})
	confirm_password = forms.CharField(max_length=80,label=_("Confirm Password"), required=True, widget=forms.PasswordInput,error_messages={'required':_('Confirm Password is a required field.')})
	email = forms.EmailField(max_length=80,label=_("Email"), required=True, error_messages={'invalid':_('Enter a valid Email.'),'required':_('Email is a required field.')})
	u_type = forms.ChoiceField(label=_("Type"), choices=(('1','Admin'),('2','Store Manager'),('0','Member'),), required=True,widget=forms.Select, error_messages={'required':_('Type is a required field.')})

	def clean_email(self):

		email = self.cleaned_data['email']

		try:
			user = User.objects.get(username=email)
		except Exception as e:
			user = None

		if not user:
			try:
				user = User.objects.get(email=email)
			except:
				user = None

		if user:
			raise forms.ValidationError(_("Email must be unique."))			

		return email

	def clean_password(self):
		try:
			password = self.cleaned_data['password']

			if password != "":

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
					raise forms.ValidationError(_("Confirm password not match to password."))
			return confirm_password
		except MultiValueDictKeyError as e:
			return ""

class HomeBannerForm(forms.Form):
	image_id 	= forms.CharField(widget=forms.HiddenInput, required=False)
	image 		= forms.CharField(widget=forms.HiddenInput, required=True)
	link 		= forms.CharField(required=True)
	name 		= forms.CharField(required=True)
	description = forms.CharField(required=True)

	def __init__(self, *args, **kwargs):		
		self.home_banner_id = kwargs.pop('home_banner_id',None)
		super(forms.Form, self).__init__(*args, **kwargs)

class HomeInfoGraphicForm(forms.Form):
	image = forms.CharField(widget=forms.HiddenInput, error_messages={'required':_('Image is a required field.')})

class ItemMenuForm(forms.Form):
	name = forms.CharField(error_messages={'required':_('Menu Name is a required field.')})
	link = forms.CharField(error_messages={'required':_('Menu Link is a required field.')})

class filterStyleboardForm(forms.Form):

	name 		= forms.CharField(max_length=100,label=_("Styleboard Name"), required=False)
	email 		= forms.CharField(max_length=100,label=_("Email"), required=False)
	date 		= forms.DateField(error_messages={'invalid':_('Please follow the format for date field.')}, input_formats=['%Y-%m-%d'], label=_("Date"), required=False)
	guest 		= forms.IntegerField(error_messages={'invalid':_('Guest field requires whole number.')}, label=_("Guests"), required=False)
	table 		= forms.IntegerField(error_messages={'invalid':_('Table field requires whole number.')}, label=_("Tables"), required=False)
	total 		= forms.DecimalField(error_messages={'invalid':_('Total field requires a number.')}, max_digits=19, decimal_places=2, label=_("Total"), required=False)
	featured 	= forms.ChoiceField(label=_("Featured"), choices=(('any','Any'),('1','Featured'),('0','Not featured'),), required=False,widget=forms.Select)

"""
Payment Method
-----------------
PayPal
Visa
Mastercard
American_Express
"""

class filterOrderForm(forms.Form):
	order_id	= forms.CharField(max_length=100,label=_("Order Id"), required=False)
	created		= forms.DateField(error_messages={'invalid':_('Please follow the format for date field.')}, input_formats=['%Y-%m-%d'], label=_("Date created"), required=False)
	name 		= forms.CharField(max_length=100,label=_("Customer Name"), required=False)
	email 		= forms.CharField(max_length=80,label=_("Email"), required=False, error_messages={'invalid':_('Enter a valid Email.')})
	status 		= forms.ChoiceField(label=_("Status"), choices=(('any','Any'),('5','Failed'),('30','Pending'),('40','Paid'),('45','Payment Received'),('46','Pending Delivery'),('50','Completed')), required=False,widget=forms.Select)

class editOrderForm(forms.Form):

	
	order_id 			= forms.CharField(label=_("ID"), widget=forms.HiddenInput, required=True, error_messages={'required':_('Order ID is a required field.')})
	status 				= forms.ChoiceField(label=_("Status"), choices=(('5','Failed'),('30','Pending'),('40','Paid'),('45','Payment Received'),('46','Pending Delivery'),('50','Completed')), required=False,widget=forms.Select)
	payment_method 		= forms.ChoiceField(label=_("Payment Method"), choices=(('','--Select--'),('PayPal','PayPal'),('Visa','Visa'),('Mastercard','Mastercard'),('American_Express','American Express')), required=False,widget=forms.Select)
	first_name 			= forms.CharField(max_length=100,label=_("First Name"), required=True,error_messages={'required':_('First Name is a required field.')})
	last_name 			= forms.CharField(max_length=100,label=_("Last Name"), required=True,error_messages={'required':_('Last Name is a required field.')})
	email 				= forms.EmailField(max_length=80,label=_("Email"), required=True, error_messages={'invalid':_('Enter a valid Email.'),'required':_('Email is a required field.')})
	delivery_date		= forms.DateField(error_messages={'invalid':_('Please follow the format for date field.')}, input_formats=['%Y-%m-%d'], label=_("Delivery Date"), required=False)
	delivery_address	= forms.CharField(max_length=100,label=_("Delivery Address"), required=True, error_messages={'required':_('Delivery address is a required field.')})
	delivery_address2	= forms.CharField(max_length=100,label=_("Delivery Address2"), required=False, error_messages={'required':_('Delivery address2 is a required field.')})
	delivery_city		= forms.CharField(max_length=100,label=_("Delivery City"), required=True, error_messages={'required':_('Delivery city is a required field.')})
	delivery_state		= forms.CharField(max_length=100,label=_("Delivery State"), required=True, error_messages={'required':_('Delivery state is a required field.')})
	delivery_zip_code	= forms.CharField(max_length=100,label=_("Delivery Zip Code"), required=True, error_messages={'required':_('Delivery zip code is a required field.')})
	delivery_country	= forms.CharField(max_length=100,label=_("Delivery Country"), required=True, error_messages={'required':_('Delivery country is a required field.')})
	billing_address 	= forms.CharField(max_length=100,label=_("Billing Address"), required=True, error_messages={'required':_('Billing address is a required field.')})
	billing_address2 	= forms.CharField(max_length=100,label=_("Billing Address2"), required=False, error_messages={'required':_('Billing address2 is a required field.')})
	billing_city		= forms.CharField(max_length=100,label=_("Billing City"), required=True, error_messages={'required':_('Billing city is a required field.')})
	billing_state		= forms.CharField(max_length=100,label=_("Billing State"), required=True, error_messages={'required':_('Billing state is a required field.')})
	billing_zip_code	= forms.CharField(max_length=100,label=_("Billing Zip Code"), required=True, error_messages={'required':_('Billing zip code is a required field.')})
	billing_country 	= forms.CharField(max_length=100,label=_("Billing Country"), required=True, error_messages={'required':_('Billing country is a required field.')})
	note 				= forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 5}), required=False, label=_("Order Note"))

	def __init__(self, *args, **kwargs):

		super(editOrderForm, self).__init__(*args, **kwargs)
		country_choices = [('','-Select-')]
		c = Countries.objects.filter()
		for cc in c:
			country_choices.append((cc.name,cc.name))

		country_choices = tuple(country_choices)

		self.fields['delivery_country'] = forms.ChoiceField(choices=country_choices,label=_("Delivery Country"), required=True, error_messages={'required':_('Delivery Country is a required field.')})
		self.fields['billing_country'] = forms.ChoiceField(choices=country_choices,label=_("Billing Country"), required=True, error_messages={'required':_('Billing Country is a required field.')})
