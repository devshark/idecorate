from django import forms
from django.utils.translation import ugettext_lazy as _

class CategoryForm(forms.Form):
	parent = forms.CharField(label=_("Parent"), widget=forms.HiddenInput, required=False)
	name = forms.CharField(label=_("Category Name"))
	thumbnail = forms.FileField(label=_("Thumbnail"), required=False)


class MenuAddForm(forms.Form):
	menu_type = forms.CharField(label=_("Menu Type"), widget=forms.HiddenInput, required=False)
	name = forms.CharField(label=_("Name"), required=True, error_messages={'required':_('Name is a required field.')})
	link = forms.CharField(label=_("Link"), required=True, error_messages={'required':_('Link is a required field.')})

