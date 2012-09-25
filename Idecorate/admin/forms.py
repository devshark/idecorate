from django import forms
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import filesizeformat
from Idecorate import settings

class CategoryForm(forms.Form):
	id = forms.CharField(widget=forms.HiddenInput, required=False)
	parent = forms.CharField(label=_("Parent"), widget=forms.HiddenInput, required=False)
	name = forms.CharField(label=_("Category Name"))
	thumbnail = forms.FileField(label=_("Thumbnail"))

	def clean_content(self):
	    content = self.cleaned_data['thumbnail']
	    content_type = content.content_type.split('/')[0]
	    if content_type in settings.CONTENT_TYPES:
	        if content._size > settings.MAX_UPLOAD_CATEGORY_IMAGE_SIZE:
	            raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(settings.MAX_UPLOAD_CATEGORY_IMAGE_SIZE), filesizeformat(content._size)))
	    else:
	        raise forms.ValidationError(_('File type is not supported'))
	    return content


class MenuAddForm(forms.Form):
	menu_type = forms.CharField(label=_("Menu Type"), widget=forms.HiddenInput, required=False)
	name = forms.CharField(label=_("Name"), required=True, error_messages={'required':_('Name is a required field.')})
	link = forms.CharField(label=_("Link"), required=True, error_messages={'required':_('Link is a required field.')})

