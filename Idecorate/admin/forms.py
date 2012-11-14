from django import forms
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import filesizeformat
from django.conf import settings
from django.utils.safestring import mark_safe
from cart.models import Product
from django.utils.html import strip_tags
import re

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
	product_description = forms.CharField(label=_("Product Description"), required=True,widget=forms.Textarea, help_text=_('Enter the product description to be displayed on the product information window on the front-end. Web page addresses and e-mail addresses turn into links automatically. Max 500 characters.'), error_messages={'required':_('Product Description is a required field.')})
	original_image = forms.CharField(label=_("Original Image"), widget=forms.HiddenInput, required=True, error_messages={'required':_('Original Image is a required field.')})
	no_background = forms.CharField(label=_("No Background Image"), widget=forms.HiddenInput, required=True, error_messages={'required':_('No Background Image is a required field.')})
	categories = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, error_messages={'required':_('Product Category is a required field.')})
	default_quantity = forms.IntegerField(min_value=1,label=_("Default Quantity"),required=False,initial=1,error_messages={'invalid':_('Enter a whole number in Default Quantity field.'),'min_value':_('Ensure that Default Quantity is greater than or equal to %(limit_value)s.')})
	guest_table = forms.ChoiceField(label=_("Guest Table"), choices=(('1','Table'),('2','Guest'),), required=False,widget=forms.Select)

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
	product_description = forms.CharField(label=_("Product Description"), required=True,widget=forms.Textarea, help_text=_('Enter the product description to be displayed on the product information window on the front-end. Web page addresses and e-mail addresses turn into links automatically. Max 500 characters.'), error_messages={'required':_('Product Description is a required field.')})
	original_image = forms.CharField(label=_("Original Image"), widget=forms.HiddenInput, required=True, error_messages={'required':_('Original Image is a required field.')})
	no_background = forms.CharField(label=_("No Background Image"), widget=forms.HiddenInput, required=True, error_messages={'required':_('No Background Image is a required field.')})
	categories = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, error_messages={'required':_('Product Category is a required field.')})
	default_quantity = forms.IntegerField(min_value=1,label=_("Default Quantity"),required=False,initial=1,error_messages={'invalid':_('Enter a whole number in Default Quantity field.'),'min_value':_('Ensure that Default Quantity is greater than or equal to %(limit_value)s.')})
	guest_table = forms.ChoiceField(label=_("Guest Table"), choices=(('1','Table'),('2','Guest'),), required=False,widget=forms.Select)

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
	embellishment_type = forms.ChoiceField(label=_("Type"), choices=(('1','Image'),('2','Texture'),('3','Pattern'),('2','Shape'),), required=True,widget=forms.Select, error_messages={'required':_('Type is a required field.')})