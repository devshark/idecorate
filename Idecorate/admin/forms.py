from django import forms
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import filesizeformat
from django.conf import settings
from django.utils.safestring import mark_safe

class MenuAddForm(forms.Form):
	menu_type = forms.CharField(label=_("Menu Type"), widget=forms.HiddenInput, required=False)
	name = forms.CharField(label=_("Name"), required=True, error_messages={'required':_('Name is a required field.')})
	link = forms.CharField(label=_("Link"), required=False, error_messages={'required':_('Link is a required field.')})

class FooterCopyRightForm(forms.Form):
	copyright = forms.CharField(label=_("Footer Copyright"), required=True, error_messages={'required':_('Footer Copyright is a required field.')})
	task = forms.CharField(label=_("Task"), widget=forms.HiddenInput, required=False)
	menu_type = forms.CharField(label=_("Menu Type"), widget=forms.HiddenInput, required=False)

class AddProductForm(forms.Form):

	product_status = forms.ChoiceField(label=_("Product Status"), choices=(('0','Inactive'),('1','Active'),), required=True,widget=forms.RadioSelect, error_messages={'required':_('Product Status is a required field.')})
	product_sku = forms.CharField(label=_("Product SKU"), required=True, help_text=_(mark_safe('Supply a unique identifier for this product using letters, numbers, hyphens, and underscores. <br />Commas may not be used.')), error_messages={'required':_('Product SKU is a required field.')})
	product_name = forms.CharField(label=_("Product Name"), required=True, help_text=_('Enter the name of this product to be displayed on the product lists on the Front-end and CMS. It is recommended you keep the name short. Max 60 chars.'), error_messages={'required':_('Product Name is a required field.')})
	price = forms.DecimalField(label=_("Price"), max_digits=19, decimal_places=4, required=True, help_text=_('Enter product price per unit using numbers, commas, and periods. Up to 2 decimal points will be accepted. Decimals will automatically added to whole numbers upon saving the product.'), error_messages={'required':_('Price is a required field.')})
	product_description = forms.CharField(label=_("Product Description"), required=True,widget=forms.Textarea, help_text=_('Enter the product description to be displayed on the product information window on the front-end. Web page addresses and e-mail addresses turn into links automatically. Max 500 characters.'), error_messages={'required':_('Product Description is a required field.')})

class ProductImageForm(forms.Form):

	image = forms.FileField(label=_("Image"), required=False)

	def clean_image(self):
	    content = self.cleaned_data['image']
	    if content:
	    	content_type = content.content_type.split('/')[0]
	    	if content_type in settings.CONTENT_TYPES:
	    		if int(content._size) > int(settings.MAX_UPLOAD_PRODUCT_IMAGE_SIZE):
	    			raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(settings.MAX_UPLOAD_PRODUCT_IMAGE_SIZE), filesizeformat(content._size)))
	    	else:
	    		raise forms.ValidationError(_('File type is not supported'))

	    return content
