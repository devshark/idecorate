from django import forms
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import filesizeformat
from django.conf import settings
from django.utils.datastructures import MultiValueDictKeyError

class SaveTemplateForm(forms.Form):
	name = forms.CharField( label=_("Template Name"), error_messages={'required':_('Enter template name.')})
	description = forms.CharField( label=_("Template Description"), widget=forms.Textarea, error_messages={'required':_('Enter a short description of the template.')})
	browser = forms.CharField(widget=forms.HiddenInput())
	item = forms.CharField(widget=forms.HiddenInput())
