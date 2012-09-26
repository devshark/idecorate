from django import forms
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import filesizeformat
from django.conf import settings

class CategoryForm(forms.Form):
	id = forms.CharField(widget=forms.HiddenInput, required=False)
	parent = forms.CharField(label=_("Parent"), widget=forms.HiddenInput, required=False)
	name = forms.CharField(label=_("Category Name"), error_messages={'required':_('Category Name is a required field.')})
	thumbnail = forms.FileField(label=_("Thumbnail"), error_messages={'required':_('Image thumbnail is a required field.')})

	def clean_thumbnail(self):
	    content = self.cleaned_data['thumbnail']
	    if content:
		    content_type = content.content_type.split('/')[0]
		    if content_type in settings.CONTENT_TYPES:
		        if int(content._size) > int(settings.MAX_UPLOAD_CATEGORY_IMAGE_SIZE):
		            raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(settings.MAX_UPLOAD_CATEGORY_IMAGE_SIZE), filesizeformat(content._size)))
		    else:
		        raise forms.ValidationError(_('File type is not supported'))
	    return content

class CategoryForm2(CategoryForm):
    
    def __init__(self,*args,**kwargs):
        CategoryForm.__init__(self,*args,**kwargs)
        self.fields['thumbnail'].required = False

class MenuAddForm(forms.Form):
	menu_type = forms.CharField(label=_("Menu Type"), widget=forms.HiddenInput, required=False)
	name = forms.CharField(label=_("Name"), required=True, error_messages={'required':_('Name is a required field.')})
	link = forms.CharField(label=_("Link"), required=False, error_messages={'required':_('Link is a required field.')})

class FooterCopyRightForm(forms.Form):
	copyright = forms.CharField(label=_("Footer Copyright"), required=True, error_messages={'required':_('Footer Copyright is a required field.')})
	task = forms.CharField(label=_("Task"), widget=forms.HiddenInput, required=False)
	menu_type = forms.CharField(label=_("Menu Type"), widget=forms.HiddenInput, required=False)
