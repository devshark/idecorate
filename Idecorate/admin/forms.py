from django import forms
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import filesizeformat
from django.conf import settings

class MenuAddForm(forms.Form):
	menu_type = forms.CharField(label=_("Menu Type"), widget=forms.HiddenInput, required=False)
	name = forms.CharField(label=_("Name"), required=True, error_messages={'required':_('Name is a required field.')})
	link = forms.CharField(label=_("Link"), required=False, error_messages={'required':_('Link is a required field.')})

class FooterCopyRightForm(forms.Form):
	copyright = forms.CharField(label=_("Footer Copyright"), required=True, error_messages={'required':_('Footer Copyright is a required field.')})
	task = forms.CharField(label=_("Task"), widget=forms.HiddenInput, required=False)
	menu_type = forms.CharField(label=_("Menu Type"), widget=forms.HiddenInput, required=False)
