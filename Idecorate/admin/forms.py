from django import forms
from django.utils.translation import ugettext_lazy as _

class CategoryForm(forms.Form):
	parent = forms.CharField(label=_("Parent"), widget=forms.HiddenInput, required=False)
	name = forms.CharField(label=_("Category Name"))
	thumbnail = forms.FileField(label=_("Thumbnail"), required=False)